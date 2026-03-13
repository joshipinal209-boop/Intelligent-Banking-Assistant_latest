# Authentication Guide - FinCore Banking Assistant

## Overview

This guide explains how to use the JWT/OAuth2 authentication system in FinCore Banking Assistant. The authentication system provides secure access control with:

- **JWT (JSON Web Tokens)** for stateless authentication
- **OAuth2 Password Flow** for user login
- **Refresh Tokens** for long-lived sessions
- **Role-Based Access Control (RBAC)** with scopes
- **Password Hashing** with bcrypt for security

## Table of Contents

1. [Configuration](#configuration)
2. [User Registration & Login](#user-registration--login)
3. [API Authentication](#api-authentication)
4. [Token Management](#token-management)
5. [Scopes & Permissions](#scopes--permissions)
6. [Example Workflows](#example-workflows)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)

## Configuration

### Environment Variables

Update your `.env` file with the following authentication parameters:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google API (if using OAuth2 with Google)
GOOGLE_API_KEY=your-google-api-key-here
```

### Generate a Secure Secret Key

For production, generate a strong secret key:

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

Then add to your `.env`:
```
JWT_SECRET_KEY=<generated-key>
```

## User Registration & Login

### 1. Register a New User

**Endpoint:** `POST /auth/register`

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-03-13T10:00:00",
  "updated_at": "2026-03-13T10:00:00",
  "last_login": null
}
```

### 2. Login to Get Tokens

**Endpoint:** `POST /auth/login`

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Login via OAuth2 Form (for Swagger UI)

**Endpoint:** `POST /auth/login-form`

This endpoint is designed for browser-based testing in Swagger UI at `/docs`:

1. Go to `http://localhost:8000/docs`
2. Find the "Login" endpoint (POST /auth/login-form)
3. Click "Try it out"
4. Enter username and password
5. Click "Execute"

## API Authentication

### Using Access Tokens

All protected endpoints require authentication via Bearer token in the Authorization header:

```bash
curl -X GET "http://localhost:8000/customers" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Protected Endpoints

The following endpoints require authentication:

| Endpoint | Method | Required Scope | Description |
|----------|--------|-----------------|-------------|
| `/customers` | GET | `read` | Get customer list |
| `/query` | POST | `write` | Process banking query |
| `/audit/{session_id}` | GET | `read`, `audit` | Get audit trail |
| `/metrics` | GET | `admin` | Get performance metrics |
| `/audit/export` | GET | `admin` | Export audit logs |
| `/auth/me` | GET | - | Get current user info |
| `/auth/users` | GET | `admin` | List all users |

## Token Management

### Access Token Expiration

Access tokens expire after the configured `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 minutes).

When your access token expires, use the refresh token to get a new one without re-entering credentials.

### Refresh Access Token

**Endpoint:** `POST /auth/refresh`

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User Info

**Endpoint:** `GET /auth/me`

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Change Password

**Endpoint:** `POST /auth/change-password`

```bash
curl -X POST "http://localhost:8000/auth/change-password" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPassword123!",
    "new_password": "NewPassword456!",
    "confirm_password": "NewPassword456!"
  }'
```

### Logout

**Endpoint:** `POST /auth/logout`

```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

## Scopes & Permissions

Scopes define what actions a user can perform:

| Scope | Description | Example Use |
|-------|-------------|-------------|
| `read` | Read customer data and audit trails | View customer info |
| `write` | Create/modify banking operations | Process queries |
| `admin` | Full system access | Manage users, metrics |
| `audit` | Access to audit logs | View compliance trails |

### Default User Scopes

- **Regular Users:** `read`, `write`
- **Admin Users:** `read`, `write`, `admin`, `audit`

### Check User Scopes

Token scopes are embedded in the JWT. Decode token at [jwt.io](https://jwt.io) to view payload:

```json
{
  "sub": "user123",
  "scopes": ["read", "write"],
  "type": "access",
  "exp": 1678123456
}
```

## Example Workflows

### Complete Login Workflow

```bash
# 1. Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "SecurePass123!"
  }'

# 2. Login
RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePass123!"
  }')

# Extract tokens
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh_token')

# 3. Use access token
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. Refresh token when expired
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"

# 5. Logout
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "bob@example.com",
        "username": "bob",
        "password": "SecurePass123!"
    }
)
print("Register:", response.json())

# Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "bob",
        "password": "SecurePass123!"
    }
)
tokens = login_response.json()
access_token = tokens["access_token"]
print("Access Token:", access_token)

# Use token to access protected endpoint
headers = {"Authorization": f"Bearer {access_token}"}
me_response = requests.get(
    f"{BASE_URL}/auth/me",
    headers=headers
)
print("Current User:", me_response.json())

# Query the banking assistant
query_response = requests.post(
    f"{BASE_URL}/query",
    headers=headers,
    json={
        "session_id": "session-001",
        "query": "What's my account balance?"
    }
)
print("Query Response:", query_response.json())

