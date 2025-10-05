from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.config.database import Base

class VitalType(str, enum.Enum):
    BLOOD_PRESSURE = "blood_pressure"
    HEMOGLOBIN = "hemoglobin"
    HEART_RATE = "heart_rate"
    TEMPERATURE = "temperature"
    OXYGEN_LEVEL = "oxygen_level"
    SUGAR_LEVEL = "sugar_level"
    WEIGHT = "weight"

class HealthStatus(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class HealthVitals(Base):
    __tablename__ = "health_vitals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Blood Pressure
    systolic_bp = Column(Integer)  # mmHg
    diastolic_bp = Column(Integer)  # mmHg
    
    # Blood Tests
    hemoglobin_level = Column(Float)  # g/dL
    hematocrit = Column(Float)  # percentage
    platelet_count = Column(Integer)  # per μL
    white_blood_cell_count = Column(Float)  # 10^3/μL
    
    # Vital Signs
    heart_rate = Column(Integer)  # bpm
    temperature = Column(Float)  # Fahrenheit
    oxygen_saturation = Column(Float)  # percentage
    respiratory_rate = Column(Integer)  # breaths per minute
    
    # Metabolic
    blood_sugar_fasting = Column(Float)  # mg/dL
    blood_sugar_random = Column(Float)  # mg/dL
    cholesterol_total = Column(Float)  # mg/dL
    cholesterol_hdl = Column(Float)  # mg/dL
    cholesterol_ldl = Column(Float)  # mg/dL
    
    # Physical Measurements
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    bmi = Column(Float)  # calculated
    
    # Iron Studies (important for blood donation)
    serum_iron = Column(Float)  # μg/dL
    ferritin = Column(Float)  # ng/mL
    transferrin_saturation = Column(Float)  # percentage
    
    # Liver Function
    alt_sgpt = Column(Float)  # U/L
    ast_sgot = Column(Float)  # U/L
    bilirubin_total = Column(Float)  # mg/dL
    
    # Kidney Function
    creatinine = Column(Float)  # mg/dL
    blood_urea_nitrogen = Column(Float)  # mg/dL
    
    # Overall Assessment
    overall_health_score = Column(Float)  # 0-100
    health_status = Column(Enum(HealthStatus))
    donation_eligible = Column(Boolean, default=True)
    
    # AI Predictions
    predicted_hemoglobin_trend = Column(String(20))  # "increasing", "stable", "decreasing"
    risk_score = Column(Float)  # 0-100
    recommended_recheck_days = Column(Integer)
    
    # Medical Context
    measured_by = Column(String(255))  # Doctor, self-reported, device
    measurement_location = Column(String(255))  # Hospital, clinic, home
    fasting_status = Column(Boolean, default=False)
    medication_taken = Column(Boolean, default=False)
    
    # Notes & Alerts
    notes = Column(Text)
    abnormal_values = Column(Text)  # JSON array of flags
    doctor_recommendations = Column(Text)
    
    # Device Information
    measurement_device = Column(String(255))  # BP monitor, glucometer, etc.
    device_calibration_date = Column(DateTime, nullable=True)
    
    # Timestamps
    measured_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="health_vitals")
    
    def __repr__(self):
        return f"<HealthVitals {self.user_id} - {self.measured_at.date()}>"