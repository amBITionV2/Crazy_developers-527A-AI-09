from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.config.database import Base

class UrgencyLevel(str, enum.Enum):
    CRITICAL = "critical"  # Life-threatening, immediate need
    HIGH = "high"         # Urgent, within hours
    MEDIUM = "medium"     # Scheduled, within days
    LOW = "low"          # Planned, flexible timing

class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    RESPONDING = "responding"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # SOS Identification
    sos_id = Column(String(100), unique=True, nullable=False)
    
    # Emergency Details
    patient_name = Column(String(255), nullable=False)
    hospital_name = Column(String(255), nullable=False)
    hospital_address = Column(String(500))
    blood_group_needed = Column(String(5), nullable=False)
    blood_group = Column(String(5), nullable=False)  # Alias for API compatibility
    units_needed = Column(Integer, default=1)
    
    # Urgency & Timing
    urgency_level = Column(Enum(UrgencyLevel), nullable=False)
    needed_by = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Location
    hospital_latitude = Column(Float)
    hospital_longitude = Column(Float)
    search_radius_km = Column(Float, default=5.0)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    
    # Contact Information
    contact_name = Column(String(255))
    contact_phone = Column(String(15))
    contact_number = Column(String(15))  # Alias for API compatibility
    emergency_contact_phone = Column(String(15))
    
    # Medical Information
    medical_condition = Column(String(255))
    special_requirements = Column(Text)  # Irradiated, CMV-negative, etc.
    additional_info = Column(Text)  # Additional information
    patient_age = Column(Integer)  # Patient age
    
    # Status & Tracking
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    donors_notified = Column(Integer, default=0)
    donors_responded = Column(Integer, default=0)
    donors_confirmed = Column(Integer, default=0)
    response_count = Column(Integer, default=0)  # Total responses received
    
    # eRaktkosh Integration
    eraktkosh_response = Column(JSON)  # Store eRaktkosh API response
    last_updated = Column(DateTime, default=datetime.utcnow)
    responders = Column(JSON)  # Store responder information
    
    # Response Tracking
    first_response_time = Column(DateTime, nullable=True)
    resolution_time = Column(DateTime, nullable=True)
    
    # Additional Information
    notes = Column(Text)
    hospital_contact_person = Column(String(255))
    case_id = Column(String(100))  # Hospital case/patient ID
    
    # AI/ML Predictions
    predicted_response_time = Column(Float)  # in minutes
    donor_availability_score = Column(Float)  # 0-100
    success_probability = Column(Float)  # 0-100
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", backref="emergency_alerts")
    
    def __repr__(self):
        return f"<EmergencyAlert {self.sos_id} - {self.blood_group} - {self.urgency_level}>"