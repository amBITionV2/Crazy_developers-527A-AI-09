"""
Emergency SOS API with eRaktkosh Integration
Provides real-time emergency blood search using official eRaktkosh portal data.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
from loguru import logger

from app.services.eraktkosh_service import ERaktkoshService, search_emergency_blood
from app.core.dependencies import get_current_user
from app.models.emergency_alert import EmergencyAlert
from app.config.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/emergency", tags=["Emergency SOS"])

class EmergencySOSRequest(BaseModel):
    """Emergency SOS request with patient details."""
    patient_name: str = Field(..., description="Patient name")
    blood_group: str = Field(..., description="Required blood group (A+, B+, O+, AB+, A-, B-, O-, AB-)")
    blood_component: str = Field(default="Whole Blood", description="Blood component needed")
    urgency_level: str = Field(..., description="Urgency level (CRITICAL, HIGH, MEDIUM)")
    state: str = Field(..., description="Patient's state")
    district: str = Field(..., description="Patient's district")
    hospital_name: str = Field(..., description="Hospital name")
    hospital_address: str = Field(..., description="Hospital address")
    contact_number: str = Field(..., description="Emergency contact number")
    units_needed: int = Field(default=1, description="Number of blood units needed")
    additional_info: Optional[str] = Field(None, description="Additional medical information")
    patient_age: Optional[int] = Field(None, description="Patient age")
    medical_condition: Optional[str] = Field(None, description="Medical condition requiring blood")

class EmergencySOSResponse(BaseModel):
    """Emergency SOS response with eRaktkosh data."""
    sos_id: str
    status: str
    message: str
    timestamp: datetime
    eraktkosh_data: Dict[str, Any]
    local_donors: List[Dict[str, Any]]
    emergency_actions: List[str]

@router.post("/sos-alert", response_model=EmergencySOSResponse)
async def create_emergency_sos_alert(
    request: EmergencySOSRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create emergency SOS alert with real-time eRaktkosh data integration.
    
    This endpoint:
    1. Searches real-time blood availability from eRaktkosh portal
    2. Finds nearby blood banks and centers
    3. Gets upcoming donation camps
    4. Alerts local donors in our database
    5. Provides comprehensive emergency response
    """
    try:
        logger.info(f"Emergency SOS alert created for {request.blood_group} in {request.district}, {request.state}")
        
        # Generate unique SOS ID
        sos_id = f"SOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.blood_group}"
        
        # Search eRaktkosh portal for real-time data
        eraktkosh_data = await search_emergency_blood(
            blood_group=request.blood_group,
            state=request.state,
            district=request.district,
            urgency_level=request.urgency_level
        )
        
        # Search local donors in parallel
        local_donors_task = asyncio.create_task(
            search_local_donors(db, request.blood_group, request.state, request.district)
        )
        
        # Save emergency alert to database
        from datetime import timedelta
        
        emergency_alert = EmergencyAlert(
            sos_id=sos_id,
            patient_name=request.patient_name,
            blood_group=request.blood_group,
            blood_group_needed=request.blood_group,  # Set both fields
            urgency_level=request.urgency_level,
            state=request.state,
            district=request.district,
            hospital_name=request.hospital_name,
            hospital_address=request.hospital_address,
            contact_number=request.contact_number,
            units_needed=request.units_needed,
            additional_info=request.additional_info,
            patient_age=request.patient_age,
            medical_condition=request.medical_condition,
            patient_id=current_user.id,  # Fixed: use patient_id instead of user_id
            status="ACTIVE",
            created_at=datetime.utcnow(),
            needed_by=datetime.utcnow() + timedelta(hours=24),  # Default to 24 hours
            expires_at=datetime.utcnow() + timedelta(hours=48),  # Expires in 48 hours
            eraktkosh_response=eraktkosh_data,
            special_requirements=request.blood_component  # Store blood component in special_requirements
        )
        
        db.add(emergency_alert)
        db.commit()
        db.refresh(emergency_alert)
        
        # Get local donors
        local_donors = await local_donors_task
        
        # Generate emergency actions based on data
        emergency_actions = generate_emergency_actions(
            request, eraktkosh_data, local_donors
        )
        
        # Start background notification tasks
        background_tasks.add_task(
            notify_emergency_contacts,
            sos_id,
            request,
            eraktkosh_data,
            local_donors
        )
        
        # Determine response status
        available_sources = 0
        if eraktkosh_data.get("blood_availability", {}).get("blood_banks"):
            available_sources += len(eraktkosh_data["blood_availability"]["blood_banks"])
        if local_donors:
            available_sources += len(local_donors)
        
        status = "SUCCESS" if available_sources > 0 else "LIMITED_AVAILABILITY"
        message = f"Emergency alert activated. Found {available_sources} potential blood sources."
        
        response = EmergencySOSResponse(
            sos_id=sos_id,
            status=status,
            message=message,
            timestamp=datetime.now(),
            eraktkosh_data=eraktkosh_data,
            local_donors=local_donors,
            emergency_actions=emergency_actions
        )
        
        logger.info(f"Emergency SOS alert {sos_id} created successfully with {available_sources} sources found")
        return response
        
    except Exception as e:
        logger.error(f"Failed to create emergency SOS alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create emergency alert: {str(e)}"
        )

