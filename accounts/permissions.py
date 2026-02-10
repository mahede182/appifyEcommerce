from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')
        )


class IsCustomer(permissions.BasePermission):
    """
    Allows access only to customer users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', '') == 'customer'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access if user is the owner of the object or an admin.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Admin can access any object
        if request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
            return True
            
        # Check if object has a user field and if it matches the current user
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # For cart objects, check if cart belongs to user
        if hasattr(obj, 'cart') and hasattr(obj.cart, 'user'):
            return obj.cart.user == request.user
            
        return False


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access to unauthenticated users, but requires authentication for write operations.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
