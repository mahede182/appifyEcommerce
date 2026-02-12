from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import routers, serializers, viewsets
from django.core.exceptions import ValidationError

from products.models import Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock_quantity', 'available_stock']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    
    Handles cart item operations including stock validation, quantity management,
    and automatic stock reservation/release during cart operations.
    
    Fields:
        - id: Unique identifier for the cart item
        - cart: Cart the item belongs to (read-only)
        - product: Product reference
        - quantity: Number of items (must be > 0)
        - product_name: Product name (read-only)
        - product_price: Current product price (read-only)
        - available_stock: Available stock for the product (read-only)
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    available_stock = serializers.IntegerField(source='product.available_stock', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'product_name', 'product_price', 'available_stock']
        read_only_fields = ['cart']

    def validate_quantity(self, value):
        """
        Validate that quantity is greater than 0.
        
        Args:
            value: The quantity value to validate
            
        Returns:
            int: Validated quantity
            
        Raises:
            ValidationError: If quantity is less than or equal to 0
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate(self, attrs):
        """
        Validate stock availability for the requested quantity.
        
        Args:
            attrs: Dictionary of serializer fields
            
        Returns:
            dict: Validated attributes
            
        Raises:
            ValidationError: If insufficient stock is available
        """
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        
        if product and quantity:
            if not product.is_in_stock(quantity):
                raise serializers.ValidationError(
                    f"Insufficient stock. Only {product.available_stock} available for {product.name}"
                )
        
        return attrs

    def create(self, validated_data):
        """
        Create a new cart item with stock reservation.
        
        This method reserves stock for the product when adding items to cart.
        Uses atomic transaction to ensure data integrity.
        
        Args:
            validated_data: Validated cart item data
            
        Returns:
            CartItem: Created cart item instance
        """
        with transaction.atomic():
            product = validated_data['product']
            quantity = validated_data['quantity']
            
            # Reserve stock
            product.reserve_stock(quantity)
            
            # Create cart item
            cart_item = super().create(validated_data)
            return cart_item

    def update(self, instance, validated_data):
        """
        Update cart item quantity with stock adjustment.
        
        This method handles stock reservation/release when updating quantities.
        Uses atomic transaction to prevent race conditions.
        
        Args:
            instance: Existing cart item instance
            validated_data: Validated update data
            
        Returns:
            CartItem: Updated cart item instance
        """
        with transaction.atomic():
            old_quantity = instance.quantity
            new_quantity = validated_data.get('quantity', old_quantity)
            product = instance.product

            # Calculate quantity difference
            quantity_diff = new_quantity - old_quantity

            if quantity_diff != 0:
                if quantity_diff > 0:
                    # Adding more items - reserve additional stock
                    product.reserve_stock(quantity_diff)
                else:
                    # Removing items - release stock
                    product.release_stock(abs(quantity_diff))

            # Update cart item
            instance.quantity = new_quantity
            instance.save()
            return instance

    def delete(self, instance):
        """
        Delete cart item and release reserved stock.
        
        This method releases the reserved stock back to available inventory
        when a cart item is removed.
        
        Args:
            instance: Cart item to delete
        """
        with transaction.atomic():
            # Release reserved stock when cart item is deleted
            instance.product.release_stock(instance.quantity)
            super().delete(instance)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']
        read_only_fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at', 'items']
        read_only_fields = ['user', 'total_price', 'status', 'created_at', 'items']


class PlaceOrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class PlaceOrderSerializer(serializers.Serializer):
    items = PlaceOrderItemSerializer(many=True)
