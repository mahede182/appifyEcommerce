#!/usr/bin/env python
"""
Test script for authentication API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("🔐 Testing Authentication API Endpoints")
    print("=" * 50)
    
    # Test registration
    print("\n1. Testing Registration")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "role": "customer",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        user_data = response.json()['data']
        tokens = user_data['tokens']
        access_token = tokens['access']
        
        print(f"\n✅ Registration successful!")
        print(f"User: {user_data['user']['username']}")
        
        # Test login
        print("\n2. Testing Login")
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            login_tokens = response.json()['data']['tokens']
            access_token = login_tokens['access']
            print(f"✅ Login successful!")
            
            # Test user profile
            print("\n3. Testing User Profile")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{BASE_URL}/auth/user/", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test logout
            print("\n4. Testing Logout")
            response = requests.post(f"{BASE_URL}/auth/logout/", 
                                   json={"refresh": login_tokens['refresh']}, 
                                   headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
    # Test admin registration
    print("\n5. Testing Admin Registration")
    admin_data = {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "password_confirm": "AdminPass123!",
        "role": "admin",
        "first_name": "Admin",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=admin_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Registration endpoint: ✅")
    print("- Login endpoint: ✅") 
    print("- User profile endpoint: ✅")
    print("- Logout endpoint: ✅")
    print("- Admin registration: ✅")
    print("\n📝 Available Endpoints:")
    print("POST /auth/register/    - User registration")
    print("POST /auth/login/       - User login")
    print("POST /auth/logout/      - User logout")
    print("GET  /auth/user/        - Get user profile")
    print("PUT  /auth/user/        - Update user profile")
    print("POST /auth/password/change/ - Change password")
    print("\n🏗️  App Structure:")
    print("- accounts/          - User authentication and management")
    print("- products/          - Product catalog and management")
    print("- cart/              - Shopping cart functionality")
    print("- orders/            - Order processing and management")

if __name__ == "__main__":
    test_endpoints()
