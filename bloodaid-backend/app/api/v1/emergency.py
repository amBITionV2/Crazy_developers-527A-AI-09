from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.config.database import get_db
from app.core.dependencies import get_current_user, get_current_patient
from app.models.user import User
from app.models.emergency_alert import EmergencyAlert, UrgencyLevel, AlertStatus
from app.models.donation import Donation
from app.services.backup_service import get_backup_service, with_backup_fallback

# Import WebSocket manager for real-time notifications
from app.websockets.manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emergency", tags=["Emergency"])

# Create WebSocket manager instance
ws_manager = ConnectionManager()

# Schemas
class SOSAlertCreate(BaseModel):
    patient_name: str
    hospital_name: str
    hospital_address: Optional[str] = None
    blood_group_needed: str
    units_needed: int = 1
    urgency_level: UrgencyLevel
    contact_name: str
    contact_phone: str
    emergency_contact_phone: Optional[str] = None
    medical_condition: Optional[str] = None
    special_requirements: Optional[str] = None
    hospital_latitude: Optional[float] = None
    hospital_longitude: Optional[float] = None
    search_radius_km: float = 5.0
    needed_by: datetime

class EmergencyResponse(BaseModel):
    alert_id: str
    response: str  # "accept" or "decline"
    message: Optional[str] = None

class SOSResponse(BaseModel):
    success: bool
    alert_id: str
    message: str
    donors_found: List[dict]
    search_radius: str

