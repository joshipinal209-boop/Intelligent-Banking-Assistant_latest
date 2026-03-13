"""
Tests for authentication system including JWT, OAuth2, and user management.
"""

import pytest
import os
import sys
from datetime import timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.utils import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    get_password_hash,
    verify_password,
    is_token_expired,
)
from auth.models import (
    UserCreate,
    create_user,
    get_user_by_username,
    authenticate_user,
    get_user_by_id,
    update_user,
    UserUpdate,
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should not be the same as password
        assert hashed != password
        # Hash should be a string
        assert isinstance(hashed, str)
    
    def test_verify_correct_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpassword", hashed) is False


class TestTokenGeneration:
    """Test JWT token generation and verification."""
    
    def test_create_access_token(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_access_token(self):
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)
        
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_refresh_token(self):
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        payload = verify_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
    
    def test_token_with_scopes(self):
        data = {"sub": "user123"}
        scopes = ["read", "write", "admin"]
        token = create_access_token(data, scopes=scopes)
        
        payload = verify_access_token(token)
        assert payload["scopes"] == scopes
    
    def test_invalid_token_verification(self):
        payload = verify_access_token("invalid.token.here")
        assert payload is None
    
    def test_access_token_rejects_refresh_token(self):
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        # Trying to verify refresh token as access token should fail
        payload = verify_access_token(token)
        assert payload is None
    
    def test_refresh_token_rejects_access_token(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        # Trying to verify access token as refresh token should fail
        payload = verify_refresh_token(token)
        assert payload is None


class TestUserManagement:
    """Test user creation, authentication, and management."""
    
    def test_create_user(self):
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123"
        )
        
        user = create_user(user_data)
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_admin is False
    
    def test_get_user_by_username(self):
        user_data = UserCreate(
            email="user2@example.com",
            username="user2",
            password="password123"
        )
        
        created_user = create_user(user_data)
        found_user = get_user_by_username("user2")
        
        assert found_user is not None
        assert found_user.username == "user2"
        assert found_user.hashed_password is not None
    
    def test_authenticate_user_success(self):
        user_data = UserCreate(
            email="auth@example.com",
            username="authuser",
            password="password123"
        )
        
        create_user(user_data)
        
        authenticated = authenticate_user("authuser", "password123")
        
        assert authenticated is not None
        assert authenticated.username == "authuser"
    
    def test_authenticate_user_wrong_password(self):
        user_data = UserCreate(
            email="auth2@example.com",
            username="authuser2",
            password="password123"
        )
        
        create_user(user_data)
        
        authenticated = authenticate_user("authuser2", "wrongpassword")
        
        assert authenticated is None
    
    def test_authenticate_nonexistent_user(self):
        authenticated = authenticate_user("nonexistent", "password123")
        assert authenticated is None
    
    def test_get_user_by_id(self):
        user_data = UserCreate(
            email="userid@example.com",
            username="useridtest",
            password="password123"
        )
        
        created_user = create_user(user_data)
        found_user = get_user_by_id(created_user.user_id)
        
        assert found_user is not None
        assert found_user.user_id == created_user.user_id
    
    def test_update_user(self):
        user_data = UserCreate(
            email="update@example.com",
            username="updateuser",
            full_name="Old Name",
            password="password123"
        )
        
        created_user = create_user(user_data)
        
        update_data = UserUpdate(full_name="New Name")
        updated_user = update_user(created_user.user_id, update_data)
        
        assert updated_user is not None
        assert updated_user.full_name == "New Name"


class TestTokenExpiration:
    """Test token expiration handling."""
    
    def test_is_token_expired_false(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        # Fresh token should not be expired
        assert is_token_expired(token) is False
    
    def test_is_token_expired_true(self):
        data = {"sub": "user123"}
        expires_delta = timedelta(seconds=-1)  # Expired 1 second ago
        token = create_access_token(data, expires_delta=expires_delta)
        
        # Expired token should be marked as expired
        assert is_token_expired(token) is True
    
    def test_is_invalid_token_expired_true(self):
        # Invalid tokens should be considered expired
        assert is_token_expired("invalid.token.here") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
