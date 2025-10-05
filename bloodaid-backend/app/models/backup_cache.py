"""
Backup Data Cache Models
Database models for storing scraped eRaktKosh data
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from app.config.database import Base

class BackupBloodBank(Base):
    """Model for cached blood bank data from eRaktKosh"""
    __tablename__ = "backup_blood_banks"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)  # Hash-based ID from scraper
    name = Column(String(500), nullable=False, index=True)
    address = Column(Text)
    contact = Column(String(50))
    email = Column(String(255))
    city = Column(String(255), index=True)
    state = Column(String(100), index=True)
    district = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    is_government = Column(Boolean, default=False)
    
    # Metadata
    source = Column(String(50), default="eraktkosh")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    validation_source = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data as JSON
    available_blood_groups = Column(JSON)  # List of available blood groups
    additional_info = Column(JSON)  # Extra scraped data
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_location', 'state', 'city'),
        Index('idx_coordinates', 'latitude', 'longitude'),
        Index('idx_government', 'is_government'),
        Index('idx_active_updated', 'is_active', 'last_updated'),
    )

class BackupBloodAvailability(Base):
    """Model for cached blood availability data from eRaktKosh"""
    __tablename__ = "backup_blood_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)  # Hash-based ID
    blood_bank_name = Column(String(500), nullable=False, index=True)
    blood_group = Column(String(10), nullable=False, index=True)
    units_available = Column(Integer, default=0)
    contact = Column(String(50))
    address = Column(Text)
    city = Column(String(255), index=True)
    state = Column(String(100), index=True)
    district = Column(String(255))
    
    # Metadata
    source = Column(String(50), default="eraktkosh")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    validation_source = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data as JSON
    additional_info = Column(JSON)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_group_units', 'blood_group', 'units_available'),
        Index('idx_location_blood', 'state', 'city', 'blood_group'),
        Index('idx_bank_blood', 'blood_bank_name', 'blood_group'),
        Index('idx_active_updated_avail', 'is_active', 'last_updated'),
    )

class BackupDonor(Base):
    """Model for cached donor data from eRaktKosh (generated from blood banks)"""
    __tablename__ = "backup_donors"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)  # Hash-based ID
    name = Column(String(500), nullable=False)
    blood_group = Column(String(10), index=True)
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    city = Column(String(255), index=True)
    state = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    is_available = Column(Boolean, default=True)
    is_blood_bank = Column(Boolean, default=False)  # Generated from blood bank
    
    # Metadata
    source = Column(String(50), default="eraktkosh")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    validation_source = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data as JSON
    additional_info = Column(JSON)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_group_available', 'blood_group', 'is_available'),
        Index('idx_location_donor', 'state', 'city'),
        Index('idx_coordinates_donor', 'latitude', 'longitude'),
        Index('idx_is_blood_bank', 'is_blood_bank'),
        Index('idx_active_updated_donor', 'is_active', 'last_updated'),
    )

class BackupDataMetrics(Base):
    """Model for tracking backup data metrics and health"""
    __tablename__ = "backup_data_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Counts
    total_blood_banks = Column(Integer, default=0)
    total_availability_records = Column(Integer, default=0)
    total_donors = Column(Integer, default=0)
    
    # Validation stats
    blood_banks_valid = Column(Integer, default=0)
    blood_banks_invalid = Column(Integer, default=0)
    availability_valid = Column(Integer, default=0)
    availability_invalid = Column(Integer, default=0)
    donors_valid = Column(Integer, default=0)
    donors_invalid = Column(Integer, default=0)
    
    # Performance metrics
    scraping_duration_seconds = Column(Float)
    validation_duration_seconds = Column(Float)
    total_duration_seconds = Column(Float)
    
    # Status
    update_successful = Column(Boolean, default=False)
    error_message = Column(Text)
    
    # Source info
    source = Column(String(50), default="eraktkosh")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_date_successful', 'date', 'update_successful'),
    )