from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas import AdminLogin, AdminLoginResponse, AdminStats
from config import settings
from datetime import datetime, timedelta
import jwt
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Simple JWT authentication
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(credentials: AdminLogin):
    """
    Admin login endpoint.
    
    Args:
        credentials: AdminLogin with username and password
        
    Returns:
        AdminLoginResponse with access token
    """
    try:
        # Verify credentials (in production, use proper password hashing)
        if (credentials.username != settings.ADMIN_USERNAME or 
            credentials.password != settings.ADMIN_PASSWORD):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": credentials.username})
        
        return AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin login: {e}")
        raise HTTPException(status_code=500, detail="Login error")

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(username: str = Depends(verify_token)):
    """
    Get admin statistics.
    
    Args:
        username: Verified admin username from token
        
    Returns:
        AdminStats with system statistics
    """
    try:
        # Count documents
        total_documents = sum(1 for _ in settings.UPLOAD_DIR.glob("*") if _.is_file())
        
        # Calculate storage used
        storage_bytes = sum(f.stat().st_size for f in settings.UPLOAD_DIR.glob("*") if f.is_file())
        storage_mb = storage_bytes / (1024 * 1024)
        storage_used = f"{storage_mb:.2f} MB"
        
        # Get total chats (this would come from database in production)
        total_chats = 0  # Placeholder
        
        return AdminStats(
            total_documents=total_documents,
            total_chats=total_chats,
            storage_used=storage_used,
            last_updated=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

@router.get("/verify")
async def verify_admin_token(username: str = Depends(verify_token)):
    """
    Verify admin token validity.
    
    Args:
        username: Verified admin username from token
        
    Returns:
        Verification status
    """
    return {
        "valid": True,
        "username": username,
        "message": "Token is valid"
    }

@router.post("/change-password")
async def change_admin_password(
    old_password: str,
    new_password: str,
    username: str = Depends(verify_token)
):
    """
    Change admin password.
    NOTE: This is a simple implementation. In production, use proper password management.
    
    Args:
        old_password: Current password
        new_password: New password
        username: Verified admin username
        
    Returns:
        Success message
    """
    try:
        if old_password != settings.ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Incorrect old password")
        
        # In production, you would update the password in a database
        # For now, this is just a placeholder
        return {
            "message": "Password change successful. Note: This is a demo endpoint. Configure proper password management in production."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Error changing password")
