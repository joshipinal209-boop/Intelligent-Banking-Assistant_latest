# Authentication Workflows - Registration & Login Guide

## Overview

This guide demonstrates how to use the FinCore Banking Assistant authentication system to register new users and obtain tokens for API access.

---

## 1. Registration Workflow

### Purpose
Create new user accounts with email, username, and password.

### Registration Endpoint
```
POST /auth/register
Content-Type: application/json
```

### Request Example

#### cURL
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@fincore.com",
    "username": "alice_smith",
    "full_name": "Alice Smith",
    "password": "SecurePassword123!"
  }'
```

#### Python
```python
import requests

registration_data = {
    "email": "alice@fincore.com",
    "username": "alice_smith",
    "full_name": "Alice Smith",
    "password": "SecurePassword123!"
}

response = requests.post(
    "http://localhost:8000/auth/register",
    json=registration_data
)

user = response.json()
print(f"User Created: {user['username']}")
print(f"User ID: {user['user_id']}")
```

#### JavaScript/TypeScript
```javascript
const registrationData = {
  email: "alice@fincore.com",
  username: "alice_smith",
  full_name: "Alice Smith",
  password: "SecurePassword123!"
};

const response = await fetch("http://localhost:8000/auth/register", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(registrationData)
});

const user = await response.json();
console.log(`User Created: ${user.username}`);
console.log(`User ID: ${user.user_id}`);
```

### Success Response (201 Created)
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@fincore.com",
  "username": "alice_smith",
  "full_name": "Alice Smith",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-03-13T10:30:00",
  "updated_at": "2026-03-13T10:30:00",
  "last_login": null
}
```

### Error Responses

#### 409 - Username Already Exists
```json
{
  "detail": "Username already registered"
}
```

#### 400 - Invalid Email
```json
{
  "detail": "Email already in use"
}
```

#### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Registration Requirements

| Field | Requirements | Example |
|-------|--------------|---------|
| **email** | Valid email format, unique | user@fincore.com |
| **username** | 3-20 characters, unique | john_doe |
| **full_name** | Optional | John Doe |
| **password** | Minimum 8 characters | SecurePass123! |

### Password Best Practices
- ✅ Use at least 8 characters
- ✅ Mix uppercase and lowercase letters
- ✅ Include numbers and special characters
- ✅ Avoid common words or personal info
- ❌ Don't reuse passwords
- ❌ Don't share with others

---

## 2. Login Workflow

### Purpose
Authenticate users with username/password and obtain access/refresh tokens.

### Login Endpoint
```
POST /auth/login
Content-Type: application/json
```

### Request Example

#### cURL
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_smith",
    "password": "SecurePassword123!"
  }'
```

#### Python
```python
import requests

login_data = {
    "username": "alice_smith",
    "password": "SecurePassword123!"
}

response = requests.post(
    "http://localhost:8000/auth/login",
    json=login_data
)

tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

print(f"Access Token: {access_token[:50]}...")
print(f"Token Type: {tokens['token_type']}")
print(f"Expires In: {tokens['expires_in']} seconds")
```

#### JavaScript/TypeScript
```javascript
const loginData = {
  username: "alice_smith",
  password: "SecurePassword123!"
};

const response = await fetch("http://localhost:8000/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(loginData)
});

const tokens = await response.json();
const accessToken = tokens.access_token;
const refreshToken = tokens.refresh_token;

// Store tokens (use httpOnly cookies in production)
localStorage.setItem("access_token", accessToken);
localStorage.setItem("refresh_token", refreshToken);

