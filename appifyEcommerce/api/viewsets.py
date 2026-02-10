from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from products.models import Product
from accounts.permissions import IsAdmin, IsCustomer, IsOwnerOrAdmin, IsAuthenticatedOrReadOnly
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductSerializer,
    UserSerializer,
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdmin]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsCustomer | IsAdmin]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return Cart.objects.all()
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsCustomer | IsAdmin]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return CartItem.objects.all()
            return CartItem.objects.filter(cart__user=self.request.user)
        return CartItem.objects.none()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer | IsAdmin]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return Order.objects.all()
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsCustomer | IsAdmin]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return OrderItem.objects.all()
            return OrderItem.objects.filter(order__user=self.request.user)
        return OrderItem.objects.none()
