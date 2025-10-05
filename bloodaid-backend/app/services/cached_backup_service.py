"""
Enhanced Backup Service with Database Caching
Provides persistent storage for backup data with fast retrieval
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import hashlib
import logging

from app.services.eraktkosh_scraper import ERaktKoshScraper, BloodBankInfo, BloodAvailability
from app.services.data_validator import get_validator
from app.config.database import get_db
from app.models.backup_cache import (
    BackupBloodBank, BackupBloodAvailability, BackupDonor, BackupDataMetrics
)

logger = logging.getLogger(__name__)

class CachedBackupService:
    """Enhanced backup service with database caching"""
    
    def __init__(self):
        self.scraper = None
        self.cache_duration = timedelta(hours=2)
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
    
    def _generate_external_id(self, data: Dict, prefix: str = "") -> str:
        """Generate consistent external ID for data item"""
        # Create a hash based on key fields
        key_data = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(key_data.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    def _is_cache_expired(self, db: Session) -> bool:
        """Check if cache needs refresh"""
        try:
            latest_metric = db.query(BackupDataMetrics).filter(
                BackupDataMetrics.update_successful == True
            ).order_by(desc(BackupDataMetrics.date)).first()
            
            if not latest_metric:
                return True
            
            return datetime.utcnow() - latest_metric.date > self.cache_duration
            
        except Exception as e:
            logger.error(f"Error checking cache expiry: {str(e)}")
            return True
    
    async def update_cached_data(self, force: bool = False) -> bool:
        """Update cached backup data with database persistence"""
        if self.is_updating:
            logger.info("Update already in progress, skipping...")
            return False
        
        db = next(get_db())
        
        try:
            # Check if update is needed
            if not force and not self._is_cache_expired(db):
                logger.info("Cache is still fresh, skipping update")
                return True
            
            self.is_updating = True
            start_time = datetime.utcnow()
            
            logger.info("Starting cached backup data update...")
            
            await self._ensure_scraper()
            validator = get_validator()
            
            # Initialize metrics
            metrics = BackupDataMetrics(
                date=start_time,
                source="eraktkosh"
            )
            
            scraping_start = datetime.utcnow()
            
            # Scrape blood availability data
            raw_availability = await self.scraper.get_all_blood_availability()
            logger.info(f"Scraped {len(raw_availability)} availability records")
            
            # Scrape blood bank data  
            raw_blood_banks = await self.scraper.get_all_blood_banks()
            logger.info(f"Scraped {len(raw_blood_banks)} blood bank records")
            
            scraping_duration = (datetime.utcnow() - scraping_start).total_seconds()
            metrics.scraping_duration_seconds = scraping_duration
            
            # Validate and process blood banks
            validation_start = datetime.utcnow()
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
            
            valid_blood_banks, invalid_blood_banks, bank_stats = validator.validate_batch(
                blood_bank_dicts, "blood_bank"
            )
            
            # Validate and process availability data
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
            
            valid_availability, invalid_availability, avail_stats = validator.validate_batch(
                availability_dicts, "blood_availability"
            )
            
            validation_duration = (datetime.utcnow() - validation_start).total_seconds()
            metrics.validation_duration_seconds = validation_duration
            
            # Store validated data in database
            await self._store_blood_banks(db, valid_blood_banks)
            await self._store_availability(db, valid_availability)
            await self._generate_donor_data(db, valid_blood_banks, valid_availability)
            
            # Update metrics
            metrics.total_blood_banks = len(valid_blood_banks)
            metrics.blood_banks_valid = bank_stats["valid"]
            metrics.blood_banks_invalid = bank_stats["invalid"]
            metrics.total_availability_records = len(valid_availability)
            metrics.availability_valid = avail_stats["valid"]
            metrics.availability_invalid = avail_stats["invalid"]
            metrics.total_duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            metrics.update_successful = True
            
            db.add(metrics)
            db.commit()
            
            self.is_updating = False
            
            logger.info(f"Cached backup data update completed successfully in "
                       f"{metrics.total_duration_seconds:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error in update_cached_data: {str(e)}")
            
            # Record failed metrics
            try:
                metrics.update_successful = False
                metrics.error_message = str(e)
                metrics.total_duration_seconds = (datetime.utcnow() - start_time).total_seconds()
                db.add(metrics)
                db.commit()
            except:
                pass
            
            self.is_updating = False
            return False
        
        finally:
            db.close()
    
    async def _store_blood_banks(self, db: Session, blood_banks: List[Dict]):
        """Store blood bank data in database"""
        try:
            # Mark all existing records as inactive
            db.query(BackupBloodBank).filter(
                BackupBloodBank.source == "eraktkosh"
            ).update({"is_active": False})
            
            for bank_data in blood_banks:
                external_id = self._generate_external_id(bank_data, "bank")
                
                # Check if record exists
                existing = db.query(BackupBloodBank).filter(
                    BackupBloodBank.external_id == external_id
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in bank_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.is_active = True
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new record
                    new_bank = BackupBloodBank(
                        external_id=external_id,
                        name=bank_data.get("name", ""),
                        address=bank_data.get("address", ""),
                        contact=bank_data.get("contact", ""),
                        email=bank_data.get("email", ""),
                        city=bank_data.get("district", ""),
                        state=bank_data.get("state", ""),
                        district=bank_data.get("district", ""),
                        latitude=bank_data.get("latitude"),
                        longitude=bank_data.get("longitude"),
                        is_government=bank_data.get("is_government", False),
                        validated_at=datetime.fromisoformat(bank_data["validated_at"]) if "validated_at" in bank_data else None,
                        validation_source=bank_data.get("validation_source"),
                        is_active=True
                    )
                    db.add(new_bank)
            
            db.commit()
            logger.info(f"Stored {len(blood_banks)} blood banks in cache")
            
        except Exception as e:
            logger.error(f"Error storing blood banks: {str(e)}")
            db.rollback()
    
    async def _store_availability(self, db: Session, availability_data: List[Dict]):
        """Store availability data in database"""
        try:
            # Mark all existing records as inactive
            db.query(BackupBloodAvailability).filter(
                BackupBloodAvailability.source == "eraktkosh"
            ).update({"is_active": False})
            
            for avail_data in availability_data:
                external_id = self._generate_external_id(avail_data, "avail")
                
                # Check if record exists
                existing = db.query(BackupBloodAvailability).filter(
                    BackupBloodAvailability.external_id == external_id
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in avail_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.is_active = True
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new record
                    new_avail = BackupBloodAvailability(
                        external_id=external_id,
                        blood_bank_name=avail_data.get("blood_bank_name", ""),
                        blood_group=avail_data.get("blood_group", ""),
                        units_available=avail_data.get("units_available", 0),
                        contact=avail_data.get("contact", ""),
                        address=avail_data.get("address", ""),
                        city=avail_data.get("district", ""),
                        state=avail_data.get("state", ""),
                        district=avail_data.get("district", ""),
                        validated_at=datetime.fromisoformat(avail_data["validated_at"]) if "validated_at" in avail_data else None,
                        validation_source=avail_data.get("validation_source"),
                        is_active=True
                    )
                    db.add(new_avail)
            
            db.commit()
            logger.info(f"Stored {len(availability_data)} availability records in cache")
            
        except Exception as e:
            logger.error(f"Error storing availability data: {str(e)}")
            db.rollback()
    
    async def _generate_donor_data(self, db: Session, blood_banks: List[Dict], availability: List[Dict]):
        """Generate synthetic donor data from blood banks"""
        try:
            # Mark all existing donor records as inactive
            db.query(BackupDonor).filter(
                BackupDonor.source == "eraktkosh"
            ).update({"is_active": False})
            
            validator = get_validator()
            donors_created = 0
            
            for bank_data in blood_banks:
                # Create donor entry for each blood bank
                donor_data = {
                    "name": f"Blood Bank: {bank_data.get('name', 'Unknown')}",
                    "blood_group": "O+",  # Default
                    "phone": bank_data.get("contact", ""),
                    "email": bank_data.get("email", ""),
                    "address": bank_data.get("address", ""),
                    "city": bank_data.get("district", ""),
                    "state": bank_data.get("state", ""),
                    "latitude": bank_data.get("latitude"),
                    "longitude": bank_data.get("longitude"),
                    "is_available": True,
                    "is_blood_bank": True
                }
                
                # Validate donor data
                result = validator.validate_donor_data(donor_data)
                if result.is_valid:
                    external_id = self._generate_external_id(result.cleaned_data, "donor")
                    
                    # Check if exists
                    existing = db.query(BackupDonor).filter(
                        BackupDonor.external_id == external_id
                    ).first()
                    
                    if existing:
                        # Update existing
                        for key, value in result.cleaned_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.is_active = True
                        existing.last_updated = datetime.utcnow()
                    else:
                        # Create new
                        new_donor = BackupDonor(
                            external_id=external_id,
                            name=result.cleaned_data.get("name", ""),
                            blood_group=result.cleaned_data.get("blood_group", "O+"),
                            phone=result.cleaned_data.get("phone", ""),
                            email=result.cleaned_data.get("email", ""),
                            address=result.cleaned_data.get("address", ""),
                            city=result.cleaned_data.get("city", ""),
                            state=result.cleaned_data.get("state", ""),
                            latitude=result.cleaned_data.get("latitude"),
                            longitude=result.cleaned_data.get("longitude"),
                            is_available=True,
                            is_blood_bank=True,
                            validated_at=datetime.fromisoformat(result.cleaned_data["validated_at"]) if "validated_at" in result.cleaned_data else None,
                            validation_source=result.cleaned_data.get("validation_source"),
                            is_active=True
                        )
                        db.add(new_donor)
                        donors_created += 1
            
            db.commit()
            logger.info(f"Generated {donors_created} donor records from blood banks")
            
        except Exception as e:
            logger.error(f"Error generating donor data: {str(e)}")
            db.rollback()
    
    def get_cached_donors(self, blood_group: str = None, location: str = None, limit: int = 50) -> List[Dict]:
        """Get cached donor data"""
        db = next(get_db())
        
        try:
            query = db.query(BackupDonor).filter(BackupDonor.is_active == True)
            
            if blood_group:
                query = query.filter(BackupDonor.blood_group == blood_group)
            
            if location:
                location_lower = location.lower()
                query = query.filter(
                    or_(
                        BackupDonor.address.ilike(f"%{location}%"),
                        BackupDonor.city.ilike(f"%{location}%"),
                        BackupDonor.state.ilike(f"%{location}%")
                    )
                )
            
            donors = query.limit(limit).all()
            
            return [
                {
                    "id": donor.external_id,
                    "name": donor.name,
                    "blood_group": donor.blood_group,
                    "phone": donor.phone,
                    "email": donor.email,
                    "address": donor.address,
                    "city": donor.city,
                    "state": donor.state,
                    "latitude": donor.latitude,
                    "longitude": donor.longitude,
                    "is_available": donor.is_available,
                    "is_blood_bank": donor.is_blood_bank,
                    "source": "eraktkosh_cached",
                    "last_updated": donor.last_updated.isoformat() if donor.last_updated else None
                }
                for donor in donors
            ]
            
        except Exception as e:
            logger.error(f"Error getting cached donors: {str(e)}")
            return []
        finally:
            db.close()
    
    def get_cached_blood_banks(self, location: str = None, limit: int = 50) -> List[Dict]:
        """Get cached blood bank data"""
        db = next(get_db())
        
        try:
            query = db.query(BackupBloodBank).filter(BackupBloodBank.is_active == True)
            
            if location:
                location_lower = location.lower()
                query = query.filter(
                    or_(
                        BackupBloodBank.address.ilike(f"%{location}%"),
                        BackupBloodBank.city.ilike(f"%{location}%"),
                        BackupBloodBank.state.ilike(f"%{location}%"),
                        BackupBloodBank.name.ilike(f"%{location}%")
                    )
                )
            
            banks = query.limit(limit).all()
            
            return [
                {
                    "id": bank.external_id,
                    "name": bank.name,
                    "address": bank.address,
                    "contact": bank.contact,
                    "email": bank.email,
                    "city": bank.city,
                    "state": bank.state,
                    "district": bank.district,
                    "latitude": bank.latitude,
                    "longitude": bank.longitude,
                    "is_government": bank.is_government,
                    "source": "eraktkosh_cached",
                    "last_updated": bank.last_updated.isoformat() if bank.last_updated else None
                }
                for bank in banks
            ]
            
        except Exception as e:
            logger.error(f"Error getting cached blood banks: {str(e)}")
            return []
        finally:
            db.close()
    
    def get_cached_availability(self, blood_group: str = None, location: str = None, limit: int = 50) -> List[Dict]:
        """Get cached blood availability data"""
        db = next(get_db())
        
        try:
            query = db.query(BackupBloodAvailability).filter(
                BackupBloodAvailability.is_active == True,
                BackupBloodAvailability.units_available > 0
            )
            
            if blood_group:
                query = query.filter(BackupBloodAvailability.blood_group == blood_group)
            
            if location:
                location_lower = location.lower()
                query = query.filter(
                    or_(
                        BackupBloodAvailability.address.ilike(f"%{location}%"),
                        BackupBloodAvailability.city.ilike(f"%{location}%"),
                        BackupBloodAvailability.state.ilike(f"%{location}%"),
                        BackupBloodAvailability.blood_bank_name.ilike(f"%{location}%")
                    )
                )
            
            availability = query.order_by(desc(BackupBloodAvailability.units_available)).limit(limit).all()
            
            return [
                {
                    "id": avail.external_id,
                    "blood_bank_name": avail.blood_bank_name,
                    "blood_group": avail.blood_group,
                    "units_available": avail.units_available,
                    "contact": avail.contact,
                    "address": avail.address,
                    "city": avail.city,
                    "state": avail.state,
                    "district": avail.district,
                    "source": "eraktkosh_cached",
                    "last_updated": avail.last_updated.isoformat() if avail.last_updated else None
                }
                for avail in availability
            ]
            
        except Exception as e:
            logger.error(f"Error getting cached availability: {str(e)}")
            return []
        finally:
            db.close()
    
    def get_cache_health(self) -> Dict[str, Any]:
        """Get cache health metrics"""
        db = next(get_db())
        
        try:
            # Get latest metrics
            latest_metric = db.query(BackupDataMetrics).filter(
                BackupDataMetrics.update_successful == True
            ).order_by(desc(BackupDataMetrics.date)).first()
            
            # Get current counts
            blood_banks_count = db.query(BackupBloodBank).filter(BackupBloodBank.is_active == True).count()
            availability_count = db.query(BackupBloodAvailability).filter(BackupBloodAvailability.is_active == True).count()
            donors_count = db.query(BackupDonor).filter(BackupDonor.is_active == True).count()
            
            health_data = {
                "service": "eraktkosh_cached_backup",
                "status": "healthy" if latest_metric and not self._is_cache_expired(db) else "stale",
                "is_updating": self.is_updating,
                "cache_expired": self._is_cache_expired(db),
                "current_counts": {
                    "blood_banks": blood_banks_count,
                    "availability_records": availability_count,
                    "donors": donors_count
                }
            }
            
            if latest_metric:
                health_data.update({
                    "last_update": latest_metric.date.isoformat(),
                    "last_update_duration": latest_metric.total_duration_seconds,
                    "validation_stats": {
                        "blood_banks_valid": latest_metric.blood_banks_valid,
                        "blood_banks_invalid": latest_metric.blood_banks_invalid,
                        "availability_valid": latest_metric.availability_valid,
                        "availability_invalid": latest_metric.availability_invalid
                    }
                })
            
            return health_data
            
        except Exception as e:
            return {
                "service": "eraktkosh_cached_backup",
                "status": "error",
                "error": str(e)
            }
        finally:
            db.close()

# Global cached service instance
cached_backup_service = CachedBackupService()

async def get_cached_backup_service() -> CachedBackupService:
    """Get the global cached backup service instance"""
    return cached_backup_service