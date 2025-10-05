from sqlalchemy import Column, String, Boolean, DateTime, Enum, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.config.database import Base

class UserType(str, enum.Enum):
    DONOR = "donor"
    PATIENT = "patient"
    BOTH = "both"

class BloodGroup(str, enum.Enum):
    O_POS = "O+"
    O_NEG = "O-"
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_type = Column(Enum(UserType), nullable=False)
    
    # Personal Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=True)  # For patients
    
    # Blood Information
    blood_group = Column(Enum(BloodGroup), nullable=False)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Verification
    is_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    eraktkosh_id = Column(String(100), unique=True, nullable=True)  # For donors
    
    # Status
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)  # For donors
    
    # Profile
    age = Column(Integer)
    weight = Column(Float)  # in kg
    gender = Column(String(10))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.name} ({self.user_type})>"