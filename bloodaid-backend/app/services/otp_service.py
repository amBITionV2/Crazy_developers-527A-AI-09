import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from twilio.rest import Client
import logging

from app.models.otp import OTP
from app.config.settings import settings

logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self):
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            except Exception as e:
                logger.warning(f"Twilio client initialization failed: {e}")
        
        self.otp_length = settings.OTP_LENGTH
        self.expiry_minutes = settings.OTP_EXPIRY_MINUTES
        self.max_attempts = settings.OTP_MAX_ATTEMPTS
    
    def generate_otp(self) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def create_otp(
        self, 
        db: Session, 
        phone_number: str, 
        purpose: str = "login",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create and store a new OTP"""
        
        # Invalidate any existing active OTPs for this phone number
        existing_otps = db.query(OTP).filter(
            OTP.phone_number == phone_number,
            OTP.is_verified == False,
            OTP.is_expired == False
        ).all()
        
        for otp in existing_otps:
            otp.mark_expired()
        
        # Generate new OTP
        otp_code = self.generate_otp()
        
        # Create OTP record
        new_otp = OTP(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose=purpose,
            expiry_minutes=self.expiry_minutes
        )
        
        if ip_address:
            new_otp.ip_address = ip_address
        if user_agent:
            new_otp.user_agent = user_agent
        
        db.add(new_otp)
        db.commit()
        db.refresh(new_otp)
        
        return {
            "otp_id": str(new_otp.id),
            "phone_number": phone_number,
            "expires_at": new_otp.expires_at,
            "otp_code": otp_code  # For development/testing only
        }
    
    def send_otp_sms(self, phone_number: str, otp_code: str) -> Dict[str, Any]:
        """Send OTP via SMS using Twilio"""
        if not self.twilio_client or not settings.TWILIO_ACCOUNT_SID or settings.TWILIO_ACCOUNT_SID == "your-twilio-account-sid":
            # For development/testing - return success without actually sending
            logger.info(f"SMS service not configured. OTP for {phone_number}: {otp_code}")
            return {
                "success": True,
                "message": f"OTP sent to {phone_number}",
                "mock": True,
                "otp_code": otp_code  # Include for testing
            }
        
        try:
            message = self.twilio_client.messages.create(
                body=f"Your BloodAid verification code is: {otp_code}. Valid for {self.expiry_minutes} minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            return {
                "success": True,
                "message": f"OTP sent to {phone_number}",
                "sid": message.sid
            }
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            # Fall back to mock mode for development
            return {
                "success": True,
                "message": f"OTP sent to {phone_number} (mock)",
                "mock": True,
                "otp_code": otp_code,
                "error": str(e)
            }
    
    def verify_otp(
        self, 
        db: Session, 
        phone_number: str, 
        otp_code: str,
        purpose: str = "login"
    ) -> Dict[str, Any]:
        """Verify OTP code"""
        
        # Find the most recent valid OTP for this phone number
        otp_record = db.query(OTP).filter(
            OTP.phone_number == phone_number,
            OTP.purpose == purpose,
            OTP.is_verified == False,
            OTP.is_expired == False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            return {
                "success": False,
                "message": "No valid OTP found for this phone number"
            }
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_record.expires_at:
            otp_record.mark_expired()
            db.commit()
            return {
                "success": False,
                "message": "OTP has expired"
            }
        
        # Increment attempts
        otp_record.increment_attempts()
        
        # Check if max attempts exceeded
        if otp_record.attempts > self.max_attempts:
            otp_record.mark_expired()
            db.commit()
            return {
                "success": False,
                "message": "Maximum verification attempts exceeded"
            }
        
        # Verify OTP code
        if otp_record.otp_code != otp_code:
            db.commit()
            return {
                "success": False,
                "message": "Invalid OTP code",
                "attempts_remaining": self.max_attempts - otp_record.attempts
            }
        
        # OTP is valid - mark as verified
        otp_record.verify()
        db.commit()
        
        return {
            "success": True,
            "message": "OTP verified successfully",
            "otp_id": str(otp_record.id)
        }
    
    def cleanup_expired_otps(self, db: Session):
        """Clean up expired OTPs"""
        expired_otps = db.query(OTP).filter(
            OTP.expires_at < datetime.utcnow(),
            OTP.is_expired == False
        ).all()
        
        for otp in expired_otps:
            otp.mark_expired()
        
        db.commit()
        return len(expired_otps)

# Global OTP service instance
otp_service = OTPService()