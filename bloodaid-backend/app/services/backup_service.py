"""
Backup Service Manager for eRaktKosh Integration
Provides fallback data sources when primary APIs fail
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.services.eraktkosh_scraper import ERaktKoshScraper, BloodBankInfo, BloodAvailability
from app.services.data_validator import get_validator
from app.config.database import get_db
from app.models.donor import Donor
from app.models.emergency_alert import EmergencyAlert
import logging

logger = logging.getLogger(__name__)

class BackupDataService:
    """Service to manage backup data from eRaktKosh"""
    
    def __init__(self):
        self.scraper = None
        self.last_updated = None
        self.cache_duration = timedelta(hours=2)  # Cache for 2 hours
        self.cached_availability = []
        self.cached_blood_banks = []
        self.is_updating = False
        
    async def _ensure_scraper(self):
        """Ensure scraper is initialized"""
        if not self.scraper:
            self.scraper = ERaktKoshScraper()
            await self.scraper.__aenter__()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.scraper:
            await self.scraper.__aexit__(None, None, None)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_updated:
            return False
        return datetime.now() - self.last_updated < self.cache_duration
    
    async def update_backup_data(self, force: bool = False) -> bool:
        """Update backup data from eRaktKosh with validation"""
        try:
            # Prevent concurrent updates
            if self.is_updating:
                logger.info("Update already in progress, skipping...")
                return False
            
            # Check if cache is still valid
            if not force and self._is_cache_valid():
                logger.info("Cache is still valid, skipping update")
                return True
            
            self.is_updating = True
            logger.info("Starting backup data update from eRaktKosh...")
            
            await self._ensure_scraper()
            validator = get_validator()
            
            # Update blood availability data
            try:
                logger.info("Updating blood availability data...")
                raw_availability = await self.scraper.get_all_blood_availability()
                logger.info(f"Scraped {len(raw_availability)} raw availability records")
                
                # Convert to dict format for validation
                availability_dicts = []
                for avail in raw_availability:
                    availability_dict = {
                        "blood_bank_name": avail.blood_bank_name,
                        "blood_group": avail.blood_group,
                        "units_available": avail.units_available,
                        "last_updated": avail.last_updated.isoformat(),
                        "contact": avail.contact,
                        "address": avail.address,
                        "state": avail.state,
                        "district": avail.district
                    }
                    availability_dicts.append(availability_dict)
                
                # Validate data
                valid_availability, invalid_availability, availability_stats = validator.validate_batch(
                    availability_dicts, "blood_availability"
                )
                
                self.cached_availability = valid_availability
                logger.info(f"Validated availability data: {availability_stats['valid']} valid, "
                          f"{availability_stats['invalid']} invalid, "
                          f"{availability_stats['warnings']} warnings, "
                          f"{availability_stats['errors']} errors")
                
            except Exception as e:
                logger.error(f"Error updating blood availability: {str(e)}")
            
            # Update blood bank data
            try:
                logger.info("Updating blood bank data...")
                raw_blood_banks = await self.scraper.get_all_blood_banks()
                logger.info(f"Scraped {len(raw_blood_banks)} raw blood bank records")
                
                # Convert to dict format for validation
                blood_bank_dicts = []
                for bank in raw_blood_banks:
                    bank_dict = {
                        "name": bank.name,
                        "address": bank.address,
                        "contact": bank.contact,
                        "email": bank.email,
                        "state": bank.state,
                        "district": bank.district,
                        "latitude": bank.latitude,
                        "longitude": bank.longitude,
                        "is_government": bank.is_government
                    }
                    blood_bank_dicts.append(bank_dict)
                
                # Validate data
                valid_blood_banks, invalid_blood_banks, bank_stats = validator.validate_batch(
                    blood_bank_dicts, "blood_bank"
                )
                
                self.cached_blood_banks = valid_blood_banks
                logger.info(f"Validated blood bank data: {bank_stats['valid']} valid, "
                          f"{bank_stats['invalid']} invalid, "
                          f"{bank_stats['warnings']} warnings, "
                          f"{bank_stats['errors']} errors")
                
            except Exception as e:
                logger.error(f"Error updating blood banks: {str(e)}")
            
            self.last_updated = datetime.now()
            self.is_updating = False
            
            logger.info("Backup data update completed successfully with validation")
            return True
            
        except Exception as e:
            logger.error(f"Error in update_backup_data: {str(e)}")
            self.is_updating = False
            return False
    
    async def get_backup_donors(self, blood_group: str = None, location: str = None) -> List[Dict]:
        """Get backup donor data from eRaktKosh blood banks"""
        try:
            # Ensure we have fresh data
            await self.update_backup_data()
            
            backup_donors = []
            
            # Convert blood bank info to donor-like format
            for bank in self.cached_blood_banks:
                try:
                    # Create a synthetic donor entry based on blood bank
                    donor_data = {
                        "id": f"eraktkosh_{hash(bank.name)}",
                        "name": f"Blood Bank: {bank.name}",
                        "blood_group": blood_group or "O+",  # Default or requested
                        "phone": bank.contact,
                        "email": bank.email,
                        "address": bank.address,
                        "city": bank.district,
                        "state": bank.state,
                        "latitude": bank.latitude,
                        "longitude": bank.longitude,
                        "is_available": True,
                        "last_donation": None,
                        "source": "eraktkosh_backup",
                        "is_blood_bank": True
                    }
                    
                    # Filter by blood group if specified
                    if blood_group and blood_group not in ["Unknown"]:
                        # Check if this blood bank has availability for the requested blood group
                        has_blood_group = any(
                            avail.blood_bank_name.lower() in bank.name.lower() and 
                            avail.blood_group == blood_group and 
                            avail.units_available > 0
                            for avail in self.cached_availability
                        )
                        if not has_blood_group:
                            continue
                    
                    # Filter by location if specified
                    if location:
                        location_lower = location.lower()
                        if not (
                            location_lower in bank.address.lower() or
                            location_lower in bank.district.lower() or
                            location_lower in bank.state.lower()
                        ):
                            continue
                    
                    backup_donors.append(donor_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing blood bank {bank.name}: {str(e)}")
                    continue
            
            logger.info(f"Generated {len(backup_donors)} backup donor records")
            return backup_donors
            
        except Exception as e:
            logger.error(f"Error in get_backup_donors: {str(e)}")
            return []
    
    async def get_backup_blood_availability(self, blood_group: str = None, location: str = None) -> List[Dict]:
        """Get backup blood availability data"""
        try:
            # Ensure we have fresh data
            await self.update_backup_data()
            
            filtered_availability = []
            
            for avail in self.cached_availability:
                try:
                    # Filter by blood group if specified
                    if blood_group and avail.blood_group != blood_group:
                        continue
                    
                    # Filter by location if specified
                    if location:
                        location_lower = location.lower()
                        if not (
                            location_lower in avail.address.lower() or
                            location_lower in avail.district.lower() or
                            location_lower in avail.state.lower() or
                            location_lower in avail.blood_bank_name.lower()
                        ):
                            continue
                    
                    # Convert to API format
                    availability_data = {
                        "id": f"eraktkosh_{hash(avail.blood_bank_name + avail.blood_group)}",
                        "blood_bank_name": avail.blood_bank_name,
                        "blood_group": avail.blood_group,
                        "units_available": avail.units_available,
                        "contact": avail.contact,
                        "address": avail.address,
                        "city": avail.district,
                        "state": avail.state,
                        "last_updated": avail.last_updated.isoformat(),
                        "source": "eraktkosh_backup"
                    }
                    
                    filtered_availability.append(availability_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing availability record: {str(e)}")
                    continue
            
            logger.info(f"Returning {len(filtered_availability)} backup availability records")
            return filtered_availability
            
        except Exception as e:
            logger.error(f"Error in get_backup_blood_availability: {str(e)}")
            return []
    
    async def get_backup_blood_banks(self, location: str = None) -> List[Dict]:
        """Get backup blood bank data"""
        try:
            # Ensure we have fresh data
            await self.update_backup_data()
            
            filtered_banks = []
            
            for bank in self.cached_blood_banks:
                try:
                    # Filter by location if specified
                    if location:
                        location_lower = location.lower()
                        if not (
                            location_lower in bank.address.lower() or
                            location_lower in bank.district.lower() or
                            location_lower in bank.state.lower() or
                            location_lower in bank.name.lower()
                        ):
                            continue
                    
                    # Convert to API format
                    bank_data = {
                        "id": f"eraktkosh_{hash(bank.name)}",
                        "name": bank.name,
                        "address": bank.address,
                        "contact": bank.contact,
                        "email": bank.email,
                        "city": bank.district,
                        "state": bank.state,
                        "latitude": bank.latitude,
                        "longitude": bank.longitude,
                        "is_government": bank.is_government,
                        "source": "eraktkosh_backup",
                        "available_blood_groups": self._get_available_blood_groups_for_bank(bank.name)
                    }
                    
                    filtered_banks.append(bank_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing blood bank {bank.name}: {str(e)}")
                    continue
            
            logger.info(f"Returning {len(filtered_banks)} backup blood bank records")
            return filtered_banks
            
        except Exception as e:
            logger.error(f"Error in get_backup_blood_banks: {str(e)}")
            return []
    
    def _get_available_blood_groups_for_bank(self, bank_name: str) -> List[str]:
        """Get available blood groups for a specific bank"""
        blood_groups = []
        
        for avail in self.cached_availability:
            if (avail.blood_bank_name.lower() in bank_name.lower() or 
                bank_name.lower() in avail.blood_bank_name.lower()):
                if avail.blood_group not in blood_groups and avail.units_available > 0:
                    blood_groups.append(avail.blood_group)
        
        return blood_groups
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of backup service"""
        try:
            await self._ensure_scraper()
            
            status = {
                "service": "eraktkosh_backup",
                "status": "healthy",
                "last_updated": self.last_updated.isoformat() if self.last_updated else None,
                "cache_valid": self._is_cache_valid(),
                "cached_availability_count": len(self.cached_availability),
                "cached_blood_banks_count": len(self.cached_blood_banks),
                "is_updating": self.is_updating
            }
            
            # Test connectivity
            try:
                test_result = await self.scraper._make_request(self.scraper.BASE_URL)
                status["connectivity"] = "ok" if test_result else "failed"
            except Exception as e:
                status["connectivity"] = f"failed: {str(e)}"
                status["status"] = "degraded"
            
            return status
            
        except Exception as e:
            return {
                "service": "eraktkosh_backup",
                "status": "error",
                "error": str(e)
            }

