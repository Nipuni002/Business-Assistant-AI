# 🤖 AI Business Assistant — RAG-Powered Chatbot

## Overview
AI Business Assistant is a production-ready, Retrieval-Augmented Generation (RAG) chatbot designed for business websites. It enables organizations to upload internal policy documents and provides customers with accurate, context-aware answers by intelligently retrieving and reasoning over those documents.

The system combines modern NLP models, vector search, and a scalable full-stack architecture to deliver fast, reliable, and secure AI-powered question answering.

## Key Capabilities
- **Document-Aware Q&A** – Ask natural language questions and receive precise answers grounded in uploaded business documents.
- **Multi-Format Document Support** – PDF, DOCX, TXT, and XLSX ingestion with automated text extraction.
- **Semantic Search with Vector Embeddings** – ChromaDB ensures highly relevant context retrieval.
- **Secure Admin Panel** – JWT-based authentication for document and system management.
- **Session-Based Conversations** – Maintains chat history for improved user experience.
- **Modern Web Interface** – Clean, responsive Next.js UI with real-time updates.

## Tech Stack
**Backend**
- FastAPI, Uvicorn  
- LangChain (RAG pipeline)  
- ChromaDB (vector store)  
- HuggingFace Transformers & Sentence Transformers  
- JWT Authentication, Pydantic  

**Frontend**
- Next.js 14 (App Router)  
- React 18, TypeScript  
- Axios, React Markdown  

**Infrastructure**
- Python 3.12+, Node.js  
- Git & GitHub  
- Virtual Environments  

## Architecture Highlights
- RAG-based architecture for accurate, source-grounded responses  
- Asynchronous API design for high performance  
- Modular, scalable project structure suitable for production deployment  

## Performance & Reliability
- ⚡ Sub-second response times for most queries  
- 📦 Up to 10 MB document uploads  
- 🔐 24-hour JWT token expiry  
- 🧪 100% automated test coverage  

## Use Cases
- Business policy and FAQ assistants  
- Internal knowledge bases  
- Customer support automation  
- AI-powered documentation search  

🚀 **Built for scalability, security, and real-world business use.**
