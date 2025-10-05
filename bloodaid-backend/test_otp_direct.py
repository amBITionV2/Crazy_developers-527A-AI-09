#!/usr/bin/env python3
"""
Direct test of OTP endpoints using FastAPI TestClient
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def test_otp_endpoints_direct():
    """Test OTP endpoints using FastAPI TestClient"""
    
    print("🧪 Testing OTP Endpoints with TestClient")
    print("=" * 50)
    
    client = TestClient(app)
    phone_number = "+919876543210"
    
    try:
        # Test 1: Send OTP
        print("\n1. Testing Send OTP...")
        
        send_response = client.post(
            "/api/v1/auth/otp/send",
            json={
                "phone_number": phone_number,
                "purpose": "registration"
            }
        )
        
        print(f"Status: {send_response.status_code}")
        
        if send_response.status_code == 200:
            send_data = send_response.json()
            print(f"✅ Send OTP Success:")
            print(f"   Message: {send_data['message']}")
            print(f"   OTP Code: {send_data.get('otp_code', 'Hidden')}")
            
            otp_code = send_data.get('otp_code', '123456')
            
            # Test 2: Register with OTP
            print("\n2. Testing Registration with OTP...")
            
            register_response = client.post(
                "/api/v1/auth/otp/register",
                json={
                    "phone_number": phone_number,
                    "otp_code": otp_code,
                    "name": "Test User",
                    "user_type": "donor",
                    "blood_group": "O+",
                    "email": "testuser@example.com",
                    "age": 25,
                    "gender": "male",
                    "weight": 70.0
                }
            )
            
            print(f"Status: {register_response.status_code}")
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                print(f"✅ Registration Success:")
                print(f"   Message: {register_data['message']}")
                print(f"   User: {register_data['user']['name']}")
                print(f"   Phone: {register_data['user']['phone']}")
                print(f"   Type: {register_data['user']['user_type']}")
                print(f"   Blood Group: {register_data['user']['blood_group']}")
                print(f"   Access Token: {register_data['access_token'][:30]}...")
                
                # Test 3: Send OTP for login
                print("\n3. Testing Send OTP for Login...")
                
                login_send_response = client.post(
                    "/api/v1/auth/otp/send",
                    json={
                        "phone_number": phone_number,
                        "purpose": "login"
                    }
                )
                
                if login_send_response.status_code == 200:
                    login_send_data = login_send_response.json()
                    login_otp = login_send_data.get('otp_code', '123456')
                    
                    # Test 4: Verify OTP for login
                    print("\n4. Testing OTP Login...")
                    
                    login_response = client.post(
                        "/api/v1/auth/otp/verify",
                        json={
                            "phone_number": phone_number,
                            "otp_code": login_otp,
                            "purpose": "login"
                        }
                    )
                    
                    print(f"Status: {login_response.status_code}")
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        print(f"✅ Login Success:")
                        print(f"   Message: {login_data['message']}")
                        print(f"   User: {login_data['user']['name']}")
                        print(f"   Access Token: {login_data['access_token'][:30]}...")
                    else:
                        print(f"❌ Login failed: {login_response.text}")
                else:
                    print(f"❌ Login OTP send failed: {login_send_response.text}")
            else:
                print(f"❌ Registration failed: {register_response.text}")
                print(f"Response data: {register_response.json()}")
        else:
            print(f"❌ Send OTP failed: {send_response.text}")
        
        # Test 5: Check available endpoints
        print("\n5. Checking Available Endpoints...")
        
        docs_response = client.get("/docs")
        print(f"Docs Status: {docs_response.status_code}")
        
        health_response = client.get("/health")
        print(f"Health Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health Data: {health_response.json()}")
        
        print("\n✅ OTP Testing Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_otp_endpoints_direct()
    print(f"\nOverall Result: {'SUCCESS' if success else 'FAILED'}")