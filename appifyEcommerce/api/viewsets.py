from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from decimal import Decimal

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from products.models import Product
from accounts.permissions import IsAdmin, IsCustomer, IsOwnerOrAdmin, IsAuthenticatedOrReadOnly
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PlaceOrderSerializer,
    ProductSerializer,
)

User = get_user_model()


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


@extend_schema_view(
    list=extend_schema(
        summary="List Cart Items",
        description="Retrieve a list of cart items for the authenticated user. Admin users can see all cart items.",
        tags=["Cart"],
        responses={200: CartItemSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Add Item to Cart",
        description="Add a product to the cart with stock validation and reservation. If the product already exists in the cart, the quantity will be increased.",
        tags=["Cart"],
        request=CartItemSerializer,
        responses={
            201: CartItemSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Add to Cart",
                value={"product": 1, "quantity": 2},
                request_only=True,
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get Cart Item",
        description="Retrieve a specific cart item by ID. Users can only access their own cart items.",
        tags=["Cart"],
        responses={200: CartItemSerializer},
    ),
    update=extend_schema(
        summary="Update Cart Item",
        description="Update the quantity of a cart item with stock validation and automatic stock adjustment.",
        tags=["Cart"],
        request=CartItemSerializer,
        responses={
            200: CartItemSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Update Quantity",
                value={"quantity": 3},
                request_only=True,
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Partially Update Cart Item",
        description="Partially update cart item quantity with stock validation.",
        tags=["Cart"],
        request=CartItemSerializer,
        responses={200: CartItemSerializer},
    ),
    destroy=extend_schema(
        summary="Remove Cart Item",
        description="Remove an item from the cart and release the reserved stock back to available inventory.",
        tags=["Cart"],
        responses={
            204: None,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cart items with automatic stock management.
    
    This ViewSet handles all cart item operations including:
    - Adding items to cart with stock reservation
    - Updating quantities with stock adjustment
    - Removing items with stock release
    - Preventing overselling through stock validation
    - Atomic operations to prevent race conditions
    
    Features:
    - Automatic cart creation for authenticated users
    - Stock reservation on item addition
    - Stock release on item removal
    - Quantity validation and stock checking
    - Concurrency control with database locking
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsCustomer | IsAdmin]
    
    def get_queryset(self):
        """
        Filter cart items based on user role.
        
        Returns:
            QuerySet: Filtered cart items
        """
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return CartItem.objects.all()
            return CartItem.objects.filter(cart__user=self.request.user)
        return CartItem.objects.none()

    def get_cart(self):
        """
        Get or create cart for current user.
        
        Returns:
            Cart: User's cart instance
        """
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart
        return None

    def perform_create(self, serializer):
        """
        Create cart item with stock reservation.
        
        This method handles:
        - Product stock validation
        - Stock reservation using atomic transactions
        - Cart creation if it doesn't exist
        - Handling existing cart items (quantity increase)
        
        Args:
            serializer: CartItemSerializer instance
            
        Raises:
            ValidationError: If insufficient stock or user not authenticated
        """
        with transaction.atomic():
            # Lock product to prevent race conditions
            product = serializer.validated_data['product']
            locked_product = Product.objects.select_for_update().get(id=product.id)
            
            # Validate stock availability
            quantity = serializer.validated_data['quantity']
            if not locked_product.is_in_stock(quantity):
                raise ValidationError(f"Insufficient stock. Only {locked_product.available_stock} available.")
            
            # Get or create cart
            cart = self.get_cart()
            if not cart:
                raise ValidationError("User must be authenticated to add items to cart")
            
            # Check if item already exists in cart
            existing_item = CartItem.objects.filter(cart=cart, product=locked_product).first()
            if existing_item:
                # Update existing item
                new_quantity = existing_item.quantity + quantity
                if not locked_product.is_in_stock(new_quantity):
                    raise ValidationError(f"Insufficient stock. Only {locked_product.available_stock} available.")
                
                locked_product.reserve_stock(quantity)
                existing_item.quantity = new_quantity
                existing_item.save()
                serializer.instance = existing_item
            else:
                # Create new item
                locked_product.reserve_stock(quantity)
                serializer.save(cart=cart)

    def perform_update(self, serializer):
        """
        Update cart item with stock adjustment.
        
        This method handles:
        - Stock reservation for quantity increases
        - Stock release for quantity decreases
        - Atomic operations to prevent race conditions
        
        Args:
            serializer: CartItemSerializer instance
            
        Raises:
            ValidationError: If insufficient stock for quantity increase
        """
        with transaction.atomic():
            instance = self.get_object()
            product = instance.product
            locked_product = Product.objects.select_for_update().get(id=product.id)
            
            old_quantity = instance.quantity
            new_quantity = serializer.validated_data.get('quantity', old_quantity)
            quantity_diff = new_quantity - old_quantity

            if quantity_diff != 0:
                if quantity_diff > 0:
                    # Adding more items
                    if not locked_product.is_in_stock(quantity_diff):
                        raise ValidationError(f"Insufficient stock. Only {locked_product.available_stock} available.")
                    locked_product.reserve_stock(quantity_diff)
                else:
                    # Removing items
                    locked_product.release_stock(abs(quantity_diff))

            serializer.save()

    def perform_destroy(self, instance):
        """
        Delete cart item and release reserved stock.
        
        This method:
        - Releases all reserved stock back to available inventory
        - Uses atomic transaction for data integrity
        - Prevents stock inconsistencies
        
        Args:
            instance: CartItem instance to delete
        """
        with transaction.atomic():
            product = instance.product
            locked_product = Product.objects.select_for_update().get(id=product.id)
            
            # Release reserved stock
            locked_product.release_stock(instance.quantity)
            instance.delete()


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

    def create(self, request, *args, **kwargs):
        return Response(
            {
                'success': False,
                'message': 'Use the place-order endpoint to create orders.',
                'errors': {'detail': 'POST /api/orders/place-order/'}
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(
        summary="Place Order",
        description=(
            "Create an order from a list of items. Validates stock, calculates total_price on the backend, "
            "and deducts stock only if the order is successfully created. Uses transaction.atomic and row locks "
            "to prevent overselling."
        ),
        tags=["Orders"],
        request=PlaceOrderSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Place Order Example",
                value={
                    "items": [
                        {"product": 1, "quantity": 2},
                        {"product": 5, "quantity": 1}
                    ]
                },
                request_only=True,
            )
        ],
    )
    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data.get('items', [])
        if not items:
            return Response(
                {
                    'success': False,
                    'message': 'No items provided',
                    'errors': {'items': 'This field is required.'}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            locked_products = {}
            total_price = Decimal('0.00')

            for item in items:
                product = item['product']
                quantity = item['quantity']

                locked_product = Product.objects.select_for_update().get(id=product.id)
                locked_products[locked_product.id] = locked_product

                if not locked_product.is_in_stock(quantity):
                    return Response(
                        {
                            'success': False,
                            'message': 'Insufficient stock',
                            'errors': {
                                'product': locked_product.id,
                                'available_stock': locked_product.available_stock,
                                'requested_quantity': quantity,
                            },
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                total_price += (locked_product.price * quantity)

            order = Order.objects.create(user=request.user, total_price=total_price, status='pending')

            for item in items:
                locked_product = locked_products[item['product'].id]
                quantity = item['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=locked_product,
                    quantity=quantity,
                    price_at_purchase=locked_product.price,
                )

                locked_product.stock_quantity = locked_product.stock_quantity - quantity
                locked_product.save(update_fields=['stock_quantity'])

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


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
