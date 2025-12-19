from fastapi import APIRouter, HTTPException
from schemas import ChatMessage, ChatResponse
from services.chatbot import chatbot_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """
    Send a message to the chatbot and get a response.
    
    Args:
        chat_message: ChatMessage with message and optional session_id
        
    Returns:
        ChatResponse with answer, session_id, and sources
    """
    try:
        result = await chatbot_service.chat(
            message=chat_message.message,
            session_id=chat_message.session_id
        )
        
        return ChatResponse(
            response=result['response'],
            session_id=result['session_id'],
            sources=result.get('sources', [])
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat message")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history for a session.
    
    Args:
        session_id: The session ID
        
    Returns:
        List of messages in the session
    """
    try:
        history = chatbot_service.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chat history")

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a chat session.
    
    Args:
        session_id: The session ID to clear
        
    Returns:
        Success message
    """
    try:
        success = chatbot_service.clear_session(session_id)
        
        if success:
            return {"message": "Session cleared successfully", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail="Error clearing session")
