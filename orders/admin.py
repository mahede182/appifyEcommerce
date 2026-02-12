from django.contrib import admin
from .models import Order, OrderItem
from accounts.mixins import AdminRoleMixin

class OrderItemInline(AdminRoleMixin, admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(AdminRoleMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(AdminRoleMixin, admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_at_purchase')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