@router.get("/sos-status/{sos_id}")
async def get_sos_status(
    sos_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current status of SOS alert."""
    try:
        alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.sos_id == sos_id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="SOS alert not found")
        
        # Refresh eRaktkosh data if alert is still active
        if alert.status == "ACTIVE":
            updated_data = await search_emergency_blood(
                blood_group=alert.blood_group,
                state=alert.state,
                district=alert.district,
                urgency_level=alert.urgency_level
            )
            
            # Update database with fresh data
            alert.eraktkosh_response = updated_data
            alert.last_updated = datetime.utcnow()
            db.commit()
        
        return {
            "sos_id": alert.sos_id,
            "status": alert.status,
            "created_at": alert.created_at,
            "last_updated": alert.last_updated,
            "patient_details": {
                "name": alert.patient_name,
                "blood_group": alert.blood_group,
                "urgency": alert.urgency_level,
                "location": f"{alert.district}, {alert.state}",
                "hospital": alert.hospital_name,
                "contact": alert.contact_number
            },
            "eraktkosh_data": alert.eraktkosh_response,
            "response_count": alert.response_count or 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get SOS status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sos-respond/{sos_id}")
async def respond_to_sos(
    sos_id: str,
    response_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Respond to SOS alert (for donors)."""
    try:
        alert = db.query(EmergencyAlert).filter(
            EmergencyAlert.sos_id == sos_id,
            EmergencyAlert.status == "ACTIVE"
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Active SOS alert not found")
        
        # Record response
        alert.response_count = (alert.response_count or 0) + 1
        
        # Add responder information
        if not alert.responders:
            alert.responders = []
        
        alert.responders.append({
            "donor_id": current_user.id,
            "donor_name": current_user.name,
            "response_time": datetime.utcnow().isoformat(),
            "availability": response_data.get("availability", "AVAILABLE"),
            "message": response_data.get("message", "")
        })
        
        db.commit()
        
        logger.info(f"SOS {sos_id} received response from donor {current_user.id}")
        
        return {
            "message": "Response recorded successfully",
            "sos_id": sos_id,
            "total_responses": alert.response_count
        }
        
    except Exception as e:
        logger.error(f"Failed to respond to SOS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blood-availability")
async def get_realtime_blood_availability(
    state: str,
    district: str,
    blood_group: str,
    current_user = Depends(get_current_user)
):
    """Get real-time blood availability from eRaktkosh portal."""
    try:
        async with ERaktkoshService() as service:
            availability = await service.search_blood_availability(
                state=state,
                district=district,
                blood_group=blood_group
            )
            
            blood_centers = await service.find_nearby_blood_centers(
                state=state,
                district=district
            )
            
            return {
                "blood_availability": availability,
                "blood_centers": blood_centers,
                "search_params": {
                    "state": state,
                    "district": district,
                    "blood_group": blood_group
                },
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to get blood availability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/donation-camps")
async def get_upcoming_donation_camps(
    state: str,
    district: str,
    current_user = Depends(get_current_user)
):
    """Get upcoming blood donation camps from eRaktkosh portal."""
    try:
        async with ERaktkoshService() as service:
            camps = await service.get_blood_donation_camps(
                state=state,
                district=district
            )
            
            return {
                "camps": camps,
                "total_camps": len(camps),
                "location": f"{district}, {state}",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to get donation camps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions

async def search_local_donors(
    db: Session, 
    blood_group: str, 
    state: str, 
    district: str
) -> List[Dict[str, Any]]:
    """Search for local donors in our database."""
    try:
        from app.models.donor import Donor
        
        # Search for compatible donors
        compatible_groups = get_compatible_donor_groups(blood_group)
        
        donors = db.query(Donor).filter(
            Donor.blood_group.in_(compatible_groups),
            Donor.state == state,
            Donor.is_available == True
        ).limit(20).all()
        
        local_donors = []
        for donor in donors:
            local_donors.append({
                "donor_id": str(donor.id),
                "name": donor.name,
                "blood_group": donor.blood_group,
                "phone": donor.phone,
                "last_donation": donor.last_donation_date.isoformat() if donor.last_donation_date else None,
                "location": f"{donor.district}, {donor.state}",
                "availability_status": "AVAILABLE"
            })
        
        return local_donors
        
    except Exception as e:
        logger.error(f"Error searching local donors: {str(e)}")
        return []

def get_compatible_donor_groups(recipient_blood_group: str) -> List[str]:
    """Get compatible donor blood groups for a recipient."""
    compatibility_map = {
        "A+": ["A+", "A-", "O+", "O-"],
        "A-": ["A-", "O-"],
        "B+": ["B+", "B-", "O+", "O-"],
        "B-": ["B-", "O-"],
        "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        "AB-": ["A-", "B-", "AB-", "O-"],
        "O+": ["O+", "O-"],
        "O-": ["O-"]
    }
    
    return compatibility_map.get(recipient_blood_group, [recipient_blood_group])

def generate_emergency_actions(
    request: EmergencySOSRequest,
    eraktkosh_data: Dict[str, Any],
    local_donors: List[Dict[str, Any]]
) -> List[str]:
    """Generate prioritized emergency actions."""
    actions = []
    
    # Immediate actions
    actions.append("🚨 IMMEDIATE: Call 108 for medical emergency assistance")
    actions.append(f"📞 URGENT: Contact hospital at {request.contact_number}")
    
    # eRaktkosh blood bank actions
    blood_banks = eraktkosh_data.get("blood_availability", {}).get("blood_banks", [])
    if blood_banks:
        actions.append(f"🏥 PRIORITY: {len(blood_banks)} blood banks have {request.blood_group} available")
        actions.append("📱 Contact blood banks immediately using eRaktkosh data")
    
    # Local donor actions  
    if local_donors:
        actions.append(f"👥 NOTIFY: {len(local_donors)} local donors in your network")
        actions.append("📲 Send emergency alerts to registered donors")
    
    # Blood center actions
    centers = eraktkosh_data.get("nearby_blood_centers", [])
    if centers:
        actions.append(f"🏢 VISIT: {len(centers)} blood centers near your location")
    
    # Camp actions
    camps = eraktkosh_data.get("upcoming_camps", [])
    if camps:
        actions.append(f"⛺ INFO: {len(camps)} donation camps upcoming in your area")
    
    # Additional actions
    actions.extend([
        "🔄 EXPAND: Search compatible blood groups if needed",
        "📍 LOCATION: Share exact hospital location with donors",
        "⏰ MONITOR: Check eRaktkosh portal every 30 minutes for updates",
        "👨‍👩‍👧‍👦 MOBILIZE: Contact family and friends for donor search"
    ])
    
    return actions

async def notify_emergency_contacts(
    sos_id: str,
    request: EmergencySOSRequest,
    eraktkosh_data: Dict[str, Any],
    local_donors: List[Dict[str, Any]]
):
    """Background task to notify emergency contacts."""
    try:
        logger.info(f"Starting emergency notifications for SOS {sos_id}")
        
        # Notify local donors via SMS/Push notifications
        for donor in local_donors:
            # TODO: Implement SMS/Push notification
            logger.info(f"Notifying donor {donor['donor_id']} for emergency {sos_id}")
        
        # Notify blood banks from eRaktkosh data
        blood_banks = eraktkosh_data.get("blood_availability", {}).get("blood_banks", [])
        for bank in blood_banks:
            # TODO: Implement blood bank notification
            logger.info(f"Notifying blood bank {bank.get('name', 'Unknown')} for emergency {sos_id}")
        
        logger.info(f"Emergency notifications completed for SOS {sos_id}")
        
    except Exception as e:
        logger.error(f"Failed to send emergency notifications: {str(e)}")