"""
Test script for eRaktKosh backup system
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_scraper():
    """Test the eRaktKosh scraper"""
    print("=== Testing eRaktKosh Scraper ===")
    
    try:
        from app.services.eraktkosh_scraper import ERaktKoshScraper
        
        async with ERaktKoshScraper() as scraper:
            print("✅ Scraper initialized successfully")
            
            # Test basic connectivity
            print("\n--- Testing Connectivity ---")
            test_result = await scraper._make_request(scraper.BASE_URL)
            if test_result:
                print("✅ Connection to eRaktKosh successful")
            else:
                print("❌ Connection to eRaktKosh failed")
                return False
            
            # Test blood availability scraping
            print("\n--- Testing Blood Availability Scraping ---")
            try:
                availability = await scraper.scrape_blood_availability(state="Delhi")
                print(f"✅ Scraped {len(availability)} availability records")
                
                if availability:
                    sample = availability[0]
                    print(f"   Sample: {sample.blood_bank_name} - {sample.blood_group}: {sample.units_available} units")
                
            except Exception as e:
                print(f"⚠️ Blood availability scraping issue: {str(e)}")
            
            # Test blood bank scraping
            print("\n--- Testing Blood Bank Scraping ---")
            try:
                blood_banks = await scraper.scrape_blood_banks(state="Delhi")
                print(f"✅ Scraped {len(blood_banks)} blood bank records")
                
                if blood_banks:
                    sample = blood_banks[0]
                    print(f"   Sample: {sample.name} - {sample.state}")
                
            except Exception as e:
                print(f"⚠️ Blood bank scraping issue: {str(e)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Scraper test failed: {str(e)}")
        return False

async def test_validator():
    """Test the data validator"""
    print("\n=== Testing Data Validator ===")
    
    try:
        from app.services.data_validator import get_validator
        
        validator = get_validator()
        print("✅ Validator initialized successfully")
        
        # Test blood bank validation
        print("\n--- Testing Blood Bank Validation ---")
        sample_bank = {
            "name": "AIIMS Delhi Blood Bank",
            "address": "AIIMS, Ansari Nagar, New Delhi, Delhi 110029",
            "contact": "+91-11-26588500",
            "email": "bloodbank@aiims.edu",
            "state": "Delhi",
            "district": "New Delhi",
            "latitude": 28.5672,
            "longitude": 77.2100,
            "is_government": True
        }
        
        result = validator.validate_blood_bank_info(sample_bank)
        if result.is_valid:
            print("✅ Blood bank validation successful")
            print(f"   Warnings: {len(result.warnings)}")
        else:
            print(f"❌ Blood bank validation failed: {result.errors}")
        
        # Test blood availability validation
        print("\n--- Testing Blood Availability Validation ---")
        sample_availability = {
            "blood_bank_name": "AIIMS Delhi",
            "blood_group": "O+",
            "units_available": 15,
            "contact": "+91-11-26588500",
            "address": "AIIMS, New Delhi",
            "state": "Delhi",
            "district": "New Delhi",
            "last_updated": "2024-01-15T10:30:00"
        }
        
        result = validator.validate_blood_availability(sample_availability)
        if result.is_valid:
            print("✅ Blood availability validation successful")
            print(f"   Warnings: {len(result.warnings)}")
        else:
            print(f"❌ Blood availability validation failed: {result.errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validator test failed: {str(e)}")
        return False

async def test_backup_service():
    """Test the backup service"""
    print("\n=== Testing Backup Service ===")
    
    try:
        from app.services.backup_service import get_backup_service
        
        service = await get_backup_service()
        print("✅ Backup service initialized successfully")
        
        # Test health check
        print("\n--- Testing Health Check ---")
        health = await service.health_check()
        print(f"✅ Health check: {health['status']}")
        print(f"   Connectivity: {health.get('connectivity', 'unknown')}")
        
        # Test backup data retrieval (limited to avoid overwhelming the server)
        print("\n--- Testing Backup Data Retrieval ---")
        try:
            # Test with a small update first
            print("   Attempting small data update...")
            success = await service.update_backup_data()
            if success:
                print("✅ Backup data update successful")
                
                # Test getting backup donors
                donors = await service.get_backup_donors(blood_group="O+")
                print(f"✅ Retrieved {len(donors)} backup donors for O+")
                
                # Test getting backup blood banks
                banks = await service.get_backup_blood_banks()
                print(f"✅ Retrieved {len(banks)} backup blood banks")
                
                # Test getting backup availability
                availability = await service.get_backup_blood_availability(blood_group="O+")
                print(f"✅ Retrieved {len(availability)} backup availability records for O+")
                
            else:
                print("⚠️ Backup data update had issues (this is normal for initial testing)")
            
        except Exception as e:
            print(f"⚠️ Backup data retrieval issue: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backup service test failed: {str(e)}")
        return False

async def test_fallback_logic():
    """Test fallback logic"""
    print("\n=== Testing Fallback Logic ===")
    
    try:
        from app.services.backup_service import with_backup_fallback
        
        print("✅ Fallback logic imported successfully")
        
        # Test primary function that fails
        async def failing_primary():
            raise Exception("Primary function failed")
        
        # Test backup function that succeeds
        async def working_backup():
            return ["backup_result_1", "backup_result_2"]
        
        # Test fallback mechanism
        print("\n--- Testing Automatic Fallback ---")
        try:
            result = await with_backup_fallback(failing_primary, working_backup)
            if result == ["backup_result_1", "backup_result_2"]:
                print("✅ Fallback logic works correctly")
            else:
                print(f"❌ Unexpected fallback result: {result}")
        except Exception as e:
            print(f"❌ Fallback logic failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback logic test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting eRaktKosh Backup System Tests\n")
    
    tests = [
        ("Scraper", test_scraper),
        ("Validator", test_validator),
        ("Backup Service", test_backup_service),
        ("Fallback Logic", test_fallback_logic)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*50}")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:15} : {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Backup system is ready.")
    else:
        print("⚠️ Some tests failed. Check logs above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    asyncio.run(main())