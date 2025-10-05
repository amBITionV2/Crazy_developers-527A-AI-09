#!/usr/bin/env python3
"""
Test OTP functionality
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import engine
from app.services.otp_service import otp_service
from app.models.otp import OTP

# Create a test session
SessionLocal = sessionmaker(bind=engine)

async def test_otp_functionality():
    """Test OTP creation and verification"""
    
    print("🧪 Testing OTP Functionality")
    print("=" * 40)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test 1: Create OTP
        print("\n1. Creating OTP...")
        phone_number = "+919876543210"
        
        otp_data = otp_service.create_otp(
            db=db,
            phone_number=phone_number,
            purpose="login"
        )
        
        print(f"✅ OTP Created:")
        print(f"   Phone: {phone_number}")
        print(f"   OTP Code: {otp_data['otp_code']}")
        print(f"   Expires: {otp_data['expires_at']}")
        
        # Test 2: Send OTP (mock)
        print("\n2. Sending OTP...")
        sms_result = otp_service.send_otp_sms(
            phone_number=phone_number,
            otp_code=otp_data['otp_code']
        )
        
        print(f"✅ SMS Result:")
        print(f"   Success: {sms_result['success']}")
        print(f"   Message: {sms_result['message']}")
        print(f"   Mock: {sms_result.get('mock', False)}")
        
        # Test 3: Verify OTP (correct)
        print("\n3. Verifying OTP (correct)...")
        verify_result = otp_service.verify_otp(
            db=db,
            phone_number=phone_number,
            otp_code=otp_data['otp_code'],
            purpose="login"
        )
        
        print(f"✅ Verification Result:")
        print(f"   Success: {verify_result['success']}")
        print(f"   Message: {verify_result['message']}")
        
        # Test 4: Create another OTP for wrong verification test
        print("\n4. Creating new OTP for incorrect test...")
        otp_data2 = otp_service.create_otp(
            db=db,
            phone_number=phone_number,
            purpose="registration"
        )
        
        # Test 5: Verify OTP (incorrect)
        print("\n5. Verifying OTP (incorrect)...")
        wrong_verify_result = otp_service.verify_otp(
            db=db,
            phone_number=phone_number,
            otp_code="000000",  # Wrong OTP
            purpose="registration"
        )
        
        print(f"❌ Wrong Verification Result:")
        print(f"   Success: {wrong_verify_result['success']}")
        print(f"   Message: {wrong_verify_result['message']}")
        
        # Test 6: Check database records
        print("\n6. Checking database records...")
        otp_records = db.query(OTP).filter(OTP.phone_number == phone_number).all()
        print(f"📊 Found {len(otp_records)} OTP records in database")
        
        for i, record in enumerate(otp_records, 1):
            print(f"   Record {i}:")
            print(f"     Code: {record.otp_code}")
            print(f"     Purpose: {record.purpose}")
            print(f"     Verified: {record.is_verified}")
            print(f"     Expired: {record.is_expired}")
            print(f"     Attempts: {record.attempts}")
        
        print("\n✅ OTP functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_otp_functionality())
    sys.exit(0 if success else 1)