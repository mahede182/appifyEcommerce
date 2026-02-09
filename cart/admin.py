from django.contrib import admin

from users.mixins import AdminRoleMixin
from .models import Cart, CartItem

class CartItemInline(AdminRoleMixin, admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(AdminRoleMixin, admin.ModelAdmin):
    list_display = ('user',)
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(AdminRoleMixin, admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')

