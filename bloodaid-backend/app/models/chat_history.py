from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.config.database import Base

class MessageType(str, enum.Enum):
    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    SYSTEM_MESSAGE = "system_message"

class ConversationContext(str, enum.Enum):
    GENERAL = "general"
    HEALTH_ADVICE = "health_advice"
    DONATION_GUIDANCE = "donation_guidance"
    EMERGENCY_SUPPORT = "emergency_support"
    MEDICATION_INFO = "medication_info"
    SYMPTOM_CHECK = "symptom_check"

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Conversation Details
    session_id = Column(UUID(as_uuid=True), default=uuid.uuid4)  # Group related messages
    message_type = Column(Enum(MessageType), nullable=False)
    
    # Message Content
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)  # AI response
    language = Column(String(5), default="en")
    
    # Context & Classification
    context = Column(Enum(ConversationContext), default=ConversationContext.GENERAL)
    intent = Column(String(100))  # Detected user intent
    entities = Column(Text)  # JSON string of extracted entities
    
    # AI/ML Information
    model_used = Column(String(100))  # LLM model version
    confidence_score = Column(Float)  # AI confidence in response
    rag_sources = Column(Text)  # JSON array of RAG sources used
    processing_time_ms = Column(Integer)  # Response generation time
    
    # Quality & Feedback
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    is_helpful = Column(Boolean, nullable=True)
    flagged_inappropriate = Column(Boolean, default=False)
    
    # Medical Disclaimer
    contains_medical_advice = Column(Boolean, default=False)
    disclaimer_shown = Column(Boolean, default=False)
    requires_professional_consultation = Column(Boolean, default=False)
    
    # Voice Features
    is_voice_input = Column(Boolean, default=False)
    is_voice_output = Column(Boolean, default=False)
    audio_duration_seconds = Column(Float, nullable=True)
    voice_language = Column(String(5), nullable=True)
    
    # Emergency Detection
    is_emergency_detected = Column(Boolean, default=False)
    emergency_keywords = Column(Text)  # JSON array
    escalated_to_emergency = Column(Boolean, default=False)
    
    # Privacy & Compliance
    contains_personal_info = Column(Boolean, default=False)
    anonymized = Column(Boolean, default=False)
    retention_category = Column(String(50), default="standard")  # standard, sensitive, emergency
    
    # Technical Details
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # IPv6 compatible
    device_type = Column(String(50))  # mobile, desktop, tablet
    
    # Follow-up Actions
    requires_followup = Column(Boolean, default=False)
    followup_action = Column(String(100))  # call_doctor, schedule_donation, etc.
    followup_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="chat_history")
    
    def __repr__(self):
        return f"<ChatHistory {self.user_id} - {self.message_type} - {self.created_at}>"