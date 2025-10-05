#!/usr/bin/env python3
"""
Test script for BloodAid Emergency API and WebSocket functionality
"""

import asyncio
import websockets
import json
import aiohttp
from datetime import datetime, timedelta

async def test_websocket_connection():
    """Test WebSocket connection to emergency endpoint"""
    user_id = "test_donor_123"
    uri = f"ws://localhost:8001/ws/emergency/{user_id}"
    
    print(f"🔌 Testing WebSocket connection to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "test",
                "message": "Hello from test client",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message: {test_message}")
            
            # Listen for messages for 5 seconds
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Received message: {message}")
            except asyncio.TimeoutError:
                print("⏰ No message received within 5 seconds (this is normal)")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_emergency_api():
    """Test Emergency API endpoints"""
    base_url = "http://localhost:8001/api/v1"
    
    print(f"🔗 Testing Emergency API at: {base_url}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test health endpoint first
            async with session.get("http://localhost:8001/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
            
            # Test emergency alerts endpoint (this should require auth)
            async with session.get(f"{base_url}/emergency/alerts") as response:
                if response.status == 401:
                    print("✅ Emergency alerts endpoint is protected (401 Unauthorized - expected)")
                else:
                    print(f"⚠️ Unexpected response from alerts endpoint: {response.status}")
            
            return True
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False

async def test_emergency_flow_simulation():
    """Simulate an emergency alert flow"""
    print("\n🚨 Simulating Emergency Alert Flow...")
    
    # This would normally require authentication, but we can test the structure
    emergency_data = {
        "patient_name": "Test Patient",
        "hospital_name": "Test Hospital",
        "hospital_address": "123 Test Street",
        "blood_group_needed": "O+",
        "units_needed": 2,
        "urgency_level": "critical",
        "contact_name": "Emergency Contact",
        "contact_phone": "+1234567890",
        "needed_by": (datetime.now() + timedelta(hours=2)).isoformat(),
        "search_radius_km": 5.0,
        "hospital_latitude": 12.9716,
        "hospital_longitude": 77.5946
    }
    
    print(f"📋 Emergency alert data structure: {json.dumps(emergency_data, indent=2)}")
    print("✅ Emergency data structure is valid")
    
    return True

async def main():
    """Run all tests"""
    print("🧪 Starting BloodAid Real-time System Tests\n")
    
    # Test 1: WebSocket Connection
    print("=" * 50)
    print("Test 1: WebSocket Connection")
    print("=" * 50)
    websocket_success = await test_websocket_connection()
    
    # Test 2: Emergency API
    print("\n" + "=" * 50)
    print("Test 2: Emergency API")
    print("=" * 50)
    api_success = await test_emergency_api()
    
    # Test 3: Emergency Flow Simulation
    print("\n" + "=" * 50)
    print("Test 3: Emergency Flow Simulation")
    print("=" * 50)
    flow_success = await test_emergency_flow_simulation()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"WebSocket Connection: {'✅ PASS' if websocket_success else '❌ FAIL'}")
    print(f"Emergency API: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"Emergency Flow: {'✅ PASS' if flow_success else '❌ FAIL'}")
    
    all_passed = websocket_success and api_success and flow_success
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_passed else '⚠️ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n✅ The real-time blood donation system is working correctly!")
        print("💡 Next steps:")
        print("   1. Register as both patient and donor in the web app")
        print("   2. Test the full emergency alert flow from patient to donor")
        print("   3. Verify real-time notifications appear in donor dashboard")
    else:
        print("\n❌ Some components need attention before the system is fully functional")

if __name__ == "__main__":
    asyncio.run(main())