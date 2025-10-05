from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.dependencies import get_current_patient
from app.models.user import User

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/profile")
async def get_patient_profile(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get patient profile"""
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "username": current_user.username,
        "blood_group": current_user.blood_group,
        "total_requests": 5,  # Mock data
        "last_transfusion": "15 days ago"
    }