"""
eRaktkosh Portal Integration Service
Integrates with the official eRaktkosh portal (https://eraktkosh.mohfw.gov.in) 
to fetch real-time blood availability, donor information, and blood bank details.
"""

import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
from loguru import logger
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime

class ERaktkoshService:
    """Service to integrate with eRaktkosh portal for real-time blood data."""
    
    BASE_URL = "https://eraktkosh.mohfw.gov.in"
    ENDPOINTS = {
        "blood_availability": "/BLDAHIMS/bloodbank/stockAvailability.cnt",
        "blood_center_directory": "/BLDAHIMS/bloodbank/nearbyBBRed.cnt", 
        "blood_camps": "/BLDAHIMS/bloodbank/campSchedule.cnt",
        "donor_login": "/BLDAHIMS/bloodbank/portalDonorLogin.cnt",
        "thalassemia_request": "/BLDAHIMS/bloodbank/portalThalassemiaLogin.cnt"
    }
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'BloodAid Emergency System/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_blood_availability(
        self, 
        state: str, 
        district: str, 
        blood_group: str,
        component_type: str = "Whole Blood"
    ) -> Dict[str, Any]:
        """
        Search for blood availability in specific location.
        
        Args:
            state: State name (e.g., "Delhi", "Maharashtra")
            district: District name 
            blood_group: Blood group (A+, B+, O+, AB+, A-, B-, O-, AB-)
            component_type: Type of blood component needed
            
        Returns:
            Dict containing blood bank details and availability
        """
        try:
            url = f"{self.BASE_URL}{self.ENDPOINTS['blood_availability']}"
            
            # Prepare search parameters
            search_data = {
                'state': state,
                'district': district,
                'bloodGroup': blood_group,
                'componentType': component_type,
                'searchType': 'EMERGENCY'
            }
            
            async with self.session.post(url, data=search_data) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return await self._parse_blood_availability(html_content)
                else:
                    logger.error(f"eRaktkosh API error: {response.status}")
                    return {"error": f"API error: {response.status}", "blood_banks": []}
                    
        except Exception as e:
            logger.error(f"Error searching blood availability: {str(e)}")
            return {"error": str(e), "blood_banks": []}
    
    async def find_nearby_blood_centers(
        self, 
        state: str, 
        district: str, 
        pincode: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find nearby blood centers/banks.
        
        Args:
            state: State name
            district: District name
            pincode: PIN code for more precise location
            
        Returns:
            List of blood center details
        """
        try:
            url = f"{self.BASE_URL}{self.ENDPOINTS['blood_center_directory']}"
            
            search_data = {
                'state': state,
                'district': district,
                'searchType': 'LOCATION'
            }
            
            if pincode:
                search_data['pincode'] = pincode
            
            async with self.session.post(url, data=search_data) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return await self._parse_blood_centers(html_content)
                else:
                    logger.error(f"Blood centers API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error finding blood centers: {str(e)}")
            return []
    
    async def get_blood_donation_camps(
        self, 
        state: str, 
        district: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming blood donation camps.
        
        Args:
            state: State name
            district: District name  
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            List of blood donation camp details
        """
        try:
            url = f"{self.BASE_URL}{self.ENDPOINTS['blood_camps']}"
            
            search_data = {
                'state': state,
                'district': district,
                'searchType': 'CAMPS'
            }
            
            if date_from:
                search_data['dateFrom'] = date_from
            if date_to:
                search_data['dateTo'] = date_to
            
            async with self.session.post(url, data=search_data) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return await self._parse_donation_camps(html_content)
                else:
                    logger.error(f"Donation camps API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting donation camps: {str(e)}")
            return []
    
    async def emergency_blood_search(
        self, 
        blood_group: str, 
        state: str, 
        district: str,
        urgency_level: str = "CRITICAL"
    ) -> Dict[str, Any]:
        """
        Emergency blood search with priority handling.
        
        Args:
            blood_group: Required blood group
            state: Patient's state
            district: Patient's district
            urgency_level: CRITICAL, HIGH, MEDIUM
            
        Returns:
            Comprehensive emergency response data
        """
        try:
            # Get blood availability
            blood_availability = await self.search_blood_availability(
                state, district, blood_group
            )
            
            # Get nearby blood centers
            blood_centers = await self.find_nearby_blood_centers(
                state, district
            )
            
            # Get upcoming camps (for potential donors)
            camps = await self.get_blood_donation_camps(state, district)
            
            # Process emergency response
            emergency_response = {
                "timestamp": datetime.now().isoformat(),
                "request_details": {
                    "blood_group": blood_group,
                    "location": f"{district}, {state}",
                    "urgency": urgency_level
                },
                "blood_availability": blood_availability,
                "nearby_blood_centers": blood_centers[:10],  # Top 10 nearest
                "upcoming_camps": camps[:5],  # Next 5 camps
                "emergency_contacts": await self._get_emergency_contacts(state, district),
                "recommendations": await self._generate_emergency_recommendations(
                    blood_group, blood_availability, blood_centers
                )
            }
            
            logger.info(f"Emergency blood search completed for {blood_group} in {district}, {state}")
            return emergency_response
            
        except Exception as e:
            logger.error(f"Emergency blood search failed: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "blood_availability": {"blood_banks": []},
                "nearby_blood_centers": [],
                "emergency_contacts": []
            }
    
    async def _parse_blood_availability(self, html_content: str) -> Dict[str, Any]:
        """Parse blood availability HTML response."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            blood_banks = []
            
            # Look for blood bank tables or result containers
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        blood_bank = {
                            "name": cells[0].get_text(strip=True),
                            "location": cells[1].get_text(strip=True),
                            "contact": cells[2].get_text(strip=True),
                            "availability": cells[3].get_text(strip=True),
                            "last_updated": cells[4].get_text(strip=True) if len(cells) > 4 else "N/A"
                        }
                        blood_banks.append(blood_bank)
            
            return {
                "total_banks": len(blood_banks),
                "blood_banks": blood_banks,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing blood availability: {str(e)}")
            return {"blood_banks": [], "error": "Parsing failed"}
    
    async def _parse_blood_centers(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse blood centers HTML response."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            centers = []
            
            # Look for blood center information
            center_divs = soup.find_all('div', class_=re.compile(r'blood.*center|center.*blood', re.I))
            
            for div in center_divs:
                center_info = div.get_text(strip=True)
                if center_info:
                    # Extract structured information
                    center = {
                        "name": self._extract_center_name(center_info),
                        "address": self._extract_address(center_info),
                        "phone": self._extract_phone(center_info),
                        "email": self._extract_email(center_info),
                        "timings": self._extract_timings(center_info)
                    }
                    centers.append(center)
            
            return centers
            
        except Exception as e:
            logger.error(f"Error parsing blood centers: {str(e)}")
            return []
    
    async def _parse_donation_camps(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse donation camps HTML response."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            camps = []
            
            # Look for camp information
            camp_tables = soup.find_all('table')
            for table in camp_tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 5:
                        camp = {
                            "date": cells[0].get_text(strip=True),
                            "time": cells[1].get_text(strip=True),
                            "venue": cells[2].get_text(strip=True),
                            "organizer": cells[3].get_text(strip=True),
                            "contact": cells[4].get_text(strip=True)
                        }
                        camps.append(camp)
            
            return camps
            
        except Exception as e:
            logger.error(f"Error parsing donation camps: {str(e)}")
            return []
    
    async def _get_emergency_contacts(self, state: str, district: str) -> List[Dict[str, str]]:
        """Get emergency contact numbers for the location."""
        # Standard emergency contacts
        emergency_contacts = [
            {"service": "National Emergency", "number": "108", "type": "ambulance"},
            {"service": "Blood Bank Emergency", "number": "1910", "type": "blood_bank"},
            {"service": "Health Ministry Helpline", "number": "1075", "type": "health"}
        ]
        
        # Add state-specific contacts if needed
        state_contacts = {
            "Delhi": [{"service": "Delhi Blood Bank", "number": "011-23379800", "type": "blood_bank"}],
            "Maharashtra": [{"service": "Mumbai Blood Bank", "number": "022-24177000", "type": "blood_bank"}],
            "Karnataka": [{"service": "Bangalore Blood Bank", "number": "080-26702676", "type": "blood_bank"}]
        }
        
        if state in state_contacts:
            emergency_contacts.extend(state_contacts[state])
        
        return emergency_contacts
    
    async def _generate_emergency_recommendations(
        self, 
        blood_group: str, 
        availability: Dict[str, Any], 
        centers: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate emergency action recommendations."""
        recommendations = []
        
        available_banks = availability.get("blood_banks", [])
        
        if available_banks:
            recommendations.append(f"✅ {len(available_banks)} blood banks have {blood_group} available")
            recommendations.append("📞 Contact the nearest blood bank immediately")
            recommendations.append("🚗 Arrange transportation to the blood bank")
        else:
            recommendations.append("⚠️ No immediate availability found in local blood banks")
            recommendations.append("📢 Consider expanding search to nearby districts")
            recommendations.append("🩸 Contact compatible blood group donors directly")
        
        if centers:
            recommendations.append(f"🏥 {len(centers)} blood centers available in your area")
        
        # Blood group compatibility recommendations
        compatible_groups = self._get_compatible_blood_groups(blood_group)
        if compatible_groups:
            recommendations.append(f"🔄 Also search for compatible groups: {', '.join(compatible_groups)}")
        
        recommendations.extend([
            "📱 Use eRaktkosh mobile app for real-time updates",
            "🆘 Call 108 for medical emergency assistance",
            "👥 Mobilize family and friends for donor search"
        ])
        
        return recommendations
    
    def _get_compatible_blood_groups(self, blood_group: str) -> List[str]:
        """Get compatible blood groups for emergency search."""
        compatibility_map = {
            "A+": ["A+", "A-", "O+", "O-"],
            "A-": ["A-", "O-"],
            "B+": ["B+", "B-", "O+", "O-"],
            "B-": ["B-", "O-"],
            "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],  # Universal recipient
            "AB-": ["A-", "B-", "AB-", "O-"],
            "O+": ["O+", "O-"],
            "O-": ["O-"]  # Can only receive O-
        }
        
        compatible = compatibility_map.get(blood_group, [])
        return [bg for bg in compatible if bg != blood_group]  # Exclude the original group
    
    def _extract_center_name(self, text: str) -> str:
        """Extract blood center name from text."""
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['blood bank', 'blood center', 'hospital']):
                return line.strip()
        return lines[0].strip() if lines else "Unknown Center"
    
    def _extract_address(self, text: str) -> str:
        """Extract address from text."""
        # Look for address patterns
        address_pattern = r'(?i)(address|add)[\s:]*([^\n]+)'
        match = re.search(address_pattern, text)
        return match.group(2).strip() if match else "Address not available"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text."""
        phone_pattern = r'(?i)(phone|tel|contact)[\s:]*([0-9\-\+\s\(\)]+)'
        match = re.search(phone_pattern, text)
        return match.group(2).strip() if match else "Phone not available"
    
    def _extract_email(self, text: str) -> str:
        """Extract email from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else "Email not available"
    
    def _extract_timings(self, text: str) -> str:
        """Extract working timings from text."""
        timing_pattern = r'(?i)(timing|hours|open)[\s:]*([^\n]+)'
        match = re.search(timing_pattern, text)
        return match.group(2).strip() if match else "Timings not available"


# Utility function for easy access
async def search_emergency_blood(
    blood_group: str, 
    state: str, 
    district: str, 
    urgency_level: str = "CRITICAL"
) -> Dict[str, Any]:
    """
    Quick emergency blood search function.
    
    Args:
        blood_group: Required blood group (A+, B+, O+, AB+, A-, B-, O-, AB-)
        state: Patient's state
        district: Patient's district
        urgency_level: CRITICAL, HIGH, MEDIUM
        
    Returns:
        Emergency response with blood availability and recommendations
    """
    async with ERaktkoshService() as service:
        return await service.emergency_blood_search(
            blood_group, state, district, urgency_level
        )