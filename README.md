# Appify E-commerce Platform

A comprehensive Django REST API e-commerce platform with robust inventory management, role-based authentication, and real-time stock tracking.

## 🚀 Features

- 🔐 **Authentication & Authorization**: JWT-based auth with role-based access control (Admin/Customer)
- 📦 **Product Management**: Full CRUD operations with admin-only restrictions
- 🛒 **Cart Management**: Real-time stock reservation and validation
- 📋 **Order Processing**: Complete checkout flow with permanent stock reduction
- 🛡️ **Inventory Control**: Atomic operations preventing overselling
- 📚 **API Documentation**: Comprehensive Swagger/OpenAPI documentation
- 🔒 **Security**: Rate limiting, input validation, and fraud prevention

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 6.0.2
- **API**: Django REST Framework 3.16.1
- **Authentication**: django-rest-framework-simplejwt 5.5.1
- **Database**: SQLite (development)
- **Documentation**: drf-spectacular 0.29.0
- **Security**: django-cors-headers 4.9.0

### Development Tools
- **Package Manager**: pip (standard)
- **Virtual Environment**: venv (built-in)
- **Python**: 3.12+
- **Environment**: Development/Production ready

## 📋 Setup Instructions

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd appifyEcommerce
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   # Create .env file (copy from .env.example if available)
   echo "SECRET_KEY=your-secret-key-here" > .env
   echo "DEBUG=True" >> .env
   echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> .env
   ```

5. **Database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🗄️ Database Schema

### Core Models

#### User Model (Custom)
```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    email = models.EmailField(unique=True)
```

#### Product Model
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)      # Total stock
    reserved_stock = models.PositiveIntegerField(default=0)      # In carts
    
    @property
    def available_stock(self):
        return self.stock_quantity - self.reserved_stock
```

#### Cart & CartItem Models
```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
```

#### Order & OrderItem Models
```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
```

### ER Diagram

```
User (1) -----> (1) Cart
User (1) -----> (N) Order
Cart (1) -----> (N) CartItem
Order (1) ----> (N) OrderItem
Product (1) --> (N) CartItem
Product (1) --> (N) OrderItem
```

## 🏗️ Key Architectural Decisions

### 1. **Stock Management Strategy**
- **Reservation System**: Stock is reserved when items are added to cart
- **Atomic Operations**: All stock operations use database transactions
- **Concurrency Control**: `select_for_update()` prevents race conditions
- **Real-time Tracking**: `available_stock` property reflects current availability

### 2. **Authentication & Authorization**
- **JWT Tokens**: Stateless authentication with refresh token rotation
- **Role-Based Access**: Separate permissions for Admin and Customer roles
- **Security**: Password hashing, token blacklisting, and session management

### 3. **API Design Principles**
- **RESTful Design**: Proper HTTP methods and status codes
- **Consistent Responses**: Standardized success/error response format
- **Validation**: Comprehensive input validation at serializer level
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

### 4. **Database Design**
- **Normalization**: Proper relationships and constraints
- **Indexing**: Optimized queries for frequently accessed data
- **Constraints**: Unique constraints prevent duplicate cart items
- **Data Integrity**: Foreign key constraints maintain relationships

### 5. **Error Handling**
- **Graceful Degradation**: User-friendly error messages
- **Logging**: Comprehensive error tracking
- **Validation**: Clear validation errors with field-specific messages
- **HTTP Standards**: Proper status codes for different error types

## 📊 API Endpoints

### Authentication
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout
- `GET /auth/me/` - User profile
- `POST /auth/password/change/` - Change password

### Products (Admin only for write operations)
- `GET /api/products/` - List products
- `POST /api/products/` - Create product (Admin)
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product (Admin)
- `DELETE /api/products/{id}/` - Delete product (Admin)

### Cart Operations
- `GET /api/cart/` - Get user cart
- `POST /api/cart-items/` - Add item to cart
- `PUT /api/cart-items/{id}/` - Update cart item
- `DELETE /api/cart-items/{id}/` - Remove cart item
- `GET /cart/summary/` - Cart summary with stock info
- `POST /cart/checkout/` - Process checkout

### Orders
- `GET /api/orders/` - User orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Get order details

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI schema

## 🎯 Assumptions Made

### Business Logic Assumptions
1. **Single Cart per User**: Each user can have only one active cart
2. **Stock Reservation**: Items in cart reserve stock until checkout
3. **Order Finalization**: Stock is permanently reduced only on successful checkout
4. **Price at Purchase**: Order items store price at time of purchase (not current price)

### Technical Assumptions
1. **Single Database**: Application uses a single database instance
2. **Synchronous Operations**: All operations are synchronous (no background jobs)
3. **File Storage**: No file/image storage implemented for products
4. **Payment Processing**: Payment gateway integration not included

### Security Assumptions
1. **Trusted Environment**: API endpoints assume trusted client applications
2. **Basic Rate Limiting**: No advanced rate limiting implemented
3. **Email Verification**: Email verification for registration not implemented
4. **Password Policy**: Basic password validation only

### Scaling Assumptions
1. **Single Server**: Designed for single-server deployment
2. **Database Load**: SQLite suitable for development, PostgreSQL for production
3. **Session Storage**: Database-backed sessions (not Redis)
4. **Caching**: No caching layer implemented

## 🔧 Development Guidelines

### Code Organization
- **Apps**: Modular structure (accounts, products, cart, orders)
- **Serializers**: API serialization with validation
- **ViewSets**: RESTful viewsets with proper permissions
- **Permissions**: Role-based access control

### Testing
- **Unit Tests**: Model and serializer tests
- **Integration Tests**: API endpoint tests
- **Stock Management**: Comprehensive inventory tests

### Security Best Practices
- **Input Validation**: All user inputs validated
- **SQL Injection**: Django ORM prevents SQL injection
- **XSS Protection**: Django's built-in XSS protection
- **CSRF Protection**: CSRF tokens for state-changing operations

## 🚀 Deployment Considerations

### Production Setup
- **Database**: PostgreSQL recommended for production
- **Web Server**: Nginx + Gunicorn/uvicorn
- **Environment Variables**: Secure configuration management
- **Static Files**: Proper static file serving

### Monitoring
- **Logging**: Comprehensive application logging
- **Error Tracking**: Sentry or similar service
- **Performance Monitoring**: Application performance metrics
- **Database Monitoring**: Query performance and connection pooling

## 📝 Contributing

1. Follow PEP 8 style guidelines
2. Write comprehensive tests for new features
3. Update API documentation for new endpoints
4. Ensure proper error handling and validation
5. Follow the existing code organization patterns

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/api/docs/`
- Review the test files for usage examples