from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.config.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.dependencies import get_current_user
from app.models.user import User, UserType, BloodGroup
from app.models.donor import Donor
from app.models.patient import Patient

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    blood_group: BloodGroup

class DonorRegister(UserBase):
    password: str
    eraktkosh_id: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    gender: Optional[str] = None

class PatientRegister(UserBase):
    password: str
    username: str
    age: Optional[int] = None
    gender: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str
    user_type: UserType

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    success: bool = True
    message: str

@router.post("/donor/register", response_model=TokenResponse)
async def register_donor(
    donor_data: DonorRegister,
    db: Session = Depends(get_db)
):
    """Register a new donor"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == donor_data.email) | (User.phone == donor_data.phone)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or phone already exists"
        )
    
    # Check eRaktKosh ID if provided
    if donor_data.eraktkosh_id:
        existing_eraktkosh = db.query(User).filter(
            User.eraktkosh_id == donor_data.eraktkosh_id
        ).first()
        if existing_eraktkosh:
            raise HTTPException(
                status_code=400,
                detail="eRaktKosh ID already registered"
            )
    
    # Create user
    hashed_password = get_password_hash(donor_data.password)
    
    new_user = User(
        user_type=UserType.DONOR,
        name=donor_data.name,
        email=donor_data.email,
        phone=donor_data.phone,
        password_hash=hashed_password,
        blood_group=donor_data.blood_group,
        eraktkosh_id=donor_data.eraktkosh_id,
        age=donor_data.age,
        weight=donor_data.weight,
        gender=donor_data.gender,
        is_phone_verified=True,  # Assume verified for now
        is_email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create donor profile
    donor_profile = Donor(
        user_id=new_user.id,
        hemoglobin_level=donor_data.weight * 0.15 if donor_data.weight else 14.0,  # Estimate
        accepts_emergency_requests=True,
        max_travel_distance=10.0
    )
    
    db.add(donor_profile)
    db.commit()
    
    # Create access token
    access_token = create_access_token(subject=str(new_user.id))
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(new_user.id),
            "name": new_user.name,
            "email": new_user.email,
            "user_type": new_user.user_type,
            "blood_group": new_user.blood_group,
            "is_verified": new_user.is_verified
        },
        message="Donor registered successfully"
    )

@router.post("/patient/register", response_model=TokenResponse)
async def register_patient(
    patient_data: PatientRegister,
    db: Session = Depends(get_db)
):
    """Register a new patient"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == patient_data.email) | 
        (User.phone == patient_data.phone) |
        (User.username == patient_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email, phone, or username already exists"
        )
    
    # Create user
    hashed_password = get_password_hash(patient_data.password)
    
    new_user = User(
        user_type=UserType.PATIENT,
        name=patient_data.name,
        email=patient_data.email,
        phone=patient_data.phone,
        password_hash=hashed_password,
        username=patient_data.username,
        blood_group=patient_data.blood_group,
        age=patient_data.age,
        gender=patient_data.gender,
        is_phone_verified=True,  # Assume verified for now
        is_email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create patient profile
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
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(new_user.id),
            "name": new_user.name,
            "email": new_user.email,
            "username": new_user.username,
            "user_type": new_user.user_type,
            "blood_group": new_user.blood_group,
            "is_verified": new_user.is_verified
        },
        message="Patient registered successfully"
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user"""
    
    user = db.query(User).filter(
        User.email == login_data.email,
        User.user_type == login_data.user_type
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "user_type": user.user_type,
            "blood_group": user.blood_group,
            "is_verified": user.is_verified
        },
        message="Login successful"
    )

@router.get("/verify-token")
async def verify_token_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Verify if token is valid"""
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email,
            "user_type": current_user.user_type,
            "blood_group": current_user.blood_group,
            "is_verified": current_user.is_verified
        }
    }