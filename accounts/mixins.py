class AdminRoleMixin:
    """Mixin to restrict admin access to users with role='admin' or superusers."""
    
    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        # Allow if superuser or has 'admin' role
        return request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
