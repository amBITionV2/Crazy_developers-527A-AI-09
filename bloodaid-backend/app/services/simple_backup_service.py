"""
Simple Backup Service without Web Scraping Dependencies
Provides mock backup data for testing and demonstration
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class SimpleMockBackupService:
    """Simple backup service with mock data (no web scraping dependencies)"""
    
    def __init__(self):
        self.last_updated = None
        self.cache_duration = timedelta(hours=2)
        self.is_updating = False
        
        # Mock data for demonstration
        self.mock_blood_banks = [
            {
                "id": "mock_bank_1",
                "name": "🏥 AIIMS Delhi Blood Bank",
                "address": "AIIMS, Ansari Nagar, New Delhi, Delhi 110029",
                "contact": "+91-11-26588500",
                "email": "bloodbank@aiims.edu",
                "city": "New Delhi",
                "state": "Delhi",
                "latitude": 28.5672,
                "longitude": 77.2100,
                "is_government": True,
                "source": "eraktkosh_mock",
                "available_blood_groups": ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
            },
            {
                "id": "mock_bank_2", 
                "name": "🏥 Fortis Hospital Blood Center",
                "address": "Fortis Hospital, Vasant Kunj, New Delhi",
                "contact": "+91-11-42778800",
                "email": "blood@fortis.in",
                "city": "New Delhi",
                "state": "Delhi",
                "latitude": 28.5244,
                "longitude": 77.1855,
                "is_government": False,
                "source": "eraktkosh_mock",
                "available_blood_groups": ["O+", "A+", "B+", "AB+"]
            },
            {
                "id": "mock_bank_3",
                "name": "🏥 Max Hospital Blood Bank",
                "address": "Max Hospital, Saket, New Delhi",
                "contact": "+91-11-26515050",
                "email": "bloodbank@maxhealthcare.com",
                "city": "New Delhi", 
                "state": "Delhi",
                "latitude": 28.5355,
                "longitude": 77.2030,
                "is_government": False,
                "source": "eraktkosh_mock",
                "available_blood_groups": ["O+", "O-", "A+", "B+"]
            }
        ]
        
        self.mock_availability = [
            {
                "id": "mock_avail_1",
                "blood_bank_name": "AIIMS Delhi Blood Bank",
                "blood_group": "O+",
                "units_available": 25,
                "contact": "+91-11-26588500",
                "address": "AIIMS, New Delhi",
                "city": "New Delhi",
                "state": "Delhi",
                "source": "eraktkosh_mock",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "mock_avail_2",
                "blood_bank_name": "Fortis Hospital Blood Center",
                "blood_group": "A+",
                "units_available": 18,
                "contact": "+91-11-42778800",
                "address": "Fortis Hospital, Vasant Kunj",
                "city": "New Delhi",
                "state": "Delhi",
                "source": "eraktkosh_mock",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "mock_avail_3",
                "blood_bank_name": "Max Hospital Blood Bank",
                "blood_group": "B+",
                "units_available": 12,
                "contact": "+91-11-26515050",
                "address": "Max Hospital, Saket",
                "city": "New Delhi",
                "state": "Delhi",
                "source": "eraktkosh_mock",
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        self.mock_donors = [
            {
                "id": "mock_donor_1",
                "name": "🏥 Blood Bank: AIIMS Delhi",
                "blood_group": "O+",
                "phone": "+91-11-26588500",
                "email": "bloodbank@aiims.edu",
                "address": "AIIMS, Ansari Nagar, New Delhi",
                "city": "New Delhi",
                "state": "Delhi",
                "latitude": 28.5672,
                "longitude": 77.2100,
                "is_available": True,
                "is_blood_bank": True,
                "source": "eraktkosh_mock"
            },
            {
                "id": "mock_donor_2",
                "name": "🏥 Blood Bank: Fortis Hospital",
                "blood_group": "A+",
                "phone": "+91-11-42778800",
                "email": "blood@fortis.in",
                "address": "Fortis Hospital, Vasant Kunj",
                "city": "New Delhi",
                "state": "Delhi",
                "latitude": 28.5244,
                "longitude": 77.1855,
                "is_available": True,
                "is_blood_bank": True,
                "source": "eraktkosh_mock"
            }
        ]
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_updated:
            return False
        return datetime.now() - self.last_updated < self.cache_duration
    
    async def update_cached_data(self, force: bool = False) -> bool:
        """Mock update of cached data"""
        try:
            if self.is_updating:
                logger.info("Update already in progress, skipping...")
                return False
            
            if not force and self._is_cache_valid():
                logger.info("Mock cache is still valid, skipping update")
                return True
            
            self.is_updating = True
            logger.info("Starting mock backup data update...")
            
            # Simulate update delay
            await asyncio.sleep(0.1)
            
            # Update timestamps
            current_time = datetime.now().isoformat()
            for item in self.mock_availability:
                item["last_updated"] = current_time
            
            self.last_updated = datetime.now()
            self.is_updating = False
            
            logger.info("Mock backup data update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in mock update: {str(e)}")
            self.is_updating = False
            return False
    
    def get_cached_donors(self, blood_group: str = None, location: str = None, limit: int = 50) -> List[Dict]:
        """Get cached donor data"""
        try:
            filtered_donors = self.mock_donors.copy()
            
            if blood_group:
                filtered_donors = [d for d in filtered_donors if d["blood_group"] == blood_group]
            
            if location:
                location_lower = location.lower()
                filtered_donors = [
                    d for d in filtered_donors 
                    if (location_lower in d["address"].lower() or 
                        location_lower in d["city"].lower() or 
                        location_lower in d["state"].lower())
                ]
            
            return filtered_donors[:limit]
            
        except Exception as e:
            logger.error(f"Error getting cached donors: {str(e)}")
            return []
    
    def get_cached_blood_banks(self, location: str = None, limit: int = 50) -> List[Dict]:
        """Get cached blood bank data"""
        try:
            filtered_banks = self.mock_blood_banks.copy()
            
            if location:
                location_lower = location.lower()
                filtered_banks = [
                    b for b in filtered_banks 
                    if (location_lower in b["address"].lower() or 
                        location_lower in b["city"].lower() or 
                        location_lower in b["state"].lower() or
                        location_lower in b["name"].lower())
                ]
            
            return filtered_banks[:limit]
            
        except Exception as e:
            logger.error(f"Error getting cached blood banks: {str(e)}")
            return []
    
    def get_cached_availability(self, blood_group: str = None, location: str = None, limit: int = 50) -> List[Dict]:
        """Get cached blood availability data"""
        try:
            filtered_availability = self.mock_availability.copy()
            
            if blood_group:
                filtered_availability = [a for a in filtered_availability if a["blood_group"] == blood_group]
            
            if location:
                location_lower = location.lower()
                filtered_availability = [
                    a for a in filtered_availability 
                    if (location_lower in a["address"].lower() or 
                        location_lower in a["city"].lower() or 
                        location_lower in a["state"].lower() or
                        location_lower in a["blood_bank_name"].lower())
                ]
            
            return filtered_availability[:limit]
            
        except Exception as e:
            logger.error(f"Error getting cached availability: {str(e)}")
            return []
    
    def get_cache_health(self) -> Dict[str, Any]:
        """Get cache health metrics"""
        try:
            return {
                "service": "eraktkosh_mock_backup",
                "status": "healthy" if self._is_cache_valid() else "stale",
                "last_update": self.last_updated.isoformat() if self.last_updated else None,
                "is_updating": self.is_updating,
                "cache_expired": not self._is_cache_valid(),
                "current_counts": {
                    "blood_banks": len(self.mock_blood_banks),
                    "availability_records": len(self.mock_availability),
                    "donors": len(self.mock_donors)
                },
                "note": "This is a mock backup service for demonstration"
            }
            
        except Exception as e:
            return {
                "service": "eraktkosh_mock_backup",
                "status": "error",
                "error": str(e)
            }

# Global mock service instance
mock_backup_service = SimpleMockBackupService()

async def get_mock_backup_service() -> SimpleMockBackupService:
    """Get the global mock backup service instance"""
    return mock_backup_service