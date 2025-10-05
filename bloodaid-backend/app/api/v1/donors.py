from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.config.database import get_db
from app.core.dependencies import get_current_donor
from app.models.user import User
from app.models.donor import Donor
from app.services.backup_service import get_backup_service, with_backup_fallback
from app.services.cached_backup_service import get_cached_backup_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/donors", tags=["Donors"])

@router.get("/profile")
async def get_donor_profile(
    current_user: User = Depends(get_current_donor),
    db: Session = Depends(get_db)
):
    """Get donor profile"""
    try:
        # Get detailed donor information
        donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
        
        profile_data = {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "blood_group": current_user.blood_group,
            "address": current_user.address,
            "city": current_user.city,
            "state": current_user.state,
            "is_available": current_user.is_available,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
        
        if donor:
            profile_data.update({
                "total_donations": donor.total_donations or 0,
                "last_donation": donor.last_donation.isoformat() if donor.last_donation else None,
                "medical_conditions": donor.medical_conditions,
                "emergency_contact": donor.emergency_contact,
                "preferred_donation_time": donor.preferred_donation_time
            })
        
        return profile_data
        
    except Exception as e:
        logger.error(f"Error getting donor profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get donor profile")

@router.get("/nearby")
async def get_nearby_donors(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    radius: float = Query(5.0, description="Search radius in kilometers"),
    blood_group: Optional[str] = Query(None, description="Required blood group"),
    limit: int = Query(20, description="Maximum number of donors to return"),
    db: Session = Depends(get_db)
):
    """Get nearby donors with backup fallback"""
    
    async def get_primary_donors():
        """Get donors from primary database"""
        try:
            query = db.query(Donor).join(User)
            
            if blood_group:
                query = query.filter(User.blood_group == blood_group)
            
            # Filter for available donors
            query = query.filter(User.is_available == True)
            
            # In a real implementation, you would use geospatial queries
            # For now, we'll get all and filter/sort by distance
            donors = query.limit(limit * 2).all()  # Get more to filter by distance
            
            donor_list = []
            for donor in donors:
                if donor.user:
                    # Calculate approximate distance (simplified)
                    # In production, use proper geospatial calculations
                    lat_diff = abs(float(donor.user.latitude or 0) - latitude) if donor.user.latitude else 999
                    lon_diff = abs(float(donor.user.longitude or 0) - longitude) if donor.user.longitude else 999
                    approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion
                    
                    if approx_distance <= radius:
                        donor_data = {
                            "id": str(donor.id),
                            "name": donor.user.name,
                            "blood_group": donor.user.blood_group,
                            "distance": f"{approx_distance:.1f} km",
                            "phone": donor.user.phone,
                            "address": donor.user.address,
                            "city": donor.user.city,
                            "state": donor.user.state,
                            "is_available": donor.user.is_available,
                            "last_donation": donor.last_donation.isoformat() if donor.last_donation else None,
                            "total_donations": donor.total_donations or 0,
                            "source": "primary_db"
                        }
                        donor_list.append(donor_data)
            
            # Sort by distance and limit results
            donor_list.sort(key=lambda x: float(x["distance"].split()[0]))
            return donor_list[:limit]
            
        except Exception as e:
            logger.error(f"Error getting primary donors: {str(e)}")
            return []
    
    async def get_backup_donors():
        """Get donors from backup service"""
        try:
            # Use cached backup service for better performance
            cached_service = await get_cached_backup_service()
            
            # Determine location string for backup search
            location = f"{latitude},{longitude}"  # Could be enhanced with city/state lookup
            
            backup_donors = cached_service.get_cached_donors(
                blood_group=blood_group,
                location=None,  # Location filtering is limited in backup
                limit=limit
            )
            
            # Add distance calculations for backup donors
            for donor in backup_donors:
                if donor.get("latitude") and donor.get("longitude"):
                    try:
                        lat_diff = abs(float(donor["latitude"]) - latitude)
                        lon_diff = abs(float(donor["longitude"]) - longitude)
                        approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                        donor["distance"] = f"{approx_distance:.1f} km"
                    except:
                        donor["distance"] = "Unknown"
                else:
                    donor["distance"] = "Unknown"
            
            # Filter by radius and sort
            filtered_donors = [d for d in backup_donors if d.get("distance", "999") != "Unknown" and float(d["distance"].split()[0]) <= radius]
            filtered_donors.sort(key=lambda x: float(x["distance"].split()[0]) if x["distance"] != "Unknown" else 999)
            
            return filtered_donors[:limit]
            
        except Exception as e:
            logger.error(f"Error getting backup donors: {str(e)}")
            return []
    
    # Use fallback mechanism
    try:
        donors = await with_backup_fallback(
            get_primary_donors,
            get_backup_donors
        )
        
        return {
            "donors": donors,
            "total": len(donors),
            "search_criteria": {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
                "blood_group": blood_group
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_nearby_donors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get nearby donors")

@router.get("/search")
async def search_donors(
    blood_group: Optional[str] = Query(None, description="Blood group to search for"),
    city: Optional[str] = Query(None, description="City to search in"),
    state: Optional[str] = Query(None, description="State to search in"),
    available_only: bool = Query(True, description="Only show available donors"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search donors with backup fallback"""
    
    async def get_primary_search_results():
        """Search in primary database"""
        try:
            query = db.query(Donor).join(User)
            
            if blood_group:
                query = query.filter(User.blood_group == blood_group)
            
            if city:
                query = query.filter(User.city.ilike(f"%{city}%"))
            
            if state:
                query = query.filter(User.state.ilike(f"%{state}%"))
            
            if available_only:
                query = query.filter(User.is_available == True)
            
            donors = query.limit(limit).all()
            
            return [
                {
                    "id": str(donor.id),
                    "name": donor.user.name,
                    "blood_group": donor.user.blood_group,
                    "phone": donor.user.phone,
                    "address": donor.user.address,
                    "city": donor.user.city,
                    "state": donor.user.state,
                    "is_available": donor.user.is_available,
                    "last_donation": donor.last_donation.isoformat() if donor.last_donation else None,
                    "total_donations": donor.total_donations or 0,
                    "source": "primary_db"
                }
                for donor in donors if donor.user
            ]
            
        except Exception as e:
            logger.error(f"Error in primary search: {str(e)}")
            return []
    
    async def get_backup_search_results():
        """Search in backup data"""
        try:
            backup_service = await get_backup_service()
            
            # Create location string from city/state
            location = None
            if city or state:
                location_parts = [part for part in [city, state] if part]
                location = " ".join(location_parts)
            
            backup_donors = await backup_service.get_backup_donors(
                blood_group=blood_group,
                location=location
            )
            
            return backup_donors[:limit]
            
        except Exception as e:
            logger.error(f"Error in backup search: {str(e)}")
            return []
    
    try:
        donors = await with_backup_fallback(
            get_primary_search_results,
            get_backup_search_results
        )
        
        return {
            "donors": donors,
            "total": len(donors),
            "search_criteria": {
                "blood_group": blood_group,
                "city": city,
                "state": state,
                "available_only": available_only
            }
        }
        
    except Exception as e:
        logger.error(f"Error in search_donors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search donors")

@router.get("/blood-banks")
async def get_blood_banks(
    city: Optional[str] = Query(None, description="City to search in"),
    state: Optional[str] = Query(None, description="State to search in"),
    blood_group: Optional[str] = Query(None, description="Check availability for blood group"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get blood banks with backup fallback"""
    
    async def get_primary_blood_banks():
        """Get blood banks from primary sources"""
        # This would typically query a blood_banks table or external API
        # For now, return empty to demonstrate fallback
        logger.info("Primary blood banks API not implemented, using fallback")
        return []
    
    async def get_backup_blood_banks():
        """Get blood banks from backup service"""
        try:
            backup_service = await get_backup_service()
            
            # Create location string
            location = None
            if city or state:
                location_parts = [part for part in [city, state] if part]
                location = " ".join(location_parts)
            
            blood_banks = await backup_service.get_backup_blood_banks(location=location)
            
            # Filter by blood group availability if specified
            if blood_group:
                filtered_banks = []
                for bank in blood_banks:
                    available_groups = bank.get("available_blood_groups", [])
                    if blood_group in available_groups:
                        filtered_banks.append(bank)
                blood_banks = filtered_banks
            
            return blood_banks[:limit]
            
        except Exception as e:
            logger.error(f"Error getting backup blood banks: {str(e)}")
            return []
    
    try:
        blood_banks = await with_backup_fallback(
            get_primary_blood_banks,
            get_backup_blood_banks
        )
        
        return {
            "blood_banks": blood_banks,
            "total": len(blood_banks),
            "search_criteria": {
                "city": city,
                "state": state,
                "blood_group": blood_group
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_blood_banks: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get blood banks")

@router.get("/backup-status")
async def get_backup_status():
    """Get status of backup service"""
    try:
        backup_service = await get_backup_service()
        status = await backup_service.health_check()
        return status
    except Exception as e:
        logger.error(f"Error getting backup status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get backup status")