console.log(`Login successful!`);
console.log(`Token expires in: ${tokens.expires_in} seconds`);
```

### Success Response (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTY0Njc2ODAwMH0...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTY0NzcyODAwMH0...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Error Responses

#### 401 - Invalid Credentials
```json
{
  "detail": "Incorrect username or password",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

#### 403 - Account Inactive
```json
{
  "detail": "User account is inactive"
}
```

#### 404 - User Not Found
```json
{
  "detail": "User not found"
}
```

### Token Information

#### Access Token
- **Duration**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Purpose**: Authenticate API requests
- **Format**: JWT with HS256 signature
- **Usage**: Include in `Authorization: Bearer <token>` header
- **Expiration**: Automatic after 30 minutes

#### Refresh Token
- **Duration**: 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
- **Purpose**: Get new access token without re-entering credentials
- **Format**: JWT with HS256 signature
- **Usage**: POST to `/auth/refresh` endpoint
- **Rotation**: New refresh token issued on refresh

---

## 3. Complete Authentication Flow

### Step-by-Step Example

#### Step 1: Register New User
```bash
# Create account
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@fincore.com",
    "username": "bob_jones",
    "password": "MyPassword456!"
  }'

# Response:
# {
#   "user_id": "...",
#   "username": "bob_jones",
#   "email": "bob@fincore.com",
#   ...
# }
```

#### Step 2: Login
```bash
# Login with credentials
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob_jones",
    "password": "MyPassword456!"
  }'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

#### Step 3: Store Tokens
```bash
# Save tokens for later use
ACCESS_TOKEN="eyJ..."
REFRESH_TOKEN="eyJ..."
```

#### Step 4: Use Access Token
```bash
# Make authenticated request
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Response:
# {
#   "user_id": "...",
#   "username": "bob_jones",
#   "email": "bob@fincore.com",
#   "is_active": true,
#   ...
# }
```

#### Step 5: Refresh Token When Expired
```bash
# Get new access token
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "'$REFRESH_TOKEN'"
  }'

# Response:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

---

## 4. Using Tokens in API Calls

### Authorization Header Format
```
Authorization: Bearer <access_token>
```

### Protected Endpoints Examples

#### Get Current User
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Get Customers
```bash
curl -X GET "http://localhost:8000/customers" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Process Query
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-001",
    "query": "What is my account balance?",
    "customer_id": "fa800b9e"
  }'
```

#### View Audit Trail
```bash
curl -X GET "http://localhost:8000/audit/session-001" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## 5. Token Management

### Check Token Status

#### Get Current User Info
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Decode JWT Token (at jwt.io or locally)
```python
import jwt

def decode_token(token, secret_key="your-secret"):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
    except jwt.InvalidTokenError:
        print("Invalid token")

# Get token details
payload = decode_token(ACCESS_TOKEN)
print(f"User ID: {payload['sub']}")
print(f"Expiration: {payload['exp']}")
print(f"Scopes: {payload['scopes']}")
```

### Refresh Expired Token
```bash
# When access token expires (after 30 min)
NEW_ACCESS=$(curl -s -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"'$REFRESH_TOKEN'"}' \
  | jq -r '.access_token')

# Use new token
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $NEW_ACCESS"
```

### Logout
```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Response:
# {
#   "message": "Successfully logged out"
# }
```

---

## 6. Advanced: Multiple Users

### Register Multiple Users
```bash
#!/bin/bash

# User 1
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@fincore.com","username":"user1","password":"Pass1234!"}'

# User 2
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@fincore.com","username":"user2","password":"Pass1234!"}'

# User 3
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user3@fincore.com","username":"user3","password":"Pass1234!"}'
```

### Login All Users and Store Tokens
```bash
#!/bin/bash

# Function to login and store token
login_user() {
    local username=$1
    local password=$2
    local output_file="${username}_token.txt"
    
    TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"$username\",\"password\":\"$password\"}" \
      | jq -r '.access_token')
    
    echo "$TOKEN" > "$output_file"
    echo "✅ Token saved: $output_file"
}

# Login all users
login_user "user1" "Pass1234!"
login_user "user2" "Pass1234!"
login_user "user3" "Pass1234!"
```

### Use Different User Tokens
```bash
# User 1 query
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $(cat user1_token.txt)"

# User 2 query
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $(cat user2_token.txt)"

# User 3 query
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $(cat user3_token.txt)"
```

---

## 7. Frontend Integration Example

### React Registration Form
```javascript
import React, { useState } from 'react';

export function RegisterForm() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSuccess(true);
        setFormData({ email: '', username: '', full_name: '', password: '' });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        name="email"
        placeholder="Email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="username"
        placeholder="Username"
        value={formData.username}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="full_name"
        placeholder="Full Name"
        value={formData.full_name}
        onChange={handleChange}
      />
      <input
        type="password"
        name="password"
        placeholder="Password (min 8 chars)"
        value={formData.password}
        onChange={handleChange}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>Registration successful!</p>}
    </form>
  );
}
```

### React Login Form
```javascript
import React, { useState } from 'react';

