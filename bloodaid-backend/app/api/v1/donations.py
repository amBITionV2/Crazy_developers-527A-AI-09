from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/donations", tags=["Donations"])

@router.get("/history/{user_id}")
async def get_donation_history(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get donation history for user"""
    # Mock data
    history = [
        {
            "id": "donation-1",
            "recipient_name": "John Doe",
            "hospital": "City Hospital",
            "blood_group": "O+",
            "date": "2024-08-15",
            "status": "completed",
            "units": 1
        },
        {
            "id": "donation-2",
            "recipient_name": "Jane Smith", 
            "hospital": "General Hospital",
            "blood_group": "O+",
            "date": "2024-06-20",
            "status": "completed",
            "units": 1
        }
    ]
    return history

@router.get("/stats/{user_id}")
async def get_donation_stats(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get donation statistics"""
    return {
        "total_donations": 12,
        "pending_requests": 2,
        "lives_impacted": 36,
        "next_eligible_date": "2024-12-15"
    }