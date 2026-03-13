"""
FastAPI dependencies for JWT authentication and OAuth2 flows.
Provides decorators and dependency functions for securing endpoints.
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.utils import verify_access_token, get_token_scopes, TokenData as TokenDataUtil
from auth.models import User, get_user_by_id

# OAuth2 scheme - tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={
        "read": "Read access to customer data",
        "write": "Write access to banking operations",
        "admin": "Admin access to system configuration",
        "audit": "Access to audit logs",
    }
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_access_token(token)
    
    if payload is None:
        raise credential_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credential_exception
    
    user = get_user_by_id(user_id)
    if user is None:
        raise credential_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure current user is an admin.
    
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required."
        )
    return current_user


def require_scopes(required_scopes: List[str]):
    """
    Factory function to create a dependency that checks for required OAuth2 scopes.
    
    Args:
        required_scopes: List of required scopes
    
    Returns:
        Dependency function that validates scopes
    
    Example:
        @app.get("/admin")
        async def admin_endpoint(current_user: User = Depends(require_scopes(["admin"]))):
            return {"message": "Admin only"}
    """
    async def check_scopes(token: str = Depends(oauth2_scheme)) -> User:
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = verify_access_token(token)
        if payload is None:
            raise credential_exception
        
        token_scopes = payload.get("scopes", [])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credential_exception
        
        # Check if user has required scopes (admin bypasses scope checks)
        if "admin" not in token_scopes:
            for scope in required_scopes:
                if scope not in token_scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not enough permissions. Required scope: {scope}",
                    )
        
        user = get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise credential_exception
        
        return user
    
    return check_scopes


async def get_current_user_scopes(token: str = Depends(oauth2_scheme)) -> List[str]:
    """
    Dependency to get the current user's scopes from their token.
    
    Returns:
        List of scopes the user has
    """
    payload = verify_access_token(token)
    if payload:
        return payload.get("scopes", [])
    return []


async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Dependency to optionally get the current user.
    Does not raise an exception if no token is provided.
    
    Returns:
        User object if authenticated, None otherwise
    """
    if not token:
        return None
    
    payload = verify_access_token(token)
    if payload is None:
        return None
    
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
    
    user = get_user_by_id(user_id)
    return user if user and user.is_active else None


class RoleChecker:
    """
    Class-based dependency for checking user roles.
    
    Example:
        admin_checker = RoleChecker(required_roles=["admin"])
        
        @app.get("/admin")
        async def admin_endpoint(admin: User = Depends(admin_checker)):
            return {"message": "Admin only"}
    """
    
    def __init__(self, required_roles: List[str] = None):
        self.required_roles = required_roles or []
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if self.required_roles:
            has_role = False
            for role in self.required_roles:
                if role == "admin" and current_user.is_admin:
                    has_role = True
                    break
            
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        return current_user


def create_bearer_token_header(token: str) -> dict:
    """
    Create proper Authorization header for Bearer token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}
