"""
BloodAid ML Prediction Module
Provides health predictions and risk assessments
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random


class HealthPredictor:
    """Health prediction and risk assessment for blood donation"""
    
    def __init__(self):
        # Health risk factors and their weights
        self.risk_factors = {
            "age": {"min": 18, "max": 65, "optimal": (25, 50)},
            "weight": {"min": 50, "critical": 45},
            "hemoglobin": {"min": 12.5, "optimal": (13.0, 16.0)},
            "blood_pressure_systolic": {"min": 110, "max": 160, "optimal": (120, 140)},
            "blood_pressure_diastolic": {"min": 70, "max": 100, "optimal": (80, 90)},
            "last_donation_days": {"min": 84}  # 3 months minimum
        }
    
    def predict_donation_eligibility(
        self,
        health_data: Dict[str, Any],
        user_profile: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Predict blood donation eligibility"""
        
        score = 100
        warnings = []
        recommendations = []
        risk_level = "low"
        
        # Age assessment
        age = health_data.get("age", 25)
        if age < 18:
            score -= 100
            warnings.append("Must be at least 18 years old to donate blood")
        elif age > 65:
            score -= 50
            warnings.append("Age above 65 requires special medical clearance")
        elif age > 60:
            score -= 10
            recommendations.append("Consider consulting your doctor before donation")
        
        # Weight assessment
        weight = health_data.get("weight", 60)
        if weight < 50:
            score -= 100
            warnings.append("Minimum weight requirement is 50 kg")
        elif weight < 55:
            score -= 20
            recommendations.append("Weight is on the lower side, ensure good nutrition")
        
        # Hemoglobin assessment
        hemoglobin = health_data.get("hemoglobin")
        if hemoglobin:
            if hemoglobin < 12.5:
                score -= 100
                warnings.append("Hemoglobin below 12.5 g/dL - not eligible for donation")
                recommendations.append("Increase iron-rich foods and consult a doctor")
            elif hemoglobin < 13.0:
                score -= 20
                recommendations.append("Hemoglobin is on the lower side, monitor regularly")
        
        # Blood pressure assessment
        bp_systolic = health_data.get("blood_pressure_systolic")
        bp_diastolic = health_data.get("blood_pressure_diastolic")
        
        if bp_systolic and bp_diastolic:
            if bp_systolic < 110 or bp_systolic > 160:
                score -= 50
                warnings.append("Blood pressure outside acceptable range (110-160 systolic)")
            if bp_diastolic < 70 or bp_diastolic > 100:
                score -= 50
                warnings.append("Blood pressure outside acceptable range (70-100 diastolic)")
        
        # Last donation history
        last_donation = health_data.get("last_donation_date")
        if last_donation:
            # Parse date string or assume it's already datetime
            if isinstance(last_donation, str):
                try:
                    last_date = datetime.fromisoformat(last_donation.replace('Z', '+00:00'))
                except:
                    last_date = datetime.now() - timedelta(days=100)  # Default to eligible
            else:
                last_date = last_donation
            
            days_since = (datetime.now() - last_date).days
            if days_since < 84:  # 3 months
                score -= 100
                warnings.append(f"Must wait {84 - days_since} more days before next donation")
        
        # Determine risk level and eligibility
        if score >= 80:
            risk_level = "low"
            eligible = True
        elif score >= 60:
            risk_level = "medium"
            eligible = True
            recommendations.append("Schedule pre-donation health check")
        elif score >= 30:
            risk_level = "high"
            eligible = False
            recommendations.append("Address health concerns before attempting donation")
        else:
            risk_level = "critical"
            eligible = False
            recommendations.append("Consult healthcare provider immediately")
        
        return {
            "eligible": eligible,
            "score": max(0, score),
            "risk_level": risk_level,
            "warnings": warnings,
            "recommendations": recommendations,
            "assessment_date": datetime.utcnow().isoformat(),
            "next_eligible_date": self._calculate_next_eligible_date(health_data)
        }
    
    def predict_health_trends(
        self,
        health_history: List[Dict[str, Any]],
        prediction_days: int = 30
    ) -> Dict[str, Any]:
        """Predict health trends based on historical data"""
        
        if not health_history or len(health_history) < 2:
            return {
                "trends": {},
                "predictions": {},
                "confidence": "low",
                "message": "Insufficient data for trend analysis"
            }
        
        # Sort by date
        sorted_history = sorted(
            health_history,
            key=lambda x: x.get("recorded_at", datetime.now()),
            reverse=True
        )
        
        trends = {}
        predictions = {}
        
        # Analyze hemoglobin trend
        hb_values = [h.get("hemoglobin") for h in sorted_history if h.get("hemoglobin")]
        if len(hb_values) >= 2:
            hb_trend = "stable"
            if hb_values[0] > hb_values[-1]:
                hb_trend = "improving"
            elif hb_values[0] < hb_values[-1]:
                hb_trend = "declining"
            
            trends["hemoglobin"] = {
                "trend": hb_trend,
                "current": hb_values[0],
                "previous": hb_values[-1],
                "change": round(hb_values[0] - hb_values[-1], 1)
            }
            
            # Simple prediction (linear trend)
            avg_change = sum(hb_values[i] - hb_values[i+1] for i in range(len(hb_values)-1)) / (len(hb_values)-1)
            predicted_hb = hb_values[0] + (avg_change * (prediction_days / 30))
            predictions["hemoglobin"] = round(max(0, predicted_hb), 1)
        
        # Analyze weight trend
        weight_values = [h.get("weight") for h in sorted_history if h.get("weight")]
        if len(weight_values) >= 2:
            weight_trend = "stable"
            if weight_values[0] > weight_values[-1]:
                weight_trend = "increasing"
            elif weight_values[0] < weight_values[-1]:
                weight_trend = "decreasing"
            
            trends["weight"] = {
                "trend": weight_trend,
                "current": weight_values[0],
                "previous": weight_values[-1],
                "change": round(weight_values[0] - weight_values[-1], 1)
            }
        
        confidence = "high" if len(sorted_history) >= 5 else "medium"
        
        return {
            "trends": trends,
            "predictions": predictions,
            "confidence": confidence,
            "analysis_period_days": (sorted_history[0].get("recorded_at", datetime.now()) - 
                                   sorted_history[-1].get("recorded_at", datetime.now())).days,
            "data_points": len(sorted_history)
        }
    
    def assess_emergency_urgency(
        self,
        patient_condition: Dict[str, Any],
        required_units: int = 1
    ) -> Dict[str, Any]:
        """Assess urgency level for emergency blood requests"""
        
        urgency_score = 50  # Base urgency
        urgency_factors = []
        
        # Medical condition factors
        condition = patient_condition.get("condition", "").lower()
        if "emergency" in condition or "trauma" in condition:
            urgency_score += 40
            urgency_factors.append("Emergency/trauma case")
        
        if "surgery" in condition:
            urgency_score += 30
            urgency_factors.append("Surgical requirement")
        
        if "thalassemia" in condition:
            urgency_score += 20
            urgency_factors.append("Chronic condition")
        
        # Blood requirements
        if required_units > 5:
            urgency_score += 30
            urgency_factors.append("Large blood requirement")
        elif required_units > 2:
            urgency_score += 15
            urgency_factors.append("Multiple units needed")
        
        # Rare blood type
        blood_group = patient_condition.get("blood_group", "")
        if blood_group in ["AB-", "B-", "A-"]:
            urgency_score += 25
            urgency_factors.append("Rare blood group")
        elif blood_group == "O-":
            urgency_score += 15
            urgency_factors.append("Universal donor type needed")
        
        # Time sensitivity
        needed_by = patient_condition.get("needed_by")
        if needed_by:
            try:
                needed_date = datetime.fromisoformat(needed_by.replace('Z', '+00:00'))
                hours_remaining = (needed_date - datetime.now()).total_seconds() / 3600
                
                if hours_remaining < 6:
                    urgency_score += 50
                    urgency_factors.append("Needed within 6 hours")
                elif hours_remaining < 24:
                    urgency_score += 30
                    urgency_factors.append("Needed within 24 hours")
                elif hours_remaining < 72:
                    urgency_score += 15
                    urgency_factors.append("Needed within 3 days")
            except:
                pass
        
        # Determine urgency level
        if urgency_score >= 90:
            urgency_level = "critical"
            response_time = "immediate"
        elif urgency_score >= 70:
            urgency_level = "high"
            response_time = "within_1_hour"
        elif urgency_score >= 50:
            urgency_level = "medium"
            response_time = "within_6_hours"
        else:
            urgency_level = "low"
            response_time = "within_24_hours"
        
        return {
            "urgency_level": urgency_level,
            "urgency_score": min(100, urgency_score),
            "response_time": response_time,
            "factors": urgency_factors,
            "recommended_actions": self._get_urgency_actions(urgency_level),
            "assessment_time": datetime.utcnow().isoformat()
        }
    
    def _calculate_next_eligible_date(self, health_data: Dict[str, Any]) -> Optional[str]:
        """Calculate when user will next be eligible for donation"""
        last_donation = health_data.get("last_donation_date")
        if last_donation:
            try:
                if isinstance(last_donation, str):
                    last_date = datetime.fromisoformat(last_donation.replace('Z', '+00:00'))
                else:
                    last_date = last_donation
                
                next_eligible = last_date + timedelta(days=84)  # 3 months
                if next_eligible > datetime.now():
                    return next_eligible.isoformat()
            except:
                pass
        
        return None
    
    def _get_urgency_actions(self, urgency_level: str) -> List[str]:
        """Get recommended actions based on urgency level"""
        actions = {
            "critical": [
                "Broadcast emergency alert to all compatible donors",
                "Contact emergency blood banks",
                "Notify hospital blood transfusion services",
                "Activate emergency donor network",
                "Consider blood substitutes if available"
            ],
            "high": [
                "Send alerts to nearby donors",
                "Contact blood banks in area",
                "Notify registered emergency donors",
                "Check hospital reserves"
            ],
            "medium": [
                "Post requirement on donor platforms",
                "Contact regular donors",
                "Schedule donation drives",
                "Coordinate with blood banks"
            ],
            "low": [
                "Schedule routine donation requests",
                "Plan ahead with regular donors",
                "Use normal blood bank channels"
            ]
        }
        
        return actions.get(urgency_level, [])

# Singleton instance
_predictor_instance = None

def get_health_predictor() -> HealthPredictor:
    """Get or create health predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = HealthPredictor()
    return _predictor_instance