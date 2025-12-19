from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from schemas import DocumentUploadResponse, DocumentListResponse, DocumentInfo, DocumentDeleteResponse
from services.document_processor import document_processor
from services.vector_store import vector_store_service
from config import settings
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document and add it to the vector store.
    
    Args:
        file: The file to upload
        
    Returns:
        DocumentUploadResponse with file details
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Save file
        file_id, file_path = await document_processor.save_upload_file(file, file.filename)
        
        # Extract text
        text = document_processor.extract_text(file_path)
        
        if not text or len(text.strip()) < 10:
            # Delete the file if no text extracted
            await document_processor.delete_file(file_id)
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the document or document is empty"
            )
        
        # Get metadata
        metadata = document_processor.get_file_metadata(file_path, file.filename, file_id)
        
        # Add to vector store
        vector_store_service.add_documents([text], [metadata])
        
        logger.info(f"Document uploaded successfully: {file.filename}")
        
        return DocumentUploadResponse(
            filename=file.filename,
            file_id=file_id,
            size=file_path.stat().st_size,
            status="success",
            message="Document uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """
    Get list of all uploaded documents.
    
    Returns:
        DocumentListResponse with list of documents
    """
    try:
        documents = []
        seen_files = set()
        
        # Get documents from vector store
        vector_docs = vector_store_service.get_all_documents()
        
        for doc in vector_docs:
            file_id = doc['metadata'].get('file_id')
            if file_id and file_id not in seen_files:
                seen_files.add(file_id)
                
                # Find file on disk
                file_path = None
                for path in settings.UPLOAD_DIR.glob(f"{file_id}.*"):
                    file_path = path
                    break
                
                if file_path:
                    documents.append(DocumentInfo(
                        id=file_id,
                        filename=doc['metadata'].get('filename', 'Unknown'),
                        upload_date=datetime.fromtimestamp(file_path.stat().st_ctime),
                        size=file_path.stat().st_size,
                        status="active"
                    ))
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving documents")

@router.delete("/delete/{file_id}", response_model=DocumentDeleteResponse)
async def delete_document(file_id: str):
    """
    Delete a document from the vector store and disk.
    
    Args:
        file_id: The ID of the file to delete
        
    Returns:
        DocumentDeleteResponse with success message
    """
    try:
        # Delete from vector store
        vector_deleted = vector_store_service.delete_documents(file_id)
        
        # Delete from disk
        file_deleted = await document_processor.delete_file(file_id)
        
        if vector_deleted or file_deleted:
            return DocumentDeleteResponse(
                message="Document deleted successfully",
                deleted_id=file_id
            )
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Error deleting document")

@router.post("/clear-all")
async def clear_all_documents():
    """
    Clear all documents from the system.
    WARNING: This will delete all documents and vector store data.
    
    Returns:
        Success message
    """
    try:
        # Clear vector store
        vector_store_service.clear_collection()
        
        # Delete all files
        deleted_count = 0
        for file_path in settings.UPLOAD_DIR.glob("*"):
            if file_path.is_file() and file_path.name != ".gitkeep":
                file_path.unlink()
                deleted_count += 1
        
        return {
            "message": "All documents cleared successfully",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing all documents: {e}")
        raise HTTPException(status_code=500, detail="Error clearing documents")
