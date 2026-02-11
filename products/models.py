from django.db import models
from django.core.exceptions import ValidationError


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

    @property
    def available_stock(self):
        """Calculate available stock (total - reserved)"""
        return self.stock_quantity - self.reserved_stock

    def reserve_stock(self, quantity):
        """Reserve stock for cart items"""
        if quantity > self.available_stock:
            raise ValidationError(f'Insufficient stock. Only {self.available_stock} available.')
        
        self.reserved_stock += quantity
        self.save(update_fields=['reserved_stock'])

    def release_stock(self, quantity):
        """Release reserved stock back to available"""
        if quantity > self.reserved_stock:
            raise ValidationError('Cannot release more stock than reserved.')
        
        self.reserved_stock -= quantity
        self.save(update_fields=['reserved_stock'])

    def reduce_stock(self, quantity):
        """Permanently reduce stock after order completion"""
        if quantity > self.reserved_stock:
            raise ValidationError('Cannot reduce more stock than reserved.')
        
        self.reserved_stock -= quantity
        self.stock_quantity -= quantity
        self.save(update_fields=['reserved_stock', 'stock_quantity'])

    def is_in_stock(self, quantity=1):
        """Check if product has sufficient stock"""
        return self.available_stock >= quantity