# Refresh token
refresh_response = requests.post(
    f"{BASE_URL}/auth/refresh",
    json={"refresh_token": tokens["refresh_token"]}
)
new_access_token = refresh_response.json()["access_token"]
print("New Access Token:", new_access_token)
```

### JavaScript/Frontend Example

```javascript
// Register
async function register(email, username, password) {
  const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password })
  });
  return response.json();
}

// Login
async function login(username, password) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data;
}

// API call with token
async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    ...options.headers
  };
  
  return fetch(endpoint, { ...options, headers });
}

// Get customers
async function getCustomers() {
  const response = await apiCall('http://localhost:8000/customers');
  return response.json();
}

// Process query
async function processQuery(sessionId, query) {
  const response = await apiCall('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, query })
  });
  return response.json();
}

// Refresh token
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch('http://localhost:8000/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
}
```

## Security Best Practices

### 1. Protect Your Secret Key

- **Never commit `.env` to git** - The `.env` file contains secrets!
- **Use `.env.example`** - Track this in git without secrets
- **Different keys per environment** - Development, staging, production should have different keys
- **Rotate keys periodically** - Change JWT_SECRET_KEY every 30-90 days

### 2. HTTPS in Production

Always use HTTPS in production to prevent man-in-the-middle attacks:

```bash
# Development (HTTP is OK)
curl -X GET "http://localhost:8000/auth/me" -H "Authorization: Bearer ..."

# Production (HTTPS required)
curl -X GET "https://api.fincore.io/auth/me" -H "Authorization: Bearer ..."
```

### 3. Token Storage

**Frontend (Browser):**
- ✅ **Do:** Store tokens in httpOnly cookies (more secure)
- ❌ **Don't:** Store tokens in localStorage (vulnerable to XSS)
- ❌ **Don't:** Store tokens in sessionStorage (vulnerable to XSS)

### 4. Password Requirements

- Minimum 8 characters (enforced)
- Mix of uppercase, lowercase, numbers, special characters (recommend)
- Never send passwords in URL or query parameters
- Always use POST for password endpoints

### 5. Token Expiration

Configure reasonable expiration times:

```
ACCESS_TOKEN_EXPIRE_MINUTES=30    # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS=7       # Longer-lived
```

### 6. Audit Logging

All authentication events are logged:

```bash
# View auth audit trail
curl -X GET "http://localhost:8000/audit/{session_id}" \
  -H "Authorization: Bearer <token>"

# Export all audit logs (admin only)
curl -X GET "http://localhost:8000/audit/export" \
  -H "Authorization: Bearer <admin_token>" \
  > audit_logs.jsonl
```

### 7. Account Security

- Support account deactivation (not deletion)
- Implement rate limiting on login attempts
- Monitor for suspicious login patterns
- Require password change after failed attempts

## Troubleshooting

### "Could not validate credentials"

**Cause:** Token is invalid, expired, or malformed.

**Solutions:**
1. Check token is correctly formatted: `Authorization: Bearer <token>`
2. Login again to get new token
3. Use refresh endpoint if token expired
4. Verify JWT_SECRET_KEY matches between instances

### "Not enough permissions. Required scope: admin"

**Cause:** User doesn't have required scope for endpoint.

**Solutions:**
1. Check your user scopes: `GET /auth/me`
2. Contact admin to upgrade your permissions
3. Use different endpoint available to your scope level

### "Username already registered"

**Cause:** Email or username already exists.

**Solutions:**
1. Use unique username and email
2. Login if you already have an account
3. Contact admin for account recovery

### Token Expiration Issues

**Symptoms:** Requests suddenly start failing with 401 Unauthorized

**Solutions:**
1. Use refresh token to get new access token
2. Re-login with credentials
3. Check `ACCESS_TOKEN_EXPIRE_MINUTES` configuration

### Database Locked

**Cause:** Multiple processes accessing SQLite simultaneously.

**Solutions:**
1. Close other instances of the app
2. Implement connection pooling for production
3. Upgrade to PostgreSQL for multi-process use

## Database Schema

Authentication uses SQLite with three tables:

### users table
```sql
CREATE TABLE users (
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
);
```

### refresh_tokens table
```sql
CREATE TABLE refresh_tokens (
  token_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  token_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  is_revoked BOOLEAN DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### user_sessions table
```sql
CREATE TABLE user_sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  access_token TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  is_active BOOLEAN DEFAULT 1,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## Next Steps

1. **Add OAuth2 Provider Integration:** Google, Microsoft, GitHub
2. **Implement Rate Limiting:** Prevent brute force attacks
3. **Add Multi-Factor Authentication:** TOTP, SMS
4. **Upgrade to PostgreSQL:** For production deployments
5. **Add Token Blacklist:** Immediate token revocation
6. **Implement CORS Properly:** Restrict origins in production

## Support

For issues or questions:
1. Check Troubleshooting section above
2. Review logs in `logs/fincore.log`
3. Check JWT token at [jwt.io](https://jwt.io)
4. Open an issue on GitHub

---

**Last Updated:** March 13, 2026  
**Version:** 1.0.0
