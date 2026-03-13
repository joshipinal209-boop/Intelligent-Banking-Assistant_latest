"""
Integration tests for authentication endpoints with FastAPI.
Tests the complete authentication flow including registration, login, and token operations.
"""

import pytest
import os
import sys
import asyncio
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after path setup
from app import app

client = TestClient(app)

class TestAuthenticationIntegration:
    """Integration tests for authentication endpoints."""
    
    @classmethod
    def setup_class(cls):
        """Setup test fixtures."""
        cls.test_user = {
            "email": "integration@example.com",
            "username": "integrationtest",
            "full_name": "Integration Tester",
            "password": "IntegrationTest123!"
        }
    
    def test_health_check(self):
        """Test auth service health check."""
        response = client.post("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Authentication API"
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        response = client.post("/auth/register", json=self.test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == self.test_user["email"]
        assert data["username"] == self.test_user["username"]
        assert data["is_active"] is True
        assert data["is_admin"] is False
        assert "hashed_password" not in data  # Password should not be exposed
    
    def test_duplicate_registration(self):
        """Test that duplicate registration fails."""
        # First registration succeeds
        client.post("/auth/register", json=self.test_user)
        
        # Second registration should fail
        response = client.post("/auth/register", json=self.test_user)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login."""
        # Register first
        client.post("/auth/register", json=self.test_user)
        
        # Login
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    def test_login_wrong_password(self):
        """Test login with wrong password."""
        # Register first
        client.post("/auth/register", json=self.test_user)
        
        # Login with wrong password
        login_data = {
            "username": self.test_user["username"],
            "password": "WrongPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent",
            "password": "SomePassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test getting current user info."""
        # Register and login
        client.post("/auth/register", json=self.test_user)
        login_response = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == self.test_user["username"]
        assert data["email"] == self.test_user["email"]
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = client.get("/auth/me")
        assert response.status_code == 403
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401
    
    def test_refresh_token(self):
        """Test refresh token endpoint."""
        # Register and login
        client.post("/auth/register", json=self.test_user)
        login_response = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_with_invalid_token(self):
        """Test refresh with invalid token."""
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid.token.here"
        })
        assert response.status_code == 401
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        # Register and login
        client.post("/auth/register", json=self.test_user)
        login_response = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {"full_name": "Updated Name"}
        response = client.put(
            "/auth/me",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    def test_change_password(self):
        """Test password change."""
        # Register and login
        client.post("/auth/register", json=self.test_user)
        login_response = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Change password
        change_data = {
            "old_password": self.test_user["password"],
            "new_password": "NewPassword456!",
            "confirm_password": "NewPassword456!"
        }
        response = client.post(
            "/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        
        # Try login with new password
        login_response2 = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": "NewPassword456!"
        })
        assert login_response2.status_code == 200
    
    def test_logout(self):
        """Test logout endpoint."""
        # Register and login
        client.post("/auth/register", json=self.test_user)
        login_response = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_customer_endpoint_protected(self):
        """Test that customer endpoint requires authentication."""
        # Try without token
        response = client.get("/customers")
        assert response.status_code == 403  # Requires auth
        
        # Register and login
        client.post("/auth/register", json=self.test_user)
        login_response = client.post("/auth/login", json={
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        })
        access_token = login_response.json()["access_token"]
        
        # Try with token
        response = client.get(
            "/customers",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        # Should succeed (returns customers list or empty list)
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
