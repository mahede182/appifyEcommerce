from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.contrib.auth import get_user_model
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Cart, CartItem
from orders.models import Order, OrderItem
from products.models import Product
from appifyEcommerce.api.serializers import CartSerializer, OrderSerializer

User = get_user_model()


@extend_schema(
    summary="Process Checkout",
    description="""
    Convert cart items to an order and permanently reduce product stock.
    
    This endpoint handles the complete checkout process:
    - Validates cart is not empty
    - Creates a new order with all cart items
    - Permanently reduces product stock
    - Clears the user's cart
    - Uses atomic transactions to ensure data integrity
    
    The checkout process prevents race conditions and ensures stock consistency
    by using database row locking during stock reduction operations.
    """,
    tags=["Cart"],
    responses={
        201: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "order": {"$ref": "#/components/schemas/Order"},
                        "total_price": {"type": "number"},
                        "items_count": {"type": "integer"}
                    }
                }
            }
        },
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Successful Checkout",
            value={
                "success": True,
                "message": "Order placed successfully",
                "data": {
                    "order": {"id": 1, "total_price": 199.99, "status": "pending"},
                    "total_price": 199.99,
                    "items_count": 2
                }
            },
            response_only=True,
        )
    ]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    """
    Convert cart items to order and permanently reduce stock.
    
    This endpoint processes the complete checkout flow:
    1. Validates user has a cart with items
    2. Calculates total price
    3. Creates order with order items
    4. Reduces product stock permanently
    5. Clears the cart
    
    Uses atomic transactions to ensure data integrity and prevent
    race conditions during stock operations.
    
    Returns:
        201: Order created successfully
        400: Cart empty or validation error
        401: User not authenticated
        500: Server error during checkout
    """
    try:
        with transaction.atomic():
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'No cart found',
                    'errors': {'cart': 'Cart is empty'}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get cart items
            cart_items = cart.items.all()
            if not cart_items.exists():
                return Response({
                    'success': False,
                    'message': 'Cart is empty',
                    'errors': {'cart': 'Cannot checkout with empty cart'}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total price
            total_price = Decimal('0.00')
            for item in cart_items:
                item_total = item.quantity * item.product.price
                total_price += item_total

            # Create order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='pending'
            )

            # Create order items and reduce stock
            for cart_item in cart_items:
                # Lock product for stock reduction
                product = Product.objects.select_for_update().get(id=cart_item.product.id)
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.product.price
                )
                
                # Permanently reduce stock
                product.reduce_stock(cart_item.quantity)

            # Clear cart
            cart_items.delete()

            # Return order details
            order_serializer = OrderSerializer(order)
            
            return Response({
                'success': True,
                'message': 'Order placed successfully',
                'data': {
                    'order': order_serializer.data,
                    'total_price': float(total_price),
                    'items_count': cart_items.count()
                }
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': 'Checkout failed',
            'errors': {'detail': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get Cart Summary",
    description="""
    Retrieve a comprehensive summary of the user's shopping cart.
    
    This endpoint provides detailed cart information including:
    - All cart items with product details
    - Real-time stock availability for each item
    - Individual item totals and cart total
    - Checkout eligibility based on stock availability
    
    The stock information is real-time and reflects current inventory levels,
    helping users understand if they can proceed with checkout.
    """,
    tags=["Cart"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "product": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "price": {"type": "number"},
                                            "available_stock": {"type": "integer"}
                                        }
                                    },
                                    "quantity": {"type": "integer"},
                                    "item_total": {"type": "number"},
                                    "in_stock": {"type": "boolean"}
                                }
                            }
                        },
                        "total_price": {"type": "number"},
                        "items_count": {"type": "integer"},
                        "can_checkout": {"type": "boolean"}
                    }
                }
            }
        },
        401: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Cart Summary",
            value={
                "success": True,
                "data": {
                    "items": [
                        {
                            "id": 1,
                            "product": {
                                "id": 1,
                                "name": "Laptop",
                                "price": 999.99,
                                "available_stock": 3
                            },
                            "quantity": 2,
                            "item_total": 1999.98,
                            "in_stock": True
                        }
                    ],
                    "total_price": 1999.98,
                    "items_count": 1,
                    "can_checkout": True
                }
            },
            response_only=True,
        )
    ]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cart_summary(request):
    """
    Get cart summary with stock information.
    
    This endpoint provides a detailed view of the user's cart including:
    - Product details and current stock levels
    - Item quantities and individual totals
    - Cart total and item count
    - Checkout eligibility based on stock availability
    
    The stock information is real-time and helps users understand
    if all items in their cart are still available for purchase.
    
    Returns:
        200: Cart summary retrieved successfully
        401: User not authenticated
        500: Server error during retrieval
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
        
        total_price = Decimal('0.00')
        items_data = []
        
        for item in cart_items:
            item_total = item.quantity * item.product.price
            total_price += item_total
            
            items_data.append({
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': float(item.product.price),
                    'available_stock': item.product.available_stock
                },
                'quantity': item.quantity,
                'item_total': float(item_total),
                'in_stock': item.product.is_in_stock(item.quantity)
            })
        
        return Response({
            'success': True,
            'data': {
                'items': items_data,
                'total_price': float(total_price),
                'items_count': len(items_data),
                'can_checkout': all(item['in_stock'] for item in items_data)
            }
        })
        
    except Cart.DoesNotExist:
        return Response({
            'success': True,
            'data': {
                'items': [],
                'total_price': 0.00,
                'items_count': 0,
                'can_checkout': False
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to get cart summary',
            'errors': {'detail': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
