"""
BloodAid Donor Matching Algorithm
Intelligent matching of blood donors with patients
"""

import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class DonorScore:
    """Donor matching score with details"""
    donor_id: str
    total_score: float
    compatibility_score: float
    distance_score: float
    availability_score: float
    reliability_score: float
    urgency_bonus: float
    factors: List[str]


class DonorMatcher:
    """Advanced donor matching algorithm for BloodAid"""
    
    def __init__(self):
        # Blood type compatibility matrix
        self.compatibility_matrix = {
            "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
            "O+": ["O+", "A+", "B+", "AB+"],
            "A-": ["A-", "A+", "AB-", "AB+"],
            "A+": ["A+", "AB+"],
            "B-": ["B-", "B+", "AB-", "AB+"],
            "B+": ["B+", "AB+"],
            "AB-": ["AB-", "AB+"],
            "AB+": ["AB+"]
        }
        
        # Scoring weights
        self.weights = {
            "compatibility": 0.4,  # Blood type compatibility
            "distance": 0.25,      # Geographic proximity
            "availability": 0.2,   # Current availability
            "reliability": 0.1,    # Past donation history
            "urgency": 0.05       # Emergency bonus
        }
    
    def find_compatible_donors(
        self,
        patient_requirements: Dict[str, Any],
        available_donors: List[Dict[str, Any]],
        max_distance_km: float = 50,
        urgency_level: str = "medium"
    ) -> List[DonorScore]:
        """Find and rank compatible donors for a patient"""
        
        compatible_donors = []
        patient_blood_group = patient_requirements.get("blood_group", "O+")
        patient_location = patient_requirements.get("location", {})
        required_units = patient_requirements.get("units_needed", 1)
        
        for donor in available_donors:
            score = self._calculate_donor_score(
                donor=donor,
                patient_requirements=patient_requirements,
                urgency_level=urgency_level
            )
            
            # Only include if compatible and within distance
            if score.compatibility_score > 0 and score.distance_score > 0:
                compatible_donors.append(score)
        
        # Sort by total score (descending)
        compatible_donors.sort(key=lambda x: x.total_score, reverse=True)
        
        return compatible_donors
    
    def _calculate_donor_score(
        self,
        donor: Dict[str, Any],
        patient_requirements: Dict[str, Any],
        urgency_level: str
    ) -> DonorScore:
        """Calculate comprehensive donor matching score"""
        
        factors = []
        
        # 1. Blood type compatibility score
        compatibility_score = self._calculate_compatibility_score(
            donor.get("blood_group", "O+"),
            patient_requirements.get("blood_group", "O+")
        )
        
        if compatibility_score > 0:
            factors.append("Blood type compatible")
        
        # 2. Distance score
        distance_score = self._calculate_distance_score(
            donor.get("location", {}),
            patient_requirements.get("location", {}),
            max_distance=patient_requirements.get("max_distance_km", 50)
        )
        
        if distance_score > 0.8:
            factors.append("Very close proximity")
        elif distance_score > 0.5:
            factors.append("Nearby location")
        
        # 3. Availability score
        availability_score = self._calculate_availability_score(
            donor,
            patient_requirements.get("needed_by")
        )
        
        if availability_score > 0.8:
            factors.append("Immediately available")
        elif availability_score > 0.5:
            factors.append("Available soon")
        
        # 4. Reliability score (based on donation history)
        reliability_score = self._calculate_reliability_score(donor)
        
        if reliability_score > 0.8:
            factors.append("Highly reliable donor")
        elif reliability_score > 0.6:
            factors.append("Regular donor")
        
        # 5. Urgency bonus
        urgency_bonus = self._calculate_urgency_bonus(
            donor,
            urgency_level,
            patient_requirements
        )
        
        if urgency_bonus > 0:
            factors.append("Emergency responder")
        
        # Calculate weighted total score
        total_score = (
            compatibility_score * self.weights["compatibility"] +
            distance_score * self.weights["distance"] +
            availability_score * self.weights["availability"] +
            reliability_score * self.weights["reliability"] +
            urgency_bonus * self.weights["urgency"]
        ) * 100
        
        return DonorScore(
            donor_id=str(donor.get("id", "")),
            total_score=round(total_score, 2),
            compatibility_score=round(compatibility_score * 100, 2),
            distance_score=round(distance_score * 100, 2),
            availability_score=round(availability_score * 100, 2),
            reliability_score=round(reliability_score * 100, 2),
            urgency_bonus=round(urgency_bonus * 100, 2),
            factors=factors
        )
    
    def _calculate_compatibility_score(
        self,
        donor_blood_group: str,
        patient_blood_group: str
    ) -> float:
        """Calculate blood type compatibility score"""
        
        if not donor_blood_group or not patient_blood_group:
            return 0.0
        
        # Check if donor can give to patient
        compatible_recipients = self.compatibility_matrix.get(donor_blood_group, [])
        
        if patient_blood_group in compatible_recipients:
            # Perfect match gets highest score
            if donor_blood_group == patient_blood_group:
                return 1.0
            # Universal donor (O-) gets high score
            elif donor_blood_group == "O-":
                return 0.95
            # Other compatible combinations
            else:
                return 0.8
        
        return 0.0  # Not compatible
    
    def _calculate_distance_score(
        self,
        donor_location: Dict[str, Any],
        patient_location: Dict[str, Any],
        max_distance: float = 50
    ) -> float:
        """Calculate distance-based score"""
        
        if not donor_location or not patient_location:
            return 0.5  # Default score if location unavailable
        
        donor_lat = donor_location.get("latitude")
        donor_lng = donor_location.get("longitude")
        patient_lat = patient_location.get("latitude")
        patient_lng = patient_location.get("longitude")
        
        if not all([donor_lat, donor_lng, patient_lat, patient_lng]):
            return 0.5
        
        # Calculate distance using Haversine formula
        distance_km = self._calculate_distance(
            (donor_lat, donor_lng),
            (patient_lat, patient_lng)
        )
        
        if distance_km > max_distance:
            return 0.0  # Too far
        
        # Score inversely proportional to distance
        # Maximum score at 0 km, minimum score (0.1) at max_distance
        score = max(0.1, 1.0 - (distance_km / max_distance))
        return score
    
    def _calculate_availability_score(
        self,
        donor: Dict[str, Any],
        needed_by: Optional[str] = None
    ) -> float:
        """Calculate donor availability score"""
        
        base_score = 0.5
        
        # Check if donor is currently active
        if donor.get("is_active", True):
            base_score += 0.2
        
        # Check last donation eligibility (minimum 84 days)
        last_donation = donor.get("last_donation_date")
        if last_donation:
            try:
                if isinstance(last_donation, str):
                    last_date = datetime.fromisoformat(last_donation.replace('Z', '+00:00'))
                else:
                    last_date = last_donation
                
                days_since = (datetime.now() - last_date).days
                if days_since >= 84:  # Eligible
                    base_score += 0.3
                else:
                    return 0.0  # Not eligible yet
            except:
                pass
        else:
            # No previous donation recorded, assume eligible
            base_score += 0.3
        
        # Check availability preferences
        preferences = donor.get("availability_preferences", {})
        current_hour = datetime.now().hour
        
        if preferences.get("emergency_available", False):
            base_score += 0.2
        
        if preferences.get("flexible_schedule", True):
            base_score += 0.1
        
        # Time urgency factor
        if needed_by:
            try:
                needed_date = datetime.fromisoformat(needed_by.replace('Z', '+00:00'))
                hours_until = (needed_date - datetime.now()).total_seconds() / 3600
                
                if hours_until < 6:  # Very urgent
                    if preferences.get("emergency_available", False):
                        base_score += 0.2
                elif hours_until < 24:  # Urgent
                    base_score += 0.1
            except:
                pass
        
        return min(1.0, base_score)
    
    def _calculate_reliability_score(self, donor: Dict[str, Any]) -> float:
        """Calculate donor reliability based on history"""
        
        base_score = 0.5
        
        # Donation count
        donation_count = donor.get("total_donations", 0)
        if donation_count >= 10:
            base_score += 0.3
        elif donation_count >= 5:
            base_score += 0.2
        elif donation_count >= 1:
            base_score += 0.1
        
        # Response rate to requests
        response_rate = donor.get("response_rate", 0.8)  # Default 80%
        base_score += (response_rate - 0.5) * 0.4  # Scale 50-100% to 0-0.2
        
        # Completion rate (showed up after confirming)
        completion_rate = donor.get("completion_rate", 0.9)  # Default 90%
        base_score += (completion_rate - 0.5) * 0.4
        
        # Recent activity bonus
        last_activity = donor.get("last_active_date")
        if last_activity:
            try:
                if isinstance(last_activity, str):
                    last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                else:
                    last_date = last_activity
                
                days_since = (datetime.now() - last_date).days
                if days_since <= 30:  # Active in last month
                    base_score += 0.1
                elif days_since <= 90:  # Active in last 3 months
                    base_score += 0.05
            except:
                pass
        
        return min(1.0, base_score)
    
    def _calculate_urgency_bonus(
        self,
        donor: Dict[str, Any],
        urgency_level: str,
        patient_requirements: Dict[str, Any]
    ) -> float:
        """Calculate bonus score for emergency situations"""
        
        if urgency_level == "low":
            return 0.0
        
        bonus = 0.0
        
        # Emergency volunteer bonus
        if donor.get("emergency_volunteer", False):
            if urgency_level == "critical":
                bonus += 0.8
            elif urgency_level == "high":
                bonus += 0.6
            elif urgency_level == "medium":
                bonus += 0.3
        
        # Rare blood type bonus
        blood_group = patient_requirements.get("blood_group", "")
        if blood_group in ["AB-", "B-", "A-"] and donor.get("blood_group") == blood_group:
            bonus += 0.5
        
        # Hospital affiliation bonus
        if donor.get("hospital_affiliated", False):
            bonus += 0.2
        
        return min(1.0, bonus)
    
    def _calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    def batch_match_requests(
        self,
        requests: List[Dict[str, Any]],
        available_donors: List[Dict[str, Any]]
    ) -> Dict[str, List[DonorScore]]:
        """Match multiple requests efficiently"""
        
        results = {}
        
        # Sort requests by urgency
        sorted_requests = sorted(
            requests,
            key=lambda x: self._get_urgency_priority(x.get("urgency_level", "medium")),
            reverse=True
        )
        
        used_donors = set()
        
        for request in sorted_requests:
            request_id = str(request.get("id", ""))
            
            # Filter out already used donors for this batch
            available_for_request = [
                donor for donor in available_donors
                if str(donor.get("id", "")) not in used_donors
            ]
            
            matches = self.find_compatible_donors(
                patient_requirements=request,
                available_donors=available_for_request,
                urgency_level=request.get("urgency_level", "medium")
            )
            
            results[request_id] = matches
            
            # Mark top donors as potentially used (simplified allocation)
            top_donors_needed = min(request.get("units_needed", 1), len(matches))
            for i in range(top_donors_needed):
                if i < len(matches):
                    used_donors.add(matches[i].donor_id)
        
        return results
    
    def _get_urgency_priority(self, urgency_level: str) -> int:
        """Get numeric priority for urgency levels"""
        priorities = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return priorities.get(urgency_level, 2)

# Singleton instance
_matcher_instance = None

def get_donor_matcher() -> DonorMatcher:
    """Get or create donor matcher instance"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = DonorMatcher()
    return _matcher_instance