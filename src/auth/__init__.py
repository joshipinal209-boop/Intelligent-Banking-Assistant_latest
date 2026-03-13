"""
Authentication module for FinCore Banking Assistant.

Provides:
- JWT/OAuth2 authentication
- User registration and login
- Refresh token rotation
- Role-based access control (RBAC)
- Password hashing with bcrypt
"""

from auth.utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_access_token,
    verify_refresh_token,
    get_password_hash,
    verify_password,
)

from auth.models import (
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
    Token,
    TokenData,
    LoginRequest,
    RefreshTokenRequest,
    PasswordChangeRequest,
)

from auth.dependencies import (
    get_current_user,
    get_current_admin_user,
    require_scopes,
    oauth2_scheme,
    get_optional_user,
    RoleChecker,
)

from auth.routes import router

__all__ = [
    # Utils
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "verify_access_token",
    "verify_refresh_token",
    "get_password_hash",
    "verify_password",
    # Models
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    # Dependencies
    "get_current_user",
    "get_current_admin_user",
    "require_scopes",
    "oauth2_scheme",
    "get_optional_user",
    "RoleChecker",
    # Router
    "router",
]
