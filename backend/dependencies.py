"""
Dependency injection for FastAPI routes.

Provides:
- get_db: Database session dependency
- get_current_user: Current authenticated user dependency
- get_current_active_user: Current active user dependency
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
import logging

from config import settings
from database import get_db
from shared.exceptions import UnauthorizedException, ForbiddenException

logger = logging.getLogger(__name__)

# Security scheme for JWT token extraction
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        dict: User information from JWT payload
        
    Raises:
        UnauthorizedException: If token is invalid or expired
    """
    from jose import JWTError, jwt
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Invalid token: missing subject")
        
        # Return user info from token
        return {
            "user_id": user_id,
            "phone": payload.get("phone"),
            "exp": payload.get("exp"),
        }
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise UnauthorizedException("Invalid or expired token")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise UnauthorizedException("Authentication failed")


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependency to get current active user.
    Extends get_current_user with additional checks.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        dict: Active user information
        
    Raises:
        ForbiddenException: If user is inactive or disabled
    """
    # TODO: Add user status check when User model is implemented
    # if not current_user.get("is_active", True):
    #     raise ForbiddenException("User account is disabled")
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[dict]:
    """
    Dependency to optionally get current user.
    Returns None if no token or invalid token (doesn't raise exception).
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Optional[dict]: User information or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None
