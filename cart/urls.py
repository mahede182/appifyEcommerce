from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('summary/', views.cart_summary, name='cart_summary'),
    path('checkout/', views.checkout, name='checkout'),
]
