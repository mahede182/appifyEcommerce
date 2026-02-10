# Authentication API Documentation

## Overview
This Django e-commerce application now implements a complete authentication system with JWT tokens, replacing the old `users` app with a cleaner `authentication` app.

## 🔐 Authentication Endpoints

### User Registration
```http
POST /auth/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "role": "customer",
    "first_name": "Test",
    "last_name": "User"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "customer",
            "date_joined": "2024-01-01T00:00:00Z"
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    }
}
```

### User Login
```http
POST /auth/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "TestPass123!"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "customer"
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    }
}
```

### User Logout
```http
POST /auth/logout/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "refresh": "<refresh_token>"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

### Get User Profile
```http
GET /auth/user/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer",
        "date_joined": "2024-01-01T00:00:00Z"
    }
}
```

### Update User Profile
```http
PUT /auth/user/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "first_name": "Updated",
    "last_name": "Name",
    "email": "updated@example.com"
}
```

### Change Password
```http
POST /auth/password/change/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "old_password": "OldPass123!",
    "new_password": "NewPass123!"
}
```

## 🔑 JWT Token Configuration

- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Token Rotation**: Enabled
- **Blacklist After Rotation**: Enabled

## 🛡️ Security Features

### Password Validation
- Minimum length validation
- Common password detection
- User attribute similarity check
- Numeric password detection

### CORS Configuration
- Allowed origins for development
- Credentials support enabled
- Production-safe configuration

### Rate Limiting
- Login attempt limiting (recommended)
- Registration rate limiting (recommended)

## 👥 User Roles

### Customer Role
- Can browse products
- Can manage own cart and orders
- Can update own profile
- Cannot access admin features

### Admin Role
- Full system access
- Can manage all products
- Can manage all orders and users
- Can access admin panel

## 🚀 Usage Examples

### Python Requests Example
```python
import requests

# Register user
response = requests.post('http://localhost:8000/auth/register/', json={
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'TestPass123!',
    'password_confirm': 'TestPass123!',
    'role': 'customer'
})

# Get tokens
tokens = response.json()['data']['tokens']
access_token = tokens['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/products/', headers=headers)
```

### JavaScript/Fetch Example
```javascript
// Login
const response = await fetch('/auth/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'testuser',
        password: 'TestPass123!'
    })
});

const data = await response.json();
const accessToken = data.data.tokens.access;

// Authenticated request
const productsResponse = await fetch('/api/products/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
});
```

## 🔄 Migration from Users App

The old `users` app has been completely replaced by `authentication`:

1. **Models**: User model moved with enhanced role properties
2. **Permissions**: All RBAC permissions preserved and enhanced
3. **Admin**: Admin mixins and configurations updated
4. **API**: New JWT-based authentication endpoints
5. **Security**: Enhanced with modern authentication practices

## 🧪 Testing

Run the test script to verify all endpoints:
```bash
python test_auth_api.py
```

## 📝 Error Responses

All endpoints return consistent error responses:
```json
{
    "success": false,
    "message": "Operation failed",
    "errors": {
        "field": ["Error message"]
    }
}
```

## 🔧 Configuration

Key settings in `settings.py`:
- `SIMPLE_JWT`: JWT configuration
- `CORS_ALLOWED_ORIGINS`: CORS settings
- `AUTH_USER_MODEL`: Custom user model

This authentication system provides a secure, modern foundation for the e-commerce application with proper role-based access control.
