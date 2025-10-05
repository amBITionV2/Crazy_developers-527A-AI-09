#!/usr/bin/env python3
"""
Create backup database tables for BloodAid system.
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.config.database import engine
from app.models.backup_cache import Base
from app.models.otp import OTP  # Import OTP model

def create_backup_tables():
    """Create all backup-related database tables."""
    try:
        print(f"📊 Connecting to database...")
        
        # Create all tables defined in backup_cache models
        print("🔨 Creating backup tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Backup tables created successfully!")
        print("Created tables:")
        print("  - backup_blood_banks")
        print("  - backup_blood_availability") 
        print("  - backup_donors")
        print("  - backup_data_metrics")
        print("  - otps (OTP authentication)")
        
    except Exception as e:
        print(f"❌ Error creating backup tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_backup_tables()
    sys.exit(0 if success else 1)