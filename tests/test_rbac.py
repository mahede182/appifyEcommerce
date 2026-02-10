from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product

User = get_user_model()


class RBACTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            email='admin@test.com',
            role='admin'
        )
        
        self.customer_user = User.objects.create_user(
            username='customer',
            password='testpass123',
            email='customer@test.com',
            role='customer'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            stock_quantity=10
        )

    def test_unauthenticated_cannot_access_protected_endpoints(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        # Try to access products list (should work for read)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create product (should fail)
        response = self.client.post('/api/products/', {
            'name': 'New Product',
            'price': 10.00
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_manage_products(self):
        """Test that admin can perform CRUD operations on products"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create product
        response = self.client.post('/api/products/', {
            'name': 'Admin Product',
            'description': 'Created by admin',
            'price': 49.99,
            'stock_quantity': 5
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update product
        response = self.client.patch(f'/api/products/{self.product.id}/', {
            'price': 79.99
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete product
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_customer_cannot_manage_products(self):
        """Test that customer cannot perform CRUD operations on products"""
        self.client.force_authenticate(user=self.customer_user)
        
        # Try to create product
        response = self.client.post('/api/products/', {
            'name': 'Customer Product',
            'price': 10.00
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to update product
        response = self.client.patch(f'/api/products/{self.product.id}/', {
            'price': 79.99
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to delete product
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_manage_own_cart(self):
        """Test that customer can manage their own cart"""
        from cart.models import Cart
        
        self.client.force_authenticate(user=self.customer_user)
        
        # Get own cart
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create cart
        response = self.client.post('/api/cart/', {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify cart belongs to user
        cart = Cart.objects.get(user=self.customer_user)
        self.assertEqual(cart.user, self.customer_user)

    def test_admin_can_access_all_carts(self):
        """Test that admin can access all carts"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Get all carts
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_properties(self):
        """Test user role helper properties"""
        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.admin_user.is_customer)
        
        self.assertTrue(self.customer_user.is_customer)
        self.assertFalse(self.customer_user.is_admin)
