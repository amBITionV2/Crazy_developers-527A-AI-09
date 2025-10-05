from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base
from datetime import datetime, timedelta
import uuid

class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Status tracking
    is_verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    is_expired = Column(Boolean, default=False)
    
    # Additional fields
    purpose = Column(String(50), default="login")  # login, registration, password_reset
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def __init__(self, phone_number: str, otp_code: str, purpose: str = "login", expiry_minutes: int = 10):
        self.phone_number = phone_number
        self.otp_code = otp_code
        self.purpose = purpose
        self.expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    @property
    def is_valid(self) -> bool:
        """Check if OTP is still valid (not expired and not verified)"""
        return (
            not self.is_verified and 
            not self.is_expired and 
            datetime.utcnow() < self.expires_at
        )
    
    def mark_expired(self):
        """Mark OTP as expired"""
        self.is_expired = True
    
    def verify(self):
        """Mark OTP as verified"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
    
    def increment_attempts(self):
        """Increment verification attempts"""
        self.attempts += 1