@router.post("/sos-alert", response_model=SOSResponse)
async def create_sos_alert(
    alert_data: SOSAlertCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create emergency SOS alert with backup donor search"""
    
    # Create emergency alert
    expires_at = alert_data.needed_by + timedelta(hours=2)  # Alert expires 2 hours after needed time
    
    emergency_alert = EmergencyAlert(
        patient_id=current_user.id,
        patient_name=alert_data.patient_name,
        hospital_name=alert_data.hospital_name,
        hospital_address=alert_data.hospital_address,
        blood_group_needed=alert_data.blood_group_needed,
        units_needed=alert_data.units_needed,
        urgency_level=alert_data.urgency_level,
        needed_by=alert_data.needed_by,
        expires_at=expires_at,
        hospital_latitude=alert_data.hospital_latitude,
        hospital_longitude=alert_data.hospital_longitude,
        search_radius_km=alert_data.search_radius_km,
        contact_name=alert_data.contact_name,
        contact_phone=alert_data.contact_phone,
        emergency_contact_phone=alert_data.emergency_contact_phone,
        medical_condition=alert_data.medical_condition,
        special_requirements=alert_data.special_requirements,
        status=AlertStatus.ACTIVE
    )
    
    db.add(emergency_alert)
    db.commit()
    db.refresh(emergency_alert)
    
    # Find nearby donors with backup fallback
    async def get_primary_emergency_donors():
        """Get donors from primary database for emergency"""
        try:
            # Query donors from database
            from app.models.donor import Donor
            
            query = db.query(Donor).join(User).filter(
                User.blood_group == alert_data.blood_group_needed,
                User.is_available == True
            )
            
            donors = query.limit(50).all()
            
            nearby_donors = []
            for donor in donors:
                if donor.user:
                    # Calculate distance if coordinates available
                    distance = "Unknown"
                    if (alert_data.hospital_latitude and alert_data.hospital_longitude and 
                        donor.user.latitude and donor.user.longitude):
                        lat_diff = abs(float(donor.user.latitude) - alert_data.hospital_latitude)
                        lon_diff = abs(float(donor.user.longitude) - alert_data.hospital_longitude)
                        approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                        
                        if approx_distance <= alert_data.search_radius_km:
                            distance = f"{approx_distance:.1f} km"
                        else:
                            continue  # Skip donors outside radius
                    
                    donor_info = {
                        "id": str(donor.id),
                        "name": donor.user.name,
                        "distance": distance,
                        "area": donor.user.city or "Unknown",
                        "bloodGroup": donor.user.blood_group,
                        "phone": donor.user.phone,
                        "isAvailable": donor.user.is_available,
                        "source": "primary_db",
                        "total_donations": donor.total_donations or 0
                    }
                    nearby_donors.append(donor_info)
            
            # Sort by distance if available
            def sort_key(donor):
                if donor["distance"] == "Unknown":
                    return 999
                return float(donor["distance"].split()[0])
            
            nearby_donors.sort(key=sort_key)
            return nearby_donors
            
        except Exception as e:
            logger.error(f"Error getting primary emergency donors: {str(e)}")
            return []
    
    async def get_backup_emergency_donors():
        """Get donors from backup service for emergency"""
        try:
            backup_service = await get_backup_service()
            
            # Get backup donors and blood banks
            backup_donors = await backup_service.get_backup_donors(
                blood_group=alert_data.blood_group_needed
            )
            
            # Also get blood banks as potential donors
            backup_blood_banks = await backup_service.get_backup_blood_banks()
            
            combined_donors = []
            
            # Process backup donors
            for donor in backup_donors:
                # Calculate distance if coordinates available
                distance = "Unknown"
                if (alert_data.hospital_latitude and alert_data.hospital_longitude and 
                    donor.get("latitude") and donor.get("longitude")):
                    try:
                        lat_diff = abs(float(donor["latitude"]) - alert_data.hospital_latitude)
                        lon_diff = abs(float(donor["longitude"]) - alert_data.hospital_longitude)
                        approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                        
                        if approx_distance <= alert_data.search_radius_km:
                            distance = f"{approx_distance:.1f} km"
                        else:
                            continue  # Skip donors outside radius
                    except:
                        pass
                
                donor_info = {
                    "id": donor.get("id", "backup_donor"),
                    "name": donor.get("name", "Backup Donor"),
                    "distance": distance,
                    "area": donor.get("city", "Unknown"),
                    "bloodGroup": alert_data.blood_group_needed,
                    "phone": donor.get("phone", ""),
                    "isAvailable": True,
                    "source": "eraktkosh_backup",
                    "is_blood_bank": donor.get("is_blood_bank", False)
                }
                combined_donors.append(donor_info)
            
            # Process blood banks as potential sources
            for bank in backup_blood_banks:
                available_groups = bank.get("available_blood_groups", [])
                if alert_data.blood_group_needed in available_groups:
                    # Calculate distance
                    distance = "Unknown"
                    if (alert_data.hospital_latitude and alert_data.hospital_longitude and 
                        bank.get("latitude") and bank.get("longitude")):
                        try:
                            lat_diff = abs(float(bank["latitude"]) - alert_data.hospital_latitude)
                            lon_diff = abs(float(bank["longitude"]) - alert_data.hospital_longitude)
                            approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
                            
                            if approx_distance <= alert_data.search_radius_km:
                                distance = f"{approx_distance:.1f} km"
                            else:
                                continue
                        except:
                            pass
                    
                    bank_info = {
                        "id": bank.get("id", "backup_bank"),
                        "name": f"🏥 {bank.get('name', 'Blood Bank')}",
                        "distance": distance,
                        "area": bank.get("city", "Unknown"),
                        "bloodGroup": alert_data.blood_group_needed,
                        "phone": bank.get("contact", ""),
                        "isAvailable": True,
                        "source": "eraktkosh_backup",
                        "is_blood_bank": True,
                        "is_government": bank.get("is_government", False)
                    }
                    combined_donors.append(bank_info)
            
            # Sort by distance and prioritize blood banks for emergencies
            def sort_key(donor):
                distance_val = 999
                if donor["distance"] != "Unknown":
                    distance_val = float(donor["distance"].split()[0])
                
                # Prioritize blood banks (lower value = higher priority)
                priority = 0 if donor.get("is_blood_bank") else 1
                return (priority, distance_val)
            
            combined_donors.sort(key=sort_key)
            return combined_donors
            
        except Exception as e:
            logger.error(f"Error getting backup emergency donors: {str(e)}")
            return []
    
    # Use fallback mechanism for finding donors
    try:
        nearby_donors = await with_backup_fallback(
            get_primary_emergency_donors,
            get_backup_emergency_donors
        )
        
        # Update alert with donor count
        emergency_alert.donors_notified = len(nearby_donors)
        db.commit()
        
        # Send real-time notifications to donors via WebSocket
        try:
            alert_notification = {
                "id": str(emergency_alert.id),
                "patient_name": emergency_alert.patient_name,
                "hospital_name": emergency_alert.hospital_name,
                "blood_group": emergency_alert.blood_group_needed,
                "units_needed": emergency_alert.units_needed,
                "urgency_level": emergency_alert.urgency_level.value,
                "needed_by": emergency_alert.needed_by.isoformat(),
                "contact_phone": emergency_alert.contact_phone,
                "medical_condition": emergency_alert.medical_condition,
                "hospital_latitude": emergency_alert.hospital_latitude,
                "hospital_longitude": emergency_alert.hospital_longitude,
                "search_radius_km": emergency_alert.search_radius_km,
                "created_at": emergency_alert.created_at.isoformat()
            }
            
            # Get donor IDs from nearby donors
            donor_ids = []
            for donor in nearby_donors:
                if donor.get("id") and donor.get("source") == "primary_db":
                    donor_ids.append(donor["id"])
            
            # Send emergency alert to connected donors
            if donor_ids:
                await ws_manager.send_emergency_alert(alert_notification, donor_ids)
                logger.info(f"🚨 Real-time notifications sent to {len(donor_ids)} connected donors")
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket notifications: {str(e)}")
        
        # TODO: Send SMS/Push notifications
        
        response_message = f"SOS alert created successfully. {len(nearby_donors)} donors/blood banks notified."
        if any(d.get("source") == "eraktkosh_backup" for d in nearby_donors):
            response_message += " (Includes backup sources from eRaktKosh)"
        
        return SOSResponse(
            success=True,
            alert_id=str(emergency_alert.id),
            message=response_message,
            donors_found=nearby_donors,
            search_radius=f"{alert_data.search_radius_km} km"
        )
        
    except Exception as e:
        logger.error(f"Error in create_sos_alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create SOS alert")

@router.get("/blood-availability")
async def get_emergency_blood_availability(
    blood_group: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: float = 10.0,
    db: Session = Depends(get_db)
):
    """Get blood availability for emergency with backup data"""
    
    async def get_primary_availability():
        """Get availability from primary sources"""
        # This would query your main blood bank/inventory database
        # For now, return empty to demonstrate fallback
        return []
    
    async def get_backup_availability():
        """Get availability from backup service"""
        try:
            backup_service = await get_backup_service()
            
            availability = await backup_service.get_backup_blood_availability(
                blood_group=blood_group
            )
            
            # Filter by location if coordinates provided
            if latitude and longitude:
                filtered_availability = []
                for item in availability:
                    # Simple distance calculation would be needed here
                    # For now, include all items
                    filtered_availability.append(item)
                availability = filtered_availability
            
            return availability
            
        except Exception as e:
            logger.error(f"Error getting backup availability: {str(e)}")
            return []
    
    try:
        availability = await with_backup_fallback(
            get_primary_availability,
            get_backup_availability
        )
        
        return {
            "success": True,
            "blood_group": blood_group,
            "availability": availability,
            "total_sources": len(availability),
            "search_criteria": {
                "blood_group": blood_group,
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_emergency_blood_availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get blood availability")

@router.post("/respond")
async def respond_to_emergency(
    response_data: EmergencyResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Donor response to emergency alert"""
    
    # Get emergency alert
    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.id == response_data.alert_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Emergency alert not found")
    
    if alert.status != AlertStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Alert is no longer active")
    
    # Record response
    if response_data.response == "accept":
        alert.donors_responded += 1
        alert.status = AlertStatus.RESPONDING
        
        # Create donation record
        donation = Donation(
            donor_id=current_user.id,
            patient_id=alert.patient_id,
            emergency_alert_id=alert.id,
            blood_group=alert.blood_group_needed,
            units_requested=alert.units_needed,
            scheduled_datetime=alert.needed_by,
            hospital_name=alert.hospital_name,
            hospital_address=alert.hospital_address,
            hospital_contact=alert.contact_phone,
            is_emergency=True,
            request_message=response_data.message
        )
        db.add(donation)
        
        if not alert.first_response_time:
            alert.first_response_time = datetime.utcnow()
        
        message = "Emergency request accepted successfully"
        
        # Send real-time notification to patient about donor response
        try:
            response_notification = {
                "donor_id": str(current_user.id),
                "donor_name": current_user.name,
                "donor_phone": current_user.phone,
                "donor_blood_group": current_user.blood_group,
                "response": "accepted",
                "message": response_data.message,
                "alert_id": str(alert.id),
                "responded_at": datetime.utcnow().isoformat()
            }
            
            await ws_manager.send_response_notification(response_notification, str(alert.patient_id))
            logger.info(f"📬 Response notification sent to patient {alert.patient_id}")
            
        except Exception as e:
            logger.error(f"Failed to send response notification: {str(e)}")
            
    else:
        message = "Response recorded"
    
    db.commit()
    
    return {
        "success": True,
        "message": message,
        "alert_status": alert.status
    }

@router.get("/alerts")
async def get_emergency_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active emergency alerts for donors"""
    
    # Get active alerts that match donor's blood group or universal recipients
    compatible_blood_groups = []
    user_blood = current_user.blood_group
    
    # Blood compatibility logic
    if user_blood == "O-":
        compatible_blood_groups = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
    elif user_blood == "O+":
        compatible_blood_groups = ["O+", "A+", "B+", "AB+"]
    elif user_blood == "A-":
        compatible_blood_groups = ["A-", "A+", "AB-", "AB+"]
    elif user_blood == "A+":
        compatible_blood_groups = ["A+", "AB+"]
    elif user_blood == "B-":
        compatible_blood_groups = ["B-", "B+", "AB-", "AB+"]
    elif user_blood == "B+":
        compatible_blood_groups = ["B+", "AB+"]
    elif user_blood == "AB-":
        compatible_blood_groups = ["AB-", "AB+"]
    elif user_blood == "AB+":
        compatible_blood_groups = ["AB+"]
    
    alerts = db.query(EmergencyAlert).filter(
        EmergencyAlert.status == AlertStatus.ACTIVE,
        EmergencyAlert.blood_group_needed.in_(compatible_blood_groups),
        EmergencyAlert.expires_at > datetime.utcnow()
    ).order_by(EmergencyAlert.urgency_level, EmergencyAlert.created_at).all()
    
    alert_list = []
    for alert in alerts:
        alert_list.append({
            "id": str(alert.id),
            "patient_name": alert.patient_name,
            "hospital_name": alert.hospital_name,
            "blood_group": alert.blood_group_needed,
            "units_needed": alert.units_needed,
            "urgency_level": alert.urgency_level,
            "needed_by": alert.needed_by.isoformat(),
            "contact_phone": alert.contact_phone,
            "medical_condition": alert.medical_condition,
            "created_at": alert.created_at.isoformat()
        })
    
    return {
        "success": True,
        "alerts": alert_list
    }