# Accounts Authentication API Documentation

## Overview
This Django e-commerce application implements a complete authentication system using the `accounts` app with JWT tokens, following Django best practices for app naming.

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

### User Logout
```http
POST /auth/logout/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "refresh": "<refresh_token>"
}
```

### Get/Update User Profile
```http
GET /auth/user/
Authorization: Bearer <access_token>

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

## 🏗️ App Structure

The application follows Django best practices with clear separation of concerns:

```
accounts/          # User authentication and management
├── models.py      # Custom User model with roles
├── views.py       # Authentication endpoints
├── serializers.py # Data validation and serialization
├── permissions.py # Role-based permissions
├── mixins.py      # Admin mixins
├── urls.py        # Authentication URL patterns
└── admin.py       # User admin configuration

products/          # Product catalog and management
cart/              # Shopping cart functionality  
orders/            # Order processing and management
```

## 👥 User Roles & Permissions

### Customer Role
- Can browse products (GET /api/products/)
- Can manage own cart (POST/GET/DELETE /api/cart/)
- Can manage own orders (POST/GET /api/orders/)
- Can update own profile (GET/PUT /auth/user/)
- Cannot access admin features

### Admin Role  
- Full system access via admin panel
- Can manage all products (CRUD /api/products/)
- Can manage all orders and users
- Can access all customer data
- Full API permissions

## 🔑 JWT Configuration

- **Access Token**: 60 minutes lifetime
- **Refresh Token**: 7 days lifetime
- **Token Rotation**: Enabled (security best practice)
- **Blacklisting**: Enabled after rotation
- **Algorithm**: HS256

## 🛡️ Security Features

### Authentication Security
- Password strength validation (Django built-in)
- Common password detection
- User attribute similarity check
- Secure password hashing

### API Security
- JWT token authentication
- CORS configuration for frontend
- CSRF protection enabled
- Rate limiting ready (implement as needed)

### Role-Based Access Control
- Custom permission classes
- Object-level permissions
- Admin role verification
- Customer data isolation

## 🚀 Usage Examples

### Python/Requests
```python
import requests

# Register new user
response = requests.post('http://localhost:8000/auth/register/', json={
    'username': 'customer1',
    'email': 'customer@example.com',
    'password': 'SecurePass123!',
    'password_confirm': 'SecurePass123!',
    'role': 'customer'
})

# Get tokens for authentication
tokens = response.json()['data']['tokens']
access_token = tokens['access']

# Make authenticated API request
headers = {'Authorization': f'Bearer {access_token}'}
products = requests.get('http://localhost:8000/api/products/', headers=headers)
```

### JavaScript/Fetch
```javascript
// User login
const loginResponse = await fetch('/auth/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'customer1',
        password: 'SecurePass123!'
    })
});

const {data} = await loginResponse.json();
const accessToken = data.tokens.access;

// Authenticated API call
const productsResponse = await fetch('/api/products/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
});
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_auth_api.py
```

This will test:
- User registration (customer and admin)
- Login/logout flow
- Profile management
- Token handling
- Permission validation

## 📝 API Response Format

All endpoints follow consistent response format:

**Success Response:**
```json
{
    "success": true,
    "message": "Operation successful",
    "data": {...}
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Operation failed", 
    "errors": {
        "field": ["Error description"]
    }
}
```

## 🔄 Migration from Previous System

The authentication system has been completely refactored:

1. **App renamed**: `users` → `accounts` (Django convention)
2. **JWT implementation**: Modern token-based authentication
3. **Enhanced security**: Token rotation, blacklisting, CORS
4. **Clean endpoints**: RESTful API design
5. **Preserved RBAC**: All role-based permissions maintained

## 📚 Best Practices Followed

- **Unix Philosophy**: "Do one thing and do it well"
- **DRY Principle**: Reusable components and mixins
- **KISS Principle**: Simple, maintainable code
- **Django Conventions**: Standard app naming and structure
- **Security First**: Modern authentication practices
- **REST Standards**: Proper HTTP methods and status codes

This `accounts` app provides a secure, scalable foundation for user authentication in your e-commerce system.
