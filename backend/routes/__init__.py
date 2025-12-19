# Routes package
from .chat_routes import router as chat_router
from .document_routes import router as document_router
from .admin_routes import router as admin_router

__all__ = [
    'chat_router',
    'document_router',
    'admin_router'
]
