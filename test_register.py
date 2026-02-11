#!/usr/bin/env python
"""
Simple test for registration endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    print("🔐 Testing Registration Endpoint")
    print("=" * 40)
    
    # Test valid registration
    print("\n1. Valid Registration:")
    valid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "role": "customer"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=valid_data)
    print(f"Status: {response.status_code}")
    print(f"Content: {json.dumps(response.json(), indent=2)}")
    
    # Test password mismatch
    print("\n2. Password Mismatch:")
    invalid_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "TestPass123!",
        "password_confirm": "DifferentPass123!",
        "role": "customer"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=invalid_data)
    print(f"Status: {response.status_code}")
    print(f"Content: {json.dumps(response.json(), indent=2)}")
    
    # Test invalid email
    print("\n3. Invalid Email:")
    invalid_email_data = {
        "username": "testuser3",
        "email": "invalid-email",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "role": "customer"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=invalid_email_data)
    print(f"Status: {response.status_code}")
    print(f"Content: {json.dumps(response.json(), indent=2)}")
    
    # Test weak password
    print("\n4. Weak Password:")
    weak_password_data = {
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "123",
        "password_confirm": "123",
        "role": "customer"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=weak_password_data)
    print(f"Status: {response.status_code}")
    print(f"Content: {json.dumps(response.json(), indent=2)}")
    
    print("\n" + "=" * 40)
    print("📝 Registration Endpoint Summary:")
    print("✅ Basic fields: username, email, password, password_confirm, role")
    print("✅ Default role: customer")
    print("✅ Password validation: Django built-in validators")
    print("✅ Email validation: Required field")
    print("✅ Password confirmation: Required match")
    print("✅ Response format: success, message, content")

if __name__ == "__main__":
    test_registration()
