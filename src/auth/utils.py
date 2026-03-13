"""
Authentication utilities for JWT token generation and verification.
Supports both JWT and OAuth2 flows.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-min-32-chars-long!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scopes
SCOPES = {
    "read": "Read access to customer data",
    "write": "Write access to banking operations",
    "admin": "Admin access to system configuration",
    "audit": "Access to audit logs",
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[list] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with token claims (typically {"sub": user_id})
        expires_delta: Optional custom expiration time
        scopes: List of OAuth2 scopes for this token
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "scopes": scopes or []
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary with token claims
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary with token claims if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify that token is an access token."""
    payload = verify_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify that token is a refresh token."""
    payload = verify_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


def get_token_subject(token: str) -> Optional[str]:
    """Extract the subject (user_id) from a token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def get_token_scopes(token: str) -> list:
    """Extract the scopes from an access token."""
    payload = verify_access_token(token)
    if payload:
        return payload.get("scopes", [])
    return []


def is_token_expired(token: str) -> bool:
    """Check if a token is expired."""
    payload = verify_token(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    return datetime.fromtimestamp(exp, tz=timezone.utc) <= datetime.now(timezone.utc)


def validate_scopes(required_scopes: list, token_scopes: list) -> bool:
    """
    Validate that token has required scopes.
    
    Args:
        required_scopes: List of required scopes
        token_scopes: List of scopes in token
    
    Returns:
        True if all required scopes are present
    """
    for scope in required_scopes:
        if scope not in token_scopes and "admin" not in token_scopes:
            return False
    return True


class TokenData:
    """Holds decoded token information."""
    
    def __init__(self, user_id: str, scopes: list = None, email: str = None):
        self.user_id = user_id
        self.scopes = scopes or []
        self.email = email
    
    def has_scope(self, scope: str) -> bool:
        """Check if token has a specific scope."""
        return scope in self.scopes or "admin" in self.scopes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "scopes": self.scopes,
            "email": self.email
        }
