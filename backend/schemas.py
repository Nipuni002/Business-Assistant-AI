from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Chat Models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[str]] = []
    timestamp: datetime = Field(default_factory=datetime.now)

# Document Models
class DocumentUploadResponse(BaseModel):
    filename: str
    file_id: str
    size: int
    status: str
    message: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_date: datetime
    size: int
    status: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int

class DocumentDeleteResponse(BaseModel):
    message: str
    deleted_id: str

# Admin Models
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str

class AdminStats(BaseModel):
    total_documents: int
    total_chats: int
    storage_used: str
    last_updated: datetime

# Vector Store Models
class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: dict
    source: str

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    content: str
    metadata: dict
    similarity_score: float
