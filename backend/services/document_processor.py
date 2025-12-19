from pathlib import Path
from typing import Optional, Dict
import aiofiles
import uuid
import logging
from pypdf import PdfReader
from docx import Document
import openpyxl
import pandas as pd
from config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing uploaded documents."""
    
    @staticmethod
    async def save_upload_file(file, filename: str) -> tuple[str, Path]:
        """
        Save uploaded file to disk.
        
        Args:
            file: Uploaded file object
            filename: Original filename
            
        Returns:
            Tuple of (file_id, file_path)
        """
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            new_filename = f"{file_id}{file_extension}"
            file_path = settings.UPLOAD_DIR / new_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"File saved: {new_filename}")
            return file_id, file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(str(file_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(str(file_path))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            raise
    
    @staticmethod
    def extract_text_from_excel(file_path: Path) -> str:
        """Extract text from Excel file."""
        try:
            df = pd.read_excel(file_path, sheet_name=None)
            text = ""
            for sheet_name, sheet_df in df.items():
                text += f"\n\n=== Sheet: {sheet_name} ===\n"
                text += sheet_df.to_string(index=False)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting Excel text: {e}")
            raise
    
    @staticmethod
    def extract_text(file_path: Path) -> str:
        """
        Extract text from file based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return DocumentProcessor.extract_text_from_docx(file_path)
        elif extension == '.txt':
            return DocumentProcessor.extract_text_from_txt(file_path)
        elif extension in ['.xlsx', '.xls']:
            return DocumentProcessor.extract_text_from_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    @staticmethod
    def get_file_metadata(file_path: Path, filename: str, file_id: str) -> Dict:
        """
        Get metadata for a file.
        
        Args:
            file_path: Path to the file
            filename: Original filename
            file_id: Unique file identifier
            
        Returns:
            Dictionary of metadata
        """
        return {
            'file_id': file_id,
            'filename': filename,
            'file_type': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size,
            'source': str(file_path)
        }
    
    @staticmethod
    async def delete_file(file_id: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            file_id: The file ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Find file with this ID
            for file_path in settings.UPLOAD_DIR.glob(f"{file_id}.*"):
                file_path.unlink()
                logger.info(f"Deleted file: {file_path.name}")
                return True
            
            logger.warning(f"File not found: {file_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise

# Global instance
document_processor = DocumentProcessor()
