from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional
import re

from app.config.database import get_db
from app.services.otp_service import otp_service
from app.models.user import User, UserType, BloodGroup
from app.models.donor import Donor
from app.models.patient import Patient
from app.core.security import create_access_token
from datetime import datetime

router = APIRouter(prefix="/auth/otp", tags=["OTP Authentication"])

# Pydantic schemas
class PhoneNumberRequest(BaseModel):
    phone_number: str
    purpose: str = "login"  # login, registration
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove any non-digit characters
        cleaned = re.sub(r'\D', '', v)
        
        # Check if it's a valid Indian phone number
        if len(cleaned) == 10:
            # Add country code if not present
            cleaned = '+91' + cleaned
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = '+' + cleaned
        elif len(cleaned) == 13 and cleaned.startswith('+91'):
            cleaned = cleaned
        else:
            raise ValueError('Invalid phone number format')
        
        return cleaned

class OTPVerificationRequest(BaseModel):
    phone_number: str
    otp_code: str
    purpose: str = "login"
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Apply same validation as PhoneNumberRequest
        cleaned = re.sub(r'\D', '', v)
        if len(cleaned) == 10:
            cleaned = '+91' + cleaned
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = '+' + cleaned
        elif len(cleaned) == 13 and cleaned.startswith('+91'):
            cleaned = cleaned
        else:
            raise ValueError('Invalid phone number format')
        return cleaned

class UserRegistrationWithOTP(BaseModel):
    phone_number: str
    otp_code: str
    name: str
    user_type: UserType
    blood_group: BloodGroup
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    # Donor specific fields
    eraktkosh_id: Optional[str] = None
    weight: Optional[float] = None
    # Patient specific fields
    username: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        cleaned = re.sub(r'\D', '', v)
        if len(cleaned) == 10:
            cleaned = '+91' + cleaned
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            cleaned = '+' + cleaned
        elif len(cleaned) == 13 and cleaned.startswith('+91'):
            cleaned = cleaned
        else:
            raise ValueError('Invalid phone number format')
        return cleaned

class OTPResponse(BaseModel):
    success: bool
    message: str
    expires_at: Optional[datetime] = None
    otp_code: Optional[str] = None  # For development only

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[dict] = None

@router.post("/send", response_model=OTPResponse)
async def send_otp(
    request: PhoneNumberRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Send OTP to phone number"""
    
    try:
        # Get client IP and user agent
        client_ip = req.client.host
        user_agent = req.headers.get("user-agent", "")
        
        # Create OTP
        otp_data = otp_service.create_otp(
            db=db,
            phone_number=request.phone_number,
            purpose=request.purpose,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Send OTP via SMS
        sms_result = otp_service.send_otp_sms(
            phone_number=request.phone_number,
            otp_code=otp_data["otp_code"]
        )
        
        # Always return success for development, but log any issues
        if not sms_result["success"]:
            print(f"SMS sending issue: {sms_result.get('message', 'Unknown error')}")
        
        return OTPResponse(
            success=True,
            message=f"OTP sent to {request.phone_number}",
            expires_at=otp_data["expires_at"],
            otp_code=otp_data["otp_code"] if sms_result.get("mock") else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send OTP: {str(e)}"
        )

@router.post("/verify", response_model=AuthResponse)
async def verify_otp_login(
    request: OTPVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify OTP and login existing user"""
    
    # Verify OTP
    verification_result = otp_service.verify_otp(
        db=db,
        phone_number=request.phone_number,
        otp_code=request.otp_code,
        purpose=request.purpose
    )
    
    if not verification_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=verification_result["message"]
        )
    
    # Find user by phone number
    user = db.query(User).filter(User.phone == request.phone_number).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please register first."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Account is deactivated"
        )
    
    # Update user verification status and last login
    user.is_phone_verified = True
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(subject=str(user.id))
    
    return AuthResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        user={
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "username": user.username,
            "user_type": user.user_type,
            "blood_group": user.blood_group,
            "is_verified": user.is_verified
        }
    )

@router.post("/register", response_model=AuthResponse)
async def register_with_otp(
    request: UserRegistrationWithOTP,
    db: Session = Depends(get_db)
):
    """Register new user with OTP verification"""
    
    # Verify OTP first
    verification_result = otp_service.verify_otp(
        db=db,
        phone_number=request.phone_number,
        otp_code=request.otp_code,
        purpose="registration"
    )
    
    if not verification_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=verification_result["message"]
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.phone == request.phone_number
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this phone number already exists"
        )
    
    # Check email if provided
    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
    
    # Check username for patients
    if request.user_type == UserType.PATIENT and request.username:
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
    
    # Check eRaktKosh ID for donors
    if request.user_type == UserType.DONOR and request.eraktkosh_id:
        existing_eraktkosh = db.query(User).filter(
            User.eraktkosh_id == request.eraktkosh_id
        ).first()
        if existing_eraktkosh:
            raise HTTPException(
                status_code=400,
                detail="eRaktKosh ID already registered"
            )
    
    # Create user
    new_user = User(
        user_type=request.user_type,
        name=request.name,
        email=request.email,
        phone=request.phone_number,
        password_hash=None,  # No password for OTP authentication
        username=request.username,
        blood_group=request.blood_group,
        eraktkosh_id=request.eraktkosh_id,
        age=request.age,
        weight=request.weight,
        gender=request.gender,
        is_phone_verified=True,  # Verified via OTP
        is_email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create type-specific profile
    if request.user_type == UserType.DONOR:
        donor_profile = Donor(
            user_id=new_user.id,
            hemoglobin_level=request.weight * 0.15 if request.weight else 14.0,
            accepts_emergency_requests=True,
            max_travel_distance=10.0
        )
        db.add(donor_profile)
    elif request.user_type == UserType.PATIENT:
        patient_profile = Patient(
            user_id=new_user.id,
            enable_auto_alerts=True,
            alert_advance_days=3,
            max_wait_time_hours=24
        )
        db.add(patient_profile)
    
    db.commit()
    
    # Create access token
    access_token = create_access_token(subject=str(new_user.id))
    
    return AuthResponse(
        success=True,
        message=f"{request.user_type.value} registered successfully",
        access_token=access_token,
        user={
            "id": str(new_user.id),
            "name": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone,
            "username": new_user.username,
            "user_type": new_user.user_type,
            "blood_group": new_user.blood_group,
            "is_verified": new_user.is_verified
        }
    )

@router.post("/cleanup")
async def cleanup_expired_otps(db: Session = Depends(get_db)):
    """Cleanup expired OTPs (admin endpoint)"""
    
    cleaned_count = otp_service.cleanup_expired_otps(db)
    
    return {
        "success": True,
        "message": f"Cleaned up {cleaned_count} expired OTPs"
    }