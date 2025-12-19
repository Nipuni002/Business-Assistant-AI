import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        """Initialize the vector store with ChromaDB and embeddings."""
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        self.chroma_client = chromadb.PersistentClient(
            path=str(settings.CHROMA_DB_DIR)
        )
        
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=settings.COLLECTION_NAME,
            embedding_function=self.embedding_model
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        
        logger.info("Vector store initialized successfully")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries for each document
            
        Returns:
            List of document IDs
        """
        try:
            # Split texts into chunks
            chunks = []
            chunk_metadatas = []
            
            for text, metadata in zip(texts, metadatas):
                text_chunks = self.text_splitter.split_text(text)
                chunks.extend(text_chunks)
                
                # Add chunk index to metadata
                for i, _ in enumerate(text_chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = i
                    chunk_metadatas.append(chunk_metadata)
            
            # Add to vector store
            ids = self.vectorstore.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of documents with scores
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise
    
    def delete_documents(self, file_id: str) -> bool:
        """
        Delete all chunks associated with a file.
        
        Args:
            file_id: The file ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Get collection
            collection = self.chroma_client.get_collection(settings.COLLECTION_NAME)
            
            # Query for documents with this file_id
            results = collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for file {file_id}")
                return True
            
            logger.warning(f"No chunks found for file {file_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents in the vector store."""
        try:
            collection = self.chroma_client.get_collection(settings.COLLECTION_NAME)
            results = collection.get()
            
            documents = []
            for i, doc_id in enumerate(results['ids']):
                documents.append({
                    'id': doc_id,
                    'content': results['documents'][i] if results['documents'] else '',
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.chroma_client.delete_collection(settings.COLLECTION_NAME)
            self.chroma_client.create_collection(settings.COLLECTION_NAME)
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

# Global instance
vector_store_service = VectorStoreService()
