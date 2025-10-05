#!/usr/bin/env python3
"""
Test OTP API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8001"

def test_otp_endpoints():
    """Test OTP API endpoints"""
    
    print("🧪 Testing OTP API Endpoints")
    print("=" * 40)
    
    phone_number = "+919876543210"
    
    try:
        # Test 1: Send OTP
        print("\n1. Testing Send OTP endpoint...")
        
        send_data = {
            "phone_number": phone_number,
            "purpose": "registration"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/otp/send",
            json=send_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            send_result = response.json()
            print(f"✅ Send OTP Success:")
            print(f"   Message: {send_result['message']}")
            print(f"   OTP Code: {send_result.get('otp_code', 'Hidden')}")
            
            otp_code = send_result.get('otp_code', '123456')
            
            # Test 2: Register with OTP
            print("\n2. Testing Register with OTP endpoint...")
            
            register_data = {
                "phone_number": phone_number,
                "otp_code": otp_code,
                "name": "Test User",
                "user_type": "donor",
                "blood_group": "O+",
                "email": "test@example.com",
                "age": 25,
                "gender": "male",
                "weight": 70.0
            }
            
            register_response = requests.post(
                f"{BASE_URL}/api/v1/auth/otp/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {register_response.status_code}")
            
            if register_response.status_code == 200:
                register_result = register_response.json()
                print(f"✅ Registration Success:")
                print(f"   Message: {register_result['message']}")
                print(f"   User ID: {register_result['user']['id']}")
                print(f"   Access Token: {register_result['access_token'][:20]}...")
                
                # Test 3: Send OTP for login
                print("\n3. Testing Send OTP for login...")
                
                login_send_data = {
                    "phone_number": phone_number,
                    "purpose": "login"
                }
                
                login_send_response = requests.post(
                    f"{BASE_URL}/api/v1/auth/otp/send",
                    json=login_send_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_send_response.status_code == 200:
                    login_send_result = login_send_response.json()
                    login_otp = login_send_result.get('otp_code', '123456')
                    
                    # Test 4: Login with OTP
                    print("\n4. Testing Login with OTP endpoint...")
                    
                    login_data = {
                        "phone_number": phone_number,
                        "otp_code": login_otp,
                        "purpose": "login"
                    }
                    
                    login_response = requests.post(
                        f"{BASE_URL}/api/v1/auth/otp/verify",
                        json=login_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"Status Code: {login_response.status_code}")
                    
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        print(f"✅ Login Success:")
                        print(f"   Message: {login_result['message']}")
                        print(f"   User: {login_result['user']['name']}")
                        print(f"   Access Token: {login_result['access_token'][:20]}...")
                    else:
                        print(f"❌ Login failed: {login_response.text}")
                else:
                    print(f"❌ Login OTP send failed: {login_send_response.text}")
            else:
                print(f"❌ Registration failed: {register_response.text}")
        else:
            print(f"❌ Send OTP failed: {response.text}")
        
        print("\n✅ OTP API endpoint testing completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_otp_endpoints()
    print(f"\nTest Result: {'PASSED' if success else 'FAILED'}")