export function LoginForm() {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });

      if (response.ok) {
        const tokens = await response.json();
        
        // Store tokens in httpOnly cookies (more secure)
        // or localStorage (simpler)
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="username"
        placeholder="Username"
        value={credentials.username}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={credentials.password}
        onChange={handleChange}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
}
```

---

## 8. Security Best Practices

### During Development
- ✅ Use test credentials only
- ✅ Keep `.env` file secure (never commit)
- ✅ Use localhost for testing
- ✅ Enable CORS only for trusted origins

### For Production
- ✅ **Use HTTPS only** - Never HTTP
- ✅ **Store tokens in httpOnly cookies** - Never localStorage
- ✅ **Set secure flag on cookies** - Prevents XSS
- ✅ **Set sameSite attribute** - Prevents CSRF
- ✅ **Rotate secrets regularly** - Monthly or quarterly
- ✅ **Implement rate limiting** - Prevent brute force
- ✅ **Monitor failed logins** - Alert on suspicious activity
- ✅ **Use strong JWT secret** - At least 32 random characters

### Token Storage (Frontend)

#### ❌ NOT Recommended
```javascript
// Don't store in localStorage (XSS vulnerable)
localStorage.setItem('token', token);
```

#### ✅ Recommended
```javascript
// Store in httpOnly cookie (more secure)
// Server sets via Set-Cookie header
// Browser automatically includes in requests
```

---

## 9. Common Issues & Solutions

### Issue: "Username already registered"
```
Solution: Choose a different username or login if account exists
```

### Issue: "Incorrect username or password"
```
Solution: 
1. Verify username spelling
2. Check caps lock
3. Ensure password is correct
4. Request password reset if needed
```

### Issue: "Token expired"
```
Solution:
1. Use refresh endpoint to get new token
2. Or re-login with credentials
```

### Issue: "Could not validate credentials" (401)
```
Solution:
1. Verify token is included in header
2. Format: Authorization: Bearer <token>
3. Check token hasn't expired
4. Get new token with /auth/refresh
```

---

## 10. Testing Registration & Login

### Automated Test Script
```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
USERNAME="testuser_$(date +%s)"
PASSWORD="TestPass123!"
EMAIL="test_$(date +%s)@fincore.com"

echo "🧪 Testing Registration & Login"
echo "================================"

# 1. Register
echo -e "\n1️⃣  Registering user: $USERNAME"
REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }")

USER_ID=$(echo $REGISTER | jq -r '.user_id')
echo "   ✅ User created: $USER_ID"

# 2. Login
echo -e "\n2️⃣  Logging in as: $USERNAME"
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }")

ACCESS_TOKEN=$(echo $LOGIN | jq -r '.access_token')
EXPIRES=$(echo $LOGIN | jq -r '.expires_in')
echo "   ✅ Login successful"
echo "   ✅ Token expires in: $EXPIRES seconds"

# 3. Get current user
echo -e "\n3️⃣  Fetching current user info"
CURRENT=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "   ✅ Username: $(echo $CURRENT | jq -r '.username')"
echo "   ✅ Email: $(echo $CURRENT | jq -r '.email')"

# 4. Test protected endpoint
echo -e "\n4️⃣  Testing protected endpoint"
CUSTOMERS=$(curl -s -X GET "$BASE_URL/customers" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "   ✅ Customers endpoint accessible"

echo -e "\n✅ All tests passed!"
```

---

## Summary

| Step | Endpoint | Method | Auth Required |
|------|----------|--------|---------------|
| Register | `/auth/register` | POST | No |
| Login | `/auth/login` | POST | No |
| Get User | `/auth/me` | GET | Yes |
| Refresh | `/auth/refresh` | POST | No |
| Logout | `/auth/logout` | POST | Yes |

**Tokens**: 
- Access Token: 30 minutes
- Refresh Token: 7 days

**Security**: Argon2 passwords + JWT HS256 signing

---

**Last Updated**: March 13, 2026  
**Version**: 1.0.0