# Global instance
backup_service = BackupDataService()

async def get_backup_service() -> BackupDataService:
    """Get the global backup service instance"""
    return backup_service

# Utility function for API fallback
async def with_backup_fallback(primary_func, backup_func, *args, **kwargs):
    """Execute primary function with automatic fallback to backup"""
    try:
        # Try primary function first
        result = await primary_func(*args, **kwargs)
        
        # If result is empty or None, try backup
        if not result or (isinstance(result, list) and len(result) == 0):
            logger.info("Primary function returned empty result, trying backup...")
            backup_result = await backup_func(*args, **kwargs)
            return backup_result
        
        return result
        
    except Exception as e:
        logger.error(f"Primary function failed: {str(e)}, trying backup...")
        
        try:
            backup_result = await backup_func(*args, **kwargs)
            return backup_result
        except Exception as backup_e:
            logger.error(f"Backup function also failed: {str(backup_e)}")
            raise e  # Raise original error

# Background task to keep backup data fresh
async def start_backup_refresh_task():
    """Start background task to refresh backup data periodically"""
    service = await get_backup_service()
    
    while True:
        try:
            await service.update_backup_data()
            # Wait 2 hours before next update
            await asyncio.sleep(2 * 60 * 60)  # 2 hours
        except Exception as e:
            logger.error(f"Error in backup refresh task: {str(e)}")
            # Wait 30 minutes before retry on error
            await asyncio.sleep(30 * 60)  # 30 minutes