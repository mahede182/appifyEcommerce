from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.is_superuser or self.role == 'admin'
    
    @property
    def is_customer(self):
        """Check if user is customer"""
        return self.role == 'customer'
