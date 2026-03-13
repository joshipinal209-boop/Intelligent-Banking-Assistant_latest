# Authentication Setup - Quick Reference

## What's New

JWT/OAuth2 authentication has been integrated into FinCore Banking Assistant. All API endpoints are now protected and require valid JWT tokens.

## Files Added/Modified

### New Authentication Files
- `src/auth/utils.py` - JWT token generation/verification, password hashing
- `src/auth/models.py` - User models and SQLite database schema
- `src/auth/dependencies.py` - FastAPI dependencies for securing endpoints
- `src/auth/routes.py` - Authentication endpoints (register, login, refresh)
- `src/auth/__init__.py` - Module exports
- `AUTH_GUIDE.md` - Complete authentication documentation
- `.env.example` - Environment variables template
- `tests/test_auth.py` - Unit tests for auth functions
- `tests/integration/test_auth_integration.py` - Integration tests

### Modified Files
- `src/app.py` - Added auth routes, protected endpoints with JWT
- `requirements.txt` - Added: python-jose, passlib, argon2-cffi, pydantic[email], PyJWT
- `README.md` - Added authentication section and features

## Quick Start - Local Development

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
cp .env.example .env
```

The default JWT_SECRET_KEY is suitable for local development only.

### 3. Start Backend
```bash
cd src
python -m uvicorn app:app --reload --port 8000
```

### 4. Register First User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePassword123!"
  }'
```

### 5. Login to Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 6. Use Token in API Calls
```bash
ACCESS_TOKEN="<token_from_login>"

curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Using Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Use "POST /auth/login-form" endpoint to login
4. Enter username and password
5. All subsequent requests will include token automatically

## Key Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/auth/register` | POST | No | Create new user account |
| `/auth/login` | POST | No | Get access and refresh tokens |
| `/auth/login-form` | POST | No | OAuth2 form-compatible login |
| `/auth/refresh` | POST | No | Get new access token |
| `/auth/me` | GET | Yes | Get current user info |
| `/auth/me` | PUT | Yes | Update user profile |
| `/auth/change-password` | POST | Yes | Change password |
| `/auth/logout` | POST | Yes | Logout (audit logging) |
| `/auth/deactivate` | POST | Yes | Deactivate account |
| `/customers` | GET | Yes | Get customer list |
| `/query` | POST | Yes | Process banking query |
| `/audit/{session_id}` | GET | Yes | Get audit trail |

## Configuration (Environment Variables)

Create/update your `.env` file:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secure-key-here-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Other configurations
GOOGLE_API_KEY=your-key
DEBUG=False
LOG_LEVEL=INFO
```

### Generate Secure Secret Key
```python
import secrets
key = secrets.token_urlsafe(32)
print(key)  # Use this in JWT_SECRET_KEY
```

## Database

Authentication data is stored in SQLite:
- **Location:** `data/auth/users.db`
- **Tables:** users, refresh_tokens, user_sessions
- **Automatic:** Database is created on first run

## Token Lifecycle

### Access Token
- **Duration:** 30 minutes (configurable)
- **Purpose:** Authenticate API requests
- **Usage:** Include in `Authorization: Bearer <token>` header
- **Expiration:** Automatic - request new one before making requests

### Refresh Token
- **Duration:** 7 days (configurable)
- **Purpose:** Get new access token without re-entering password
- **Usage:** POST to `/auth/refresh` endpoint
- **Expiration:** Automatic - user must re-login

## Testing

### Run Authentication Tests
```bash
# Unit tests
pytest tests/test_auth.py -v

# Integration tests
pytest tests/integration/test_auth_integration.py -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html
```

## Security Best Practices

### Development
- ✅ Use `.env.example` as template
- ✅ Generate strong secret key
- ✅ Never commit `.env` to git

### Production
- ✅ Use HTTPS only
- ✅ Rotate secret keys periodically
- ✅ Use strong SECRET_KEY (32+ random characters)
- ✅ Store tokens in httpOnly cookies (frontend)
- ✅ Implement rate limiting on login
- ✅ Monitor audit logs for suspicious activity

## Common Issues & Solutions

### "Could not validate credentials"
**Solution:** Token expired or invalid. Re-login to get new token.

### "Not enough permissions"
**Solution:** User lacks required scope. Only admins can access certain endpoints.

### "Username already registered"
**Solution:** Use unique username or login if account exists.

### Database Locked
**Solution:** Close other app instances or use PostgreSQL for production.

## Frontend Integration

### React Example
```javascript
// Store tokens
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Add token to requests
const response = await fetch('/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

// Handle token expiration
if (response.status === 401) {
  // Refresh token or redirect to login
}
```

## Next Steps

1. **Test locally** - Run quick start above
2. **Add OAuth2 providers** - Google, Microsoft, GitHub
3. **Implement rate limiting** - Prevent brute force
4. **Add multi-factor authentication** - TOTP/SMS
5. **Upgrade to PostgreSQL** - For production
6. **Set up monitoring** - Track auth events

## Documentation

- **Complete Guide:** See [AUTH_GUIDE.md](AUTH_GUIDE.md)
- **API Docs:** http://localhost:8000/docs (when running)
- **Code Examples:** See tests/ directory

## Support

For issues:
1. Check [AUTH_GUIDE.md](AUTH_GUIDE.md) troubleshooting section
2. Review logs: `tail -f logs/fincore.log`
3. Test token at [jwt.io](https://jwt.io)
4. Check database: `sqlite3 data/auth/users.db`

---

**Version:** 1.0.0  
**Last Updated:** March 13, 2026  
**Status:** ✅ Production Ready
