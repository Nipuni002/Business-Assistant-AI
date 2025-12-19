# AI Chatbot Backend - Setup & Run Guide

## Quick Start

1. **Create environment file**
   ```bash
   copy .env.example .env
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python main.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── schemas.py             # Pydantic models
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── routes/               
│   ├── __init__.py
│   ├── chat_routes.py     # Chat/messaging endpoints
│   ├── document_routes.py # Document upload/management
│   └── admin_routes.py    # Admin authentication & stats
├── services/
│   ├── __init__.py
│   ├── vector_store.py    # ChromaDB vector database
│   ├── document_processor.py  # Document text extraction
│   └── chatbot.py         # RAG chatbot logic
├── uploads/               # Uploaded documents storage
└── chroma_db/             # Vector database storage

```

## API Endpoints

### Chat Endpoints
- `POST /api/chat/message` - Send a message to the chatbot
- `GET /api/chat/history/{session_id}` - Get chat history
- `DELETE /api/chat/session/{session_id}` - Clear chat session

### Document Endpoints
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents/list` - List all documents
- `DELETE /api/documents/delete/{file_id}` - Delete a document
- `POST /api/documents/clear-all` - Clear all documents

### Admin Endpoints
- `POST /api/admin/login` - Admin login
- `GET /api/admin/stats` - Get system statistics
- `GET /api/admin/verify` - Verify admin token

## Configuration

Edit `.env` file to configure:
- Admin credentials (change default!)
- CORS origins for your frontend
- AI model settings
- File upload limits
- API keys (if using external LLM providers)

## Features

✅ RAG (Retrieval Augmented Generation) pipeline
✅ Document upload & processing (PDF, DOCX, TXT, XLSX)
✅ Vector database with ChromaDB
✅ Local LLM support (TinyLlama)
✅ Session-based chat history
✅ Admin authentication with JWT
✅ CORS enabled for frontend integration
✅ Automatic text chunking
✅ Source attribution for responses

## Notes

- First run will download the embedding model (~80MB)
- The default LLM (TinyLlama) runs on CPU
- For better performance, consider using OpenAI API or larger models with GPU
- Change admin credentials before deploying to production!
