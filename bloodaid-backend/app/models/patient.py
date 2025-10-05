from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.config.database import Base

class ChronicCondition(str, enum.Enum):
    THALASSEMIA = "thalassemia"
    DIALYSIS = "dialysis"
    CANCER = "cancer"
    HEMOPHILIA = "hemophilia"
    SICKLE_CELL = "sickle_cell"
    OTHER = "other"

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Patient-specific information
    chronic_condition = Column(Enum(ChronicCondition), nullable=True)
    condition_details = Column(Text)  # Detailed description
    
    # Transfusion History
    total_transfusions = Column(Integer, default=0)
    last_transfusion_date = Column(DateTime, nullable=True)
    units_per_transfusion = Column(Integer, default=1)
    transfusion_frequency_days = Column(Integer, nullable=True)  # Days between transfusions
    
    # Health Information
    current_hemoglobin = Column(Float)  # g/dL
    target_hemoglobin = Column(Float)  # Target g/dL
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    
    # Medical Information
    primary_hospital = Column(String(255))
    primary_doctor = Column(String(255))
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(15))
    
    # Medical History
    medical_conditions = Column(Text)  # JSON string
    medications = Column(Text)  # JSON string
    allergies = Column(Text)  # JSON string
    
    # Treatment Schedule
    next_scheduled_transfusion = Column(DateTime, nullable=True)
    regular_transfusion_day = Column(String(10), nullable=True)  # e.g., "Monday"
    preferred_time_slot = Column(String(20), nullable=True)  # e.g., "09:00-12:00"
    
    # Emergency Settings
    critical_hemoglobin_level = Column(Float, default=7.0)  # Alert threshold
    enable_auto_alerts = Column(Boolean, default=True)
    alert_advance_days = Column(Integer, default=3)  # Days before scheduled transfusion
    
    # Preferences
    preferred_donor_types = Column(Text)  # JSON: verified, nearby, regular
    max_wait_time_hours = Column(Integer, default=24)
    preferred_hospitals = Column(Text)  # JSON string of hospital IDs
    
    # Statistics
    successful_requests = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)  # hours
    
    # Status
    is_critical = Column(Boolean, default=False)
    current_treatment_plan = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="patient_profile")
    
    def __repr__(self):
        return f"<Patient {self.user_id} - Condition: {self.chronic_condition}>"