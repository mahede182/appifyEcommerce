from django.contrib import admin

from accounts.mixins import AdminRoleMixin
from .models import Product


@admin.register(Product)
class ProductAdmin(AdminRoleMixin, admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity')
    search_fields = ('name',)

