# RBAC Implementation Documentation

## Overview
This Django e-commerce application now implements comprehensive Role-Based Access Control (RBAC) with two main roles: Admin and Customer.

## User Roles and Permissions

### Admin Role
**Full system access with the following capabilities:**

#### Product Management
- ✅ Add new products
- ✅ Edit product details (price, name, description)
- ✅ Delete products
- ✅ View all products

#### Order Management
- ✅ View all customer orders
- ✅ Update order status (pending, shipped, delivered, canceled)
- ✅ Access all order details

#### Customer Management
- ✅ View customer list
- ✅ Block/unblock customers
- ✅ Manage user accounts

#### Cart Management
- ✅ View all customer carts
- ✅ Manage cart items for any customer

#### System Administration
- ✅ Access Django admin interface
- ✅ Manage all system data
- ✅ View system reports and analytics

### Customer Role
**Limited access with customer-specific capabilities:**

#### Product Browsing
- ✅ View products by category
- ✅ Search products
- ✅ View product details (price, description, images)

#### Cart Management
- ✅ Add/remove products from own cart
- ✅ Update cart quantities
- ✅ View own cart

#### Order Management
- ✅ Place orders
- ✅ View own order history
- ✅ Track own order status
- ✅ Cancel/return own orders

#### Profile Management
- ✅ Update personal information
- ✅ Change password
- ✅ Manage account settings

## Security Features

### Authentication Required
- All API endpoints require authentication except public product browsing
- Token-based authentication using Django REST Framework
- Session authentication support

### Authorization Controls
- Role-based permissions on all endpoints
- Object-level permissions for resource ownership
- Admin override capabilities for system management

### Edge Cases Handled
- ✅ Unauthenticated users cannot access protected endpoints
- ✅ Customers cannot access other customers' data
- ✅ Admin operations are properly restricted
- ✅ Proper HTTP status codes (401/403) for authorization failures

## API Endpoints

### Public Access (Read-only)
```
GET /api/products/     # View all products
GET /api/products/{id}/ # View specific product
```

### Customer Access
```
GET/POST /api/cart/           # Manage own cart
GET/POST/PUT/DELETE /api/cart-items/  # Manage own cart items
GET/POST /api/orders/         # Manage own orders
GET/PUT/DELETE /api/order-items/      # Manage own order items
```

### Admin Access
```
GET/POST/PUT/DELETE /api/users/        # User management
GET/POST/PUT/DELETE /api/products/     # Product management
GET/POST/PUT/DELETE /api/cart/          # All cart management
GET/POST/PUT/DELETE /api/cart-items/   # All cart item management
GET/POST/PUT/DELETE /api/orders/        # All order management
GET/POST/PUT/DELETE /api/order-items/  # All order item management
```

## Implementation Details

### Custom Permission Classes
- `IsAdmin`: Allows access only to admin users
- `IsCustomer`: Allows access only to customer users
- `IsOwnerOrAdmin`: Allows access if user owns the object or is admin
- `IsAuthenticatedOrReadOnly`: Read access for unauthenticated, write for authenticated

### User Model Enhancements
- Custom User model with role field
- Helper properties: `is_admin`, `is_customer`
- Integration with Django's auth system

### Security Configuration
- Default authentication: Session + Token
- Default permissions: IsAuthenticated
- Role-based viewset permissions

## Testing
Comprehensive test suite covering:
- Unauthenticated access attempts
- Role-based permissions
- Object-level permissions
- Cross-role access prevention
- User role properties

## Usage Examples

### Admin Usage
```python
# Create admin user
admin = User.objects.create_user(
    username='admin',
    password='admin123',
    role='admin'
)

# Admin can manage products
client.force_authenticate(user=admin)
response = client.post('/api/products/', {
    'name': 'New Product',
    'price': 99.99
})
```

### Customer Usage
```python
# Create customer user
customer = User.objects.create_user(
    username='customer',
    password='customer123',
    role='customer'
)

# Customer can manage own cart
client.force_authenticate(user=customer)
response = client.post('/api/cart-items/', {
    'cart': 1,
    'product': 1,
    'quantity': 2
})
```

This RBAC implementation ensures secure, role-based access control while maintaining clean separation of concerns and following Django best practices.
