from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.config.database import Base

class DonationStatus(str, enum.Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DECLINED = "declined"
    NO_RESPONSE = "no_response"

class DonationType(str, enum.Enum):
    WHOLE_BLOOD = "whole_blood"
    PLATELETS = "platelets"
    PLASMA = "plasma"
    RED_CELLS = "red_cells"
    DOUBLE_RED = "double_red"

class Donation(Base):
    __tablename__ = "donations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    emergency_alert_id = Column(UUID(as_uuid=True), ForeignKey("emergency_alerts.id"), nullable=True)
    
    # Donation Details
    donation_type = Column(Enum(DonationType), default=DonationType.WHOLE_BLOOD)
    blood_group = Column(String(5), nullable=False)
    units_requested = Column(Integer, default=1)
    units_donated = Column(Integer, nullable=True)
    
    # Scheduling
    scheduled_datetime = Column(DateTime, nullable=False)
    actual_datetime = Column(DateTime, nullable=True)
    estimated_duration_minutes = Column(Integer, default=60)
    
    # Location
    hospital_name = Column(String(255), nullable=False)
    hospital_address = Column(String(500))
    hospital_contact = Column(String(15))
    room_number = Column(String(50))
    
    # Status & Tracking
    status = Column(Enum(DonationStatus), default=DonationStatus.REQUESTED)
    is_emergency = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    
    # Communication
    request_message = Column(Text)
    response_message = Column(Text)
    special_instructions = Column(Text)
    
    # Timing Tracking
    request_sent_at = Column(DateTime, default=datetime.utcnow)
    donor_responded_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Medical Information
    pre_donation_hemoglobin = Column(Float)
    post_donation_hemoglobin = Column(Float)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    pulse_rate = Column(Integer)
    
    # Quality & Testing
    blood_bag_number = Column(String(100))
    testing_results = Column(Text)  # JSON string
    is_tested = Column(Boolean, default=False)
    test_results_available_at = Column(DateTime, nullable=True)
    
    # Feedback & Rating
    donor_rating = Column(Integer)  # 1-5 rating by patient
    patient_rating = Column(Integer)  # 1-5 rating by donor
    donor_feedback = Column(Text)
    patient_feedback = Column(Text)
    
    # Administrative
    hospital_staff_id = Column(String(100))
    donation_certificate_number = Column(String(100))
    eraktkosh_donation_id = Column(String(100))
    
    # Compensation (if applicable)
    travel_reimbursement = Column(Float, default=0.0)
    meal_provided = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    donor = relationship("User", foreign_keys=[donor_id], backref="donations_given")
    patient = relationship("User", foreign_keys=[patient_id], backref="donations_received")
    emergency_alert = relationship("EmergencyAlert", backref="donations")
    
    def __repr__(self):
        return f"<Donation {self.id} - {self.blood_group} - {self.status}>"