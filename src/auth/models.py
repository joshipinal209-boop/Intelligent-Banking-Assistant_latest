"""
Pydantic models for authentication and user management.
Also includes SQLite schema and database operations.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from auth.utils import get_password_hash, verify_password

# Database setup
DB_PATH = "data/auth/users.db"

# Ensure data/auth directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    """Initialize SQLite database with users table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            token_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_revoked BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            access_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()


# Initialize database on module load
init_db()


# --- Pydantic Models ---

class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Seconds until token expires")


class TokenData(BaseModel):
    """Decoded token data model."""
    user_id: str
    scopes: List[str] = []
    email: Optional[str] = None


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration model."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class User(UserBase):
    """User model for API responses."""
    user_id: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password (for internal use)."""
    hashed_password: str


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change request model."""
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class UserSession(BaseModel):
    """User session model."""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    is_active: bool


# --- Database Operations ---

def create_user(user_create: UserCreate) -> Optional[User]:
    """Create a new user in the database."""
    import uuid
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_create.password)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (user_id, email, username, full_name, hashed_password)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, user_create.email, user_create.username, user_create.full_name, hashed_password))
        
        conn.commit()
        conn.close()
        
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by user_id."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(**dict(row))
    return None


def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Get user by username (including hashed password)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UserInDB(**dict(row))
    return None


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(**dict(row))
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password."""
    user = get_user_by_username(username)
    
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    return user


def update_user(user_id: str, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    update_fields = []
    update_values = []
    
    if user_update.full_name is not None:
        update_fields.append("full_name = ?")
        update_values.append(user_update.full_name)
    
    if user_update.email is not None:
        update_fields.append("email = ?")
        update_values.append(user_update.email)
    
    if user_update.password is not None:
        update_fields.append("hashed_password = ?")
        update_values.append(get_password_hash(user_update.password))
    
    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
        cursor.execute(query, update_values)
        conn.commit()
    
    conn.close()
    return get_user_by_id(user_id)


def update_last_login(user_id: str) -> None:
    """Update user's last login timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
    """, (user_id,))
    
    conn.commit()
    conn.close()


def deactivate_user(user_id: str) -> bool:
    """Deactivate a user account."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
    """, (user_id,))
    
    conn.commit()
    conn.close()
    
    return cursor.rowcount > 0


def list_all_users(skip: int = 0, limit: int = 100) -> List[User]:
    """List all users with pagination."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, username, full_name, is_active, is_admin, created_at, updated_at, last_login
        FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?
    """, (limit, skip))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [User(**dict(row)) for row in rows]
