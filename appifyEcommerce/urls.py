from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from appifyEcommerce.api.viewsets import (
    CartItemViewSet,
    CartViewSet,
    OrderItemViewSet,
    OrderViewSet,
    ProductViewSet,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
