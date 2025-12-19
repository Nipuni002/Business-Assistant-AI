from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
import os
from pathlib import Path
from pydantic import field_validator, Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )
    # API Settings
    APP_NAME: str = "AI Chatbot API"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings
    cors_origins_str: str = Field(default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000", alias="CORS_ORIGINS")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins_str.split(',')]
    
    # File Upload Settings
    UPLOAD_DIR: Path = Path(__file__).parent / "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions_str: str = Field(default=".pdf,.txt,.docx,.xlsx", alias="ALLOWED_EXTENSIONS")
    
    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions_str.split(',')]
    
    # ChromaDB Settings
    CHROMA_DB_DIR: Path = Path(__file__).parent / "chroma_db"
    COLLECTION_NAME: str = "business_documents"
    
    # AI Model Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-3.5-turbo"  # Can be changed to local models
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Admin Settings
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # Change in production!
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # API Keys (Load from environment)
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    


# Create settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
