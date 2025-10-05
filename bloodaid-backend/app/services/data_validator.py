"""
Data Validation Service for eRaktKosh Backup Data
Cleans and validates scraped data for consistency and accuracy
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[Dict] = None

class DataValidator:
    """Validates and cleans scraped data"""
    
    # Indian states and UTs for validation
    VALID_STATES = {
        "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
        "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
        "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
        "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
        "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
        "andaman and nicobar islands", "chandigarh", "dadra and nagar haveli and daman and diu",
        "delhi", "jammu and kashmir", "ladakh", "lakshadweep", "puducherry"
    }
    
    # Valid blood groups
    VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    
    # Common hospital/blood bank keywords
    MEDICAL_KEYWORDS = {
        "hospital", "medical", "health", "clinic", "blood bank", "blood center",
        "dispensary", "nursing home", "medicare", "healthcare", "infirmary"
    }
    
    # Government institution keywords
    GOVT_KEYWORDS = {
        "government", "govt", "district", "state", "central", "municipal",
        "corporation", "council", "public", "national", "regional"
    }
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.phone_pattern = re.compile(r'[\+]?[1-9]?[0-9]{7,15}')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.pincode_pattern = re.compile(r'\b[1-9][0-9]{5}\b')
        self.numbers_pattern = re.compile(r'\d+')
    
    def validate_blood_bank_info(self, blood_bank: Dict) -> ValidationResult:
        """Validate blood bank information"""
        errors = []
        warnings = []
        cleaned_data = blood_bank.copy()
        
        # Validate name
        if not blood_bank.get("name") or len(blood_bank["name"].strip()) < 3:
            errors.append("Blood bank name is missing or too short")
        else:
            # Clean name
            cleaned_name = self._clean_text(blood_bank["name"])
            if cleaned_name != blood_bank["name"]:
                cleaned_data["name"] = cleaned_name
                warnings.append("Blood bank name was cleaned")
        
        # Validate and clean address
        if not blood_bank.get("address"):
            warnings.append("Address is missing")
            cleaned_data["address"] = ""
        else:
            cleaned_address = self._clean_address(blood_bank["address"])
            if cleaned_address != blood_bank["address"]:
                cleaned_data["address"] = cleaned_address
                warnings.append("Address was cleaned")
        
        # Validate contact
        contact = blood_bank.get("contact", "")
        cleaned_contact = self._validate_and_clean_phone(contact)
        if cleaned_contact != contact:
            cleaned_data["contact"] = cleaned_contact
            if not cleaned_contact:
                warnings.append("Contact number is invalid or missing")
            else:
                warnings.append("Contact number was cleaned")
        
        # Validate email
        email = blood_bank.get("email", "")
        if email and not self.email_pattern.match(email):
            warnings.append("Email format is invalid")
            cleaned_data["email"] = ""
        
        # Validate state
        state = blood_bank.get("state", "").lower().strip()
        if state and state not in self.VALID_STATES:
            # Try to find closest match
            closest_state = self._find_closest_state(state)
            if closest_state:
                cleaned_data["state"] = closest_state
                warnings.append(f"State '{blood_bank['state']}' corrected to '{closest_state}'")
            else:
                warnings.append(f"State '{blood_bank['state']}' is not recognized")
        
        # Validate coordinates
        lat = blood_bank.get("latitude")
        lon = blood_bank.get("longitude")
        if lat is not None:
            try:
                lat_float = float(lat)
                if not (-90 <= lat_float <= 90):
                    errors.append("Latitude is out of valid range")
                    cleaned_data["latitude"] = None
                else:
                    cleaned_data["latitude"] = lat_float
            except (ValueError, TypeError):
                warnings.append("Latitude is not a valid number")
                cleaned_data["latitude"] = None
        
        if lon is not None:
            try:
                lon_float = float(lon)
                if not (-180 <= lon_float <= 180):
                    errors.append("Longitude is out of valid range")
                    cleaned_data["longitude"] = None
                else:
                    cleaned_data["longitude"] = lon_float
            except (ValueError, TypeError):
                warnings.append("Longitude is not a valid number")
                cleaned_data["longitude"] = None
        
        # Validate is_government flag
        is_govt = self._detect_government_institution(
            blood_bank.get("name", "") + " " + blood_bank.get("address", "")
        )
        cleaned_data["is_government"] = is_govt
        
        # Add validation timestamp
        cleaned_data["validated_at"] = datetime.now().isoformat()
        cleaned_data["validation_source"] = "eraktkosh_validator"
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def validate_blood_availability(self, availability: Dict) -> ValidationResult:
        """Validate blood availability information"""
        errors = []
        warnings = []
        cleaned_data = availability.copy()
        
        # Validate blood group
        blood_group = availability.get("blood_group", "").strip().upper()
        if blood_group not in self.VALID_BLOOD_GROUPS:
            # Try to fix common variations
            blood_group_fixed = self._fix_blood_group(blood_group)
            if blood_group_fixed:
                cleaned_data["blood_group"] = blood_group_fixed
                warnings.append(f"Blood group '{availability.get('blood_group')}' corrected to '{blood_group_fixed}'")
            else:
                errors.append(f"Invalid blood group: {availability.get('blood_group')}")
        else:
            cleaned_data["blood_group"] = blood_group
        
        # Validate units available
        units = availability.get("units_available")
        if units is not None:
            try:
                units_int = int(units)
                if units_int < 0:
                    warnings.append("Units available is negative, setting to 0")
                    cleaned_data["units_available"] = 0
                elif units_int > 1000:
                    warnings.append("Units available seems unusually high")
                    cleaned_data["units_available"] = units_int
                else:
                    cleaned_data["units_available"] = units_int
            except (ValueError, TypeError):
                warnings.append("Units available is not a valid number, setting to 0")
                cleaned_data["units_available"] = 0
        else:
            warnings.append("Units available is missing, setting to 0")
            cleaned_data["units_available"] = 0
        
        # Validate blood bank name
        bank_name = availability.get("blood_bank_name", "").strip()
        if not bank_name or len(bank_name) < 3:
            errors.append("Blood bank name is missing or too short")
        else:
            cleaned_data["blood_bank_name"] = self._clean_text(bank_name)
        
        # Validate contact
        contact = availability.get("contact", "")
        cleaned_contact = self._validate_and_clean_phone(contact)
        cleaned_data["contact"] = cleaned_contact
        if not cleaned_contact and contact:
            warnings.append("Contact number is invalid")
        
        # Validate and clean address
        address = availability.get("address", "")
        if address:
            cleaned_data["address"] = self._clean_address(address)
        
        # Validate state and district
        state = availability.get("state", "").lower().strip()
        if state and state not in self.VALID_STATES:
            closest_state = self._find_closest_state(state)
            if closest_state:
                cleaned_data["state"] = closest_state
                warnings.append(f"State corrected to '{closest_state}'")
        
        # Validate last_updated
        last_updated = availability.get("last_updated")
        if isinstance(last_updated, str):
            try:
                # Try to parse ISO format
                datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                cleaned_data["last_updated"] = last_updated
            except ValueError:
                warnings.append("Invalid last_updated format, using current time")
                cleaned_data["last_updated"] = datetime.now().isoformat()
        elif isinstance(last_updated, datetime):
            cleaned_data["last_updated"] = last_updated.isoformat()
        else:
            cleaned_data["last_updated"] = datetime.now().isoformat()
        
        # Add validation metadata
        cleaned_data["validated_at"] = datetime.now().isoformat()
        cleaned_data["validation_source"] = "eraktkosh_validator"
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def validate_donor_data(self, donor: Dict) -> ValidationResult:
        """Validate donor information"""
        errors = []
        warnings = []
        cleaned_data = donor.copy()
        
        # Validate name
        name = donor.get("name", "").strip()
        if not name or len(name) < 2:
            errors.append("Donor name is missing or too short")
        else:
            cleaned_data["name"] = self._clean_text(name)
        
        # Validate blood group
        blood_group = donor.get("blood_group", "").strip().upper()
        if blood_group and blood_group not in self.VALID_BLOOD_GROUPS:
            blood_group_fixed = self._fix_blood_group(blood_group)
            if blood_group_fixed:
                cleaned_data["blood_group"] = blood_group_fixed
                warnings.append(f"Blood group corrected to '{blood_group_fixed}'")
            else:
                warnings.append(f"Invalid blood group: {blood_group}")
                cleaned_data["blood_group"] = "Unknown"
        elif blood_group:
            cleaned_data["blood_group"] = blood_group
        
        # Validate phone
        phone = donor.get("phone", "")
        cleaned_phone = self._validate_and_clean_phone(phone)
        cleaned_data["phone"] = cleaned_phone
        if not cleaned_phone and phone:
            warnings.append("Phone number is invalid")
        
        # Validate email
        email = donor.get("email", "")
        if email and not self.email_pattern.match(email):
            warnings.append("Email format is invalid")
            cleaned_data["email"] = ""
        
        # Validate address
        address = donor.get("address", "")
        if address:
            cleaned_data["address"] = self._clean_address(address)
        
        # Validate coordinates
        lat = donor.get("latitude")
        lon = donor.get("longitude")
        if lat is not None:
            try:
                lat_float = float(lat)
                if -90 <= lat_float <= 90:
                    cleaned_data["latitude"] = lat_float
                else:
                    warnings.append("Latitude out of range")
                    cleaned_data["latitude"] = None
            except (ValueError, TypeError):
                warnings.append("Invalid latitude")
                cleaned_data["latitude"] = None
        
        if lon is not None:
            try:
                lon_float = float(lon)
                if -180 <= lon_float <= 180:
                    cleaned_data["longitude"] = lon_float
                else:
                    warnings.append("Longitude out of range")
                    cleaned_data["longitude"] = None
            except (ValueError, TypeError):
                warnings.append("Invalid longitude")
                cleaned_data["longitude"] = None
        
        # Set validation metadata
        cleaned_data["validated_at"] = datetime.now().isoformat()
        cleaned_data["validation_source"] = "eraktkosh_validator"
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-\.\,\(\)\&]', '', text)
        
        # Capitalize properly
        text = text.title()
        
        return text
    
    def _clean_address(self, address: str) -> str:
        """Clean and normalize address"""
        if not address:
            return ""
        
        # Remove extra whitespace and normalize
        address = re.sub(r'\s+', ' ', address.strip())
        
        # Remove common prefixes that don't add value
        prefixes_to_remove = ["address:", "add:", "addr:"]
        for prefix in prefixes_to_remove:
            if address.lower().startswith(prefix):
                address = address[len(prefix):].strip()
        
        return address
    
    def _validate_and_clean_phone(self, phone: str) -> str:
        """Validate and clean phone number"""
        if not phone:
            return ""
        
        # Remove all non-digits except +
        cleaned = re.sub(r'[^\d\+]', '', phone)
        
        # Check if it matches Indian phone number patterns
        indian_patterns = [
            r'^\+91[6-9]\d{9}$',  # +91 followed by 10 digit number
            r'^[6-9]\d{9}$',      # 10 digit number starting with 6-9
            r'^0[6-9]\d{9}$',     # 11 digit with leading 0
        ]
        
        for pattern in indian_patterns:
            if re.match(pattern, cleaned):
                # Normalize to +91 format
                if cleaned.startswith('+91'):
                    return cleaned
                elif len(cleaned) == 10:
                    return f"+91{cleaned}"
                elif len(cleaned) == 11 and cleaned.startswith('0'):
                    return f"+91{cleaned[1:]}"
        
        # If no pattern matches, return empty string
        return ""
    
    def _fix_blood_group(self, blood_group: str) -> Optional[str]:
        """Try to fix common blood group variations"""
        if not blood_group:
            return None
        
        # Common variations and fixes
        fixes = {
            "A POSITIVE": "A+",
            "A NEGATIVE": "A-",
            "B POSITIVE": "B+",
            "B NEGATIVE": "B-",
            "AB POSITIVE": "AB+",
            "AB NEGATIVE": "AB-",
            "O POSITIVE": "O+",
            "O NEGATIVE": "O-",
            "A POS": "A+",
            "A NEG": "A-",
            "B POS": "B+",
            "B NEG": "B-",
            "AB POS": "AB+",
            "AB NEG": "AB-",
            "O POS": "O+",
            "O NEG": "O-"
        }
        
        blood_group_upper = blood_group.upper().strip()
        return fixes.get(blood_group_upper)
    
    def _find_closest_state(self, state: str) -> Optional[str]:
        """Find closest matching state name"""
        state_lower = state.lower().strip()
        
        # Direct match
        if state_lower in self.VALID_STATES:
            return next(s for s in self.VALID_STATES if s == state_lower).title()
        
        # Partial match
        for valid_state in self.VALID_STATES:
            if state_lower in valid_state or valid_state in state_lower:
                return valid_state.title()
        
        # Common abbreviations
        abbreviations = {
            "ap": "andhra pradesh",
            "ar": "arunachal pradesh",
            "as": "assam",
            "br": "bihar",
            "cg": "chhattisgarh",
            "ga": "goa",
            "gj": "gujarat",
            "hr": "haryana",
            "hp": "himachal pradesh",
            "jh": "jharkhand",
            "ka": "karnataka",
            "kl": "kerala",
            "mp": "madhya pradesh",
            "mh": "maharashtra",
            "mn": "manipur",
            "ml": "meghalaya",
            "mz": "mizoram",
            "nl": "nagaland",
            "or": "odisha",
            "pb": "punjab",
            "rj": "rajasthan",
            "sk": "sikkim",
            "tn": "tamil nadu",
            "tg": "telangana",
            "tr": "tripura",
            "up": "uttar pradesh",
            "uk": "uttarakhand",
            "wb": "west bengal"
        }
        
        if state_lower in abbreviations:
            return abbreviations[state_lower].title()
        
        return None
    
    def _detect_government_institution(self, text: str) -> bool:
        """Detect if institution is government-owned"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.GOVT_KEYWORDS)
    
    def validate_batch(self, data_list: List[Dict], data_type: str) -> Tuple[List[Dict], List[Dict], Dict]:
        """Validate a batch of data items"""
        valid_items = []
        invalid_items = []
        stats = {
            "total": len(data_list),
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
            "errors": 0
        }
        
        for item in data_list:
            try:
                if data_type == "blood_bank":
                    result = self.validate_blood_bank_info(item)
                elif data_type == "blood_availability":
                    result = self.validate_blood_availability(item)
                elif data_type == "donor":
                    result = self.validate_donor_data(item)
                else:
                    logger.error(f"Unknown data type: {data_type}")
                    continue
                
                stats["warnings"] += len(result.warnings)
                stats["errors"] += len(result.errors)
                
                if result.is_valid:
                    valid_items.append(result.cleaned_data)
                    stats["valid"] += 1
                else:
                    invalid_items.append({
                        "original_data": item,
                        "errors": result.errors,
                        "warnings": result.warnings
                    })
                    stats["invalid"] += 1
                    
            except Exception as e:
                logger.error(f"Error validating item: {str(e)}")
                invalid_items.append({
                    "original_data": item,
                    "errors": [f"Validation error: {str(e)}"],
                    "warnings": []
                })
                stats["invalid"] += 1
        
        return valid_items, invalid_items, stats

# Global validator instance
validator = DataValidator()

def get_validator() -> DataValidator:
    """Get the global validator instance"""
    return validator