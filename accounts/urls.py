from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user/', views.user_profile, name='user_profile'),
    path('password/change/', views.change_password, name='change_password'),
]
