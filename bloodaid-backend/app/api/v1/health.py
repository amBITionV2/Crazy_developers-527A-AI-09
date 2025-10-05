from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.health_vitals import HealthVitals, HealthStatus

router = APIRouter(prefix="/health", tags=["Health"])

# Schemas
class VitalsCreate(BaseModel):
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    hemoglobin_level: Optional[float] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    blood_sugar_fasting: Optional[float] = None
    blood_sugar_random: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    notes: Optional[str] = None

class HealthResponse(BaseModel):
    success: bool
    health_score: float
    vitals: dict
    recommendations: List[str]
    donation_eligible: bool

@router.post("/vitals", response_model=HealthResponse)
async def update_vitals(
    vitals_data: VitalsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user health vitals"""
    
    # Calculate BMI if height and weight provided
    bmi = None
    if vitals_data.weight and vitals_data.height:
        height_m = vitals_data.height / 100  # Convert cm to m
        bmi = vitals_data.weight / (height_m * height_m)
    
    # Calculate health score (simplified algorithm)
    health_score = 100.0
    recommendations = []
    
    # Blood pressure evaluation
    if vitals_data.systolic_bp and vitals_data.diastolic_bp:
        if vitals_data.systolic_bp > 140 or vitals_data.diastolic_bp > 90:
            health_score -= 15
            recommendations.append("Blood pressure is high. Consider consulting a doctor.")
        elif vitals_data.systolic_bp < 90 or vitals_data.diastolic_bp < 60:
            health_score -= 10
            recommendations.append("Blood pressure is low. Monitor regularly.")
    
    # Hemoglobin evaluation
    if vitals_data.hemoglobin_level:
        if vitals_data.hemoglobin_level < 12.0:
            health_score -= 20
            recommendations.append("Hemoglobin is low. Increase iron-rich foods.")
        elif vitals_data.hemoglobin_level > 17.0:
            health_score -= 10
            recommendations.append("Hemoglobin is high. Stay hydrated and consult doctor.")
    
    # BMI evaluation
    if bmi:
        if bmi < 18.5:
            health_score -= 10
            recommendations.append("BMI indicates underweight. Consider gaining healthy weight.")
        elif bmi > 30:
            health_score -= 15
            recommendations.append("BMI indicates obesity. Consider weight management.")
        elif bmi > 25:
            health_score -= 5
            recommendations.append("BMI indicates overweight. Consider healthy lifestyle.")
    
    # Blood sugar evaluation
    if vitals_data.blood_sugar_fasting:
        if vitals_data.blood_sugar_fasting > 126:
            health_score -= 20
            recommendations.append("Fasting blood sugar is high. Consult doctor for diabetes screening.")
        elif vitals_data.blood_sugar_fasting < 70:
            health_score -= 10
            recommendations.append("Fasting blood sugar is low. Monitor for hypoglycemia.")
    
    # Determine health status
    if health_score >= 90:
        health_status = HealthStatus.EXCELLENT
    elif health_score >= 75:
        health_status = HealthStatus.GOOD
    elif health_score >= 60:
        health_status = HealthStatus.FAIR
    elif health_score >= 40:
        health_status = HealthStatus.POOR
    else:
        health_status = HealthStatus.CRITICAL
    
    # Determine donation eligibility
    donation_eligible = True
    if vitals_data.hemoglobin_level and vitals_data.hemoglobin_level < 12.5:
        donation_eligible = False
        recommendations.append("Not eligible for blood donation due to low hemoglobin.")
    
    if vitals_data.systolic_bp and (vitals_data.systolic_bp > 160 or vitals_data.systolic_bp < 90):
        donation_eligible = False
        recommendations.append("Not eligible for blood donation due to blood pressure.")
    
    if vitals_data.weight and vitals_data.weight < 50:
        donation_eligible = False
        recommendations.append("Not eligible for blood donation due to low weight.")
    
    # Create vitals record
    vitals = HealthVitals(
        user_id=current_user.id,
        systolic_bp=vitals_data.systolic_bp,
        diastolic_bp=vitals_data.diastolic_bp,
        hemoglobin_level=vitals_data.hemoglobin_level,
        heart_rate=vitals_data.heart_rate,
        temperature=vitals_data.temperature,
        oxygen_saturation=vitals_data.oxygen_saturation,
        blood_sugar_fasting=vitals_data.blood_sugar_fasting,
        blood_sugar_random=vitals_data.blood_sugar_random,
        weight=vitals_data.weight,
        height=vitals_data.height,
        bmi=bmi,
        overall_health_score=health_score,
        health_status=health_status,
        donation_eligible=donation_eligible,
        notes=vitals_data.notes
    )
    
    db.add(vitals)
    db.commit()
    db.refresh(vitals)
    
    return HealthResponse(
        success=True,
        health_score=health_score,
        vitals={
            "systolic_bp": vitals_data.systolic_bp,
            "diastolic_bp": vitals_data.diastolic_bp,
            "hemoglobin_level": vitals_data.hemoglobin_level,
            "heart_rate": vitals_data.heart_rate,
            "temperature": vitals_data.temperature,
            "oxygen_saturation": vitals_data.oxygen_saturation,
            "weight": vitals_data.weight,
            "height": vitals_data.height,
            "bmi": bmi,
            "measured_at": vitals.measured_at.isoformat()
        },
        recommendations=recommendations,
        donation_eligible=donation_eligible
    )

@router.get("/score/{user_id}")
async def get_health_score(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest health score for user"""
    
    # Check if requesting own data or authorized
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest vitals
    latest_vitals = db.query(HealthVitals).filter(
        HealthVitals.user_id == user_id
    ).order_by(HealthVitals.measured_at.desc()).first()
    
    if not latest_vitals:
        return {
            "health_score": 85.0,  # Default score
            "vitals": {},
            "last_updated": None
        }
    
    return {
        "health_score": latest_vitals.overall_health_score,
        "vitals": {
            "hemoglobin_level": latest_vitals.hemoglobin_level,
            "systolic_bp": latest_vitals.systolic_bp,
            "diastolic_bp": latest_vitals.diastolic_bp,
            "heart_rate": latest_vitals.heart_rate,
            "weight": latest_vitals.weight,
            "bmi": latest_vitals.bmi,
            "health_status": latest_vitals.health_status
        },
        "last_updated": latest_vitals.measured_at.isoformat()
    }

@router.get("/donation-eligibility/{donor_id}")
async def check_donation_eligibility(
    donor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if donor is eligible for donation"""
    
    # Check if requesting own data or authorized
    if str(current_user.id) != donor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest vitals
    latest_vitals = db.query(HealthVitals).filter(
        HealthVitals.user_id == donor_id
    ).order_by(HealthVitals.measured_at.desc()).first()
    
    # Mock data for demonstration
    return {
        "is_eligible": latest_vitals.donation_eligible if latest_vitals else True,
        "last_donation": "45 days ago",
        "next_eligible_date": datetime.now().isoformat(),
        "total_donations": 12,
        "health_score": latest_vitals.overall_health_score if latest_vitals else 85.0,
        "restrictions": []
    }