from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.config.database import Base

class Donor(Base):
    __tablename__ = "donors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Donor-specific information
    total_donations = Column(Integer, default=0)
    last_donation_date = Column(DateTime, nullable=True)
    next_eligible_date = Column(DateTime, nullable=True)
    
    # Health Information
    hemoglobin_level = Column(Float)  # g/dL
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    
    # Medical History
    medical_conditions = Column(Text)  # JSON string of medical conditions
    medications = Column(Text)  # JSON string of current medications
    allergies = Column(Text)  # JSON string of allergies
    
    # Donation Preferences
    preferred_hospitals = Column(Text)  # JSON string of hospital IDs
    max_travel_distance = Column(Float, default=10.0)  # in km
    available_days = Column(String(20), default="1,2,3,4,5,6,7")  # Days of week (1=Monday)
    available_time_start = Column(String(5), default="09:00")
    available_time_end = Column(String(5), default="18:00")
    
    # Emergency Response
    accepts_emergency_requests = Column(Boolean, default=True)
    emergency_response_time = Column(Integer, default=30)  # minutes
    
    # Statistics
    lives_saved = Column(Integer, default=0)
    reliability_score = Column(Float, default=0.0)  # 0-100
    response_rate = Column(Float, default=0.0)  # percentage
    
    # Status
    is_donation_eligible = Column(Boolean, default=True)
    temporary_deferral_reason = Column(String(255), nullable=True)
    temporary_deferral_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="donor_profile")
    
    def __repr__(self):
        return f"<Donor {self.user_id} - Donations: {self.total_donations}>"