#!/usr/bin/env python3
"""
BloodAid Database Setup Script - Simple Version
Creates all required database tables
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.config.database import engine, Base
from app.models.user import User
from app.models.donor import Donor
from app.models.patient import Patient
from app.models.donation import Donation
from app.models.emergency_alert import EmergencyAlert
from app.models.health_vitals import HealthVitals
from app.models.chat_history import ChatHistory
from app.models.backup_cache import BackupBloodBank, BackupBloodAvailability, BackupDonor, BackupDataMetrics
from app.models.otp import OTP

def create_all_tables():
    """Create all database tables."""
    try:
        print(f"📊 Connecting to database...")
        
        # Create all tables defined in all models
        print("🔨 Creating all database tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ All database tables created successfully!")
        print("Created tables:")
        print("  - users (user accounts)")
        print("  - donors (donor profiles)")
        print("  - patients (patient profiles)")
        print("  - donations (donation records)")
        print("  - emergency_alerts (emergency requests)")
        print("  - health_vitals (health tracking)")
        print("  - chat_history (AI chat logs)")
        print("  - otps (OTP authentication)")
        print("  - backup_blood_banks (backup data)")
        print("  - backup_blood_availability (backup data)")
        print("  - backup_donors (backup data)")
        print("  - backup_data_metrics (backup data)")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🩸 BloodAid Database Setup")
    print("=" * 40)
    
    success = create_all_tables()
    
    if success:
        print("=" * 40)
        print("✅ Database setup completed successfully!")
        print("🚀 You can now test the OTP authentication system.")
    else:
        print("❌ Database setup failed!")
    
    sys.exit(0 if success else 1)