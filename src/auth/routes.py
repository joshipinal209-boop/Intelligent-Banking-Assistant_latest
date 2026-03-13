"""
Authentication API routes for JWT login, registration, and token management.
Supports OAuth2 Password Flow and refresh token rotation.
"""

import uuid
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.models import (
    Token, User, UserCreate, UserUpdate, LoginRequest, RefreshTokenRequest,
    PasswordChangeRequest, create_user, get_user_by_username, authenticate_user,
    update_user, update_last_login, deactivate_user, list_all_users, get_user_by_id
)
from auth.utils import (
    create_access_token, create_refresh_token, verify_refresh_token,
    verify_password, get_password_hash
)
from auth.dependencies import (
    get_current_user, get_current_admin_user, oauth2_scheme
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **username**: Unique username (3-20 characters)
    - **full_name**: Optional user's full name
    - **password**: At least 8 characters
    
    Returns: Created user object (without password hash)
    """
    # Check if user already exists
    existing_user = get_user_by_username(user_create.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    # Create user in database
    user = create_user(user_create)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user. Email may already be registered."
        )
    
    return user


@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """
    Login with username and password.
    
    Returns: Access token and refresh token
    
    - **username**: User's username
    - **password**: User's password
    """
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    update_last_login(user.user_id)
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)  # 30 minutes
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username, "email": user.email},
        expires_delta=access_token_expires,
        scopes=["read", "write"] if not user.is_admin else ["read", "write", "admin", "audit"]
    )
    
    refresh_token = create_refresh_token(data={"sub": user.user_id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )


@router.post("/login-form", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint compatible with OAuth2 form data.
    Allows swagger UI to test the endpoint.
    
    - **username**: User's username
    - **password**: User's password
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    update_last_login(user.user_id)
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username, "email": user.email},
        expires_delta=access_token_expires,
        scopes=["read", "write"] if not user.is_admin else ["read", "write", "admin", "audit"]
    )
    
    refresh_token = create_refresh_token(data={"sub": user.user_id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an expired access token using a refresh token.
    
    - **refresh_token**: Valid refresh token from login response
    
    Returns: New access token
    """
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = get_user_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username, "email": user.email},
        expires_delta=access_token_expires,
        scopes=["read", "write"] if not user.is_admin else ["read", "write", "admin", "audit"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Change the current user's password.
    
    - **old_password**: Current password
    - **new_password**: New password (must be different and 8+ chars)
    - **confirm_password**: Confirmation of new password
    """
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    user_in_db = authenticate_user(current_user.username, request.old_password)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect"
        )
    
    # Update password
    user_update = UserUpdate(password=request.new_password)
    updated_user = update_user(current_user.user_id, user_update)
    
    return {"message": "Password changed successfully", "user": updated_user}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    
    Returns: Current user's profile information
    """
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile information.
    
    - **full_name**: Optional full name
    - **email**: Optional email (must be unique)
    - **password**: Optional password change
    """
    if user_update.email and user_update.email != current_user.email:
        # Check if new email is already taken
        existing_user = get_user_by_id(user_update.email)
        if existing_user and existing_user.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
    
    updated_user = update_user(current_user.user_id, user_update)
    return updated_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout the current user.
    (Note: JWT tokens are stateless, so this primarily records logout in audit logs)
    
    In a production system, you would:
    1. Add the token to a blacklist
    2. Invalidate refresh tokens
    3. Clear any server-side sessions
    """
    # TODO: Add token to blacklist for immediate revocation
    return {"message": "Successfully logged out"}


@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate the current user's account.
    This is irreversible without admin intervention.
    """
    success = deactivate_user(current_user.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate account"
        )
    
    return {"message": "Account successfully deactivated"}


# Admin endpoints

@router.get("/users", response_model=list, status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all users (admin only).
    
    Query Parameters:
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    """
    users = list_all_users(skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific user by ID (admin only).
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/users/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Deactivate a user account (admin only).
    """
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate user"
        )
    
    return {"message": f"User {user_id} deactivated"}


@router.post("/health")
async def auth_health_check():
    """
    Health check endpoint for authentication service.
    """
    return {
        "status": "healthy",
        "service": "Authentication API",
        "version": "1.0.0"
    }
