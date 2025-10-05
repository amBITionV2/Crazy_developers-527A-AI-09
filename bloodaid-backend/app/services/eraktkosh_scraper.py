"""
eRaktKosh Website Scraper for Backup Data
Scrapes blood availability and blood bank information from eRaktKosh portal
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import json
import re
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from urllib.parse import urljoin, parse_qs, urlparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BloodBankInfo:
    """Data class for blood bank information"""
    name: str
    address: str
    contact: str
    email: str
    state: str
    district: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    blood_groups: List[str] = None
    is_government: bool = False

@dataclass
class BloodAvailability:
    """Data class for blood availability information"""
    blood_bank_name: str
    blood_group: str
    units_available: int
    last_updated: datetime
    contact: str
    address: str
    state: str
    district: str

class ERaktKoshScraper:
    """Scraper for eRaktKosh portal data"""
    
    BASE_URL = "https://eraktkosh.mohfw.gov.in"
    BLOOD_AVAILABILITY_URL = f"{BASE_URL}/BLDAHIMS/bloodbank/stockAvailability.cnt"
    BLOOD_BANK_DIRECTORY_URL = f"{BASE_URL}/BLDAHIMS/bloodbank/nearbyBBRed.cnt"
    DONATION_CAMPS_URL = f"{BASE_URL}/BLDAHIMS/bloodbank/campSchedule.cnt"
    
    # Indian states and UTs
    STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ]
    
    BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    def __init__(self):
        self.session = None
        self.last_scraped = None
        self.cache_duration = timedelta(minutes=30)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, url: str, method: str = "GET", data: Dict = None) -> str:
        """Make HTTP request with error handling"""
        try:
            if method.upper() == "POST":
                async with self.session.post(url, data=data) as response:
                    response.raise_for_status()
                    return await response.text()
            else:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    async def scrape_blood_availability(self, state: str = None, district: str = None, blood_group: str = None) -> List[BloodAvailability]:
        """Scrape blood availability data from eRaktKosh"""
        try:
            # First, get the initial page to understand the form structure
            html = await self._make_request(self.BLOOD_AVAILABILITY_URL)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to find and submit search form
            search_data = {}
            if state:
                search_data['state'] = state
            if district:
                search_data['district'] = district
            if blood_group:
                search_data['bloodGroup'] = blood_group
            
            # Submit search request if we have search criteria
            if search_data:
                search_html = await self._make_request(
                    self.BLOOD_AVAILABILITY_URL, 
                    method="POST", 
                    data=search_data
                )
                if search_html:
                    soup = BeautifulSoup(search_html, 'html.parser')
            
            return self._parse_blood_availability(soup)
            
        except Exception as e:
            logger.error(f"Error scraping blood availability: {str(e)}")
            return []
    
    def _parse_blood_availability(self, soup: BeautifulSoup) -> List[BloodAvailability]:
        """Parse blood availability from HTML"""
        availability_list = []
        
        try:
            # Look for tables with blood availability data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                headers = []
                
                # Get headers
                header_row = rows[0] if rows else None
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                # Process data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:  # Minimum required columns
                        try:
                            cell_data = [cell.get_text(strip=True) for cell in cells]
                            
                            # Try to extract structured data
                            availability = BloodAvailability(
                                blood_bank_name=cell_data[0] if len(cell_data) > 0 else "Unknown",
                                blood_group=self._extract_blood_group(cell_data),
                                units_available=self._extract_units(cell_data),
                                last_updated=datetime.now(),
                                contact=self._extract_contact(cell_data),
                                address=self._extract_address(cell_data),
                                state=self._extract_state(cell_data),
                                district=self._extract_district(cell_data)
                            )
                            
                            availability_list.append(availability)
                            
                        except Exception as e:
                            logger.warning(f"Error parsing availability row: {str(e)}")
                            continue
            
            # If no structured data found, try alternative parsing
            if not availability_list:
                availability_list = self._parse_unstructured_availability(soup)
                
        except Exception as e:
            logger.error(f"Error parsing blood availability HTML: {str(e)}")
        
        return availability_list
    
    def _extract_blood_group(self, cell_data: List[str]) -> str:
        """Extract blood group from cell data"""
        for cell in cell_data:
            for bg in self.BLOOD_GROUPS:
                if bg in cell:
                    return bg
        return "Unknown"
    
    def _extract_units(self, cell_data: List[str]) -> int:
        """Extract available units from cell data"""
        for cell in cell_data:
            # Look for numeric values
            numbers = re.findall(r'\d+', cell)
            if numbers:
                return int(numbers[0])
        return 0
    
    def _extract_contact(self, cell_data: List[str]) -> str:
        """Extract contact information"""
        for cell in cell_data:
            # Look for phone numbers
            phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
            if re.search(phone_pattern, cell):
                return cell
        return ""
    
    def _extract_address(self, cell_data: List[str]) -> str:
        """Extract address information"""
        # Usually the longest cell contains address
        longest_cell = max(cell_data, key=len) if cell_data else ""
        return longest_cell[:200]  # Limit length
    
    def _extract_state(self, cell_data: List[str]) -> str:
        """Extract state information"""
        for cell in cell_data:
            for state in self.STATES:
                if state.lower() in cell.lower():
                    return state
        return "Unknown"
    
    def _extract_district(self, cell_data: List[str]) -> str:
        """Extract district information"""
        # This is more challenging without a predefined list
        # Look for patterns that might indicate district
        for cell in cell_data:
            if len(cell) > 3 and len(cell) < 50 and not any(char.isdigit() for char in cell):
                return cell
        return "Unknown"
    
    def _parse_unstructured_availability(self, soup: BeautifulSoup) -> List[BloodAvailability]:
        """Parse availability data from unstructured HTML"""
        availability_list = []
        
        try:
            # Look for div elements or other containers with blood data
            content_divs = soup.find_all(['div', 'span', 'p'])
            
            for div in content_divs:
                text = div.get_text(strip=True)
                
                # Look for patterns that indicate blood availability
                if any(bg in text for bg in self.BLOOD_GROUPS) and any(char.isdigit() for char in text):
                    try:
                        blood_group = next((bg for bg in self.BLOOD_GROUPS if bg in text), "Unknown")
                        units = int(re.search(r'\d+', text).group()) if re.search(r'\d+', text) else 0
                        
                        availability = BloodAvailability(
                            blood_bank_name="Unknown",
                            blood_group=blood_group,
                            units_available=units,
                            last_updated=datetime.now(),
                            contact="",
                            address=text,
                            state="Unknown",
                            district="Unknown"
                        )
                        
                        availability_list.append(availability)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing unstructured availability: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in unstructured parsing: {str(e)}")
        
        return availability_list
    
    async def scrape_blood_banks(self, state: str = None, district: str = None) -> List[BloodBankInfo]:
        """Scrape blood bank directory from eRaktKosh"""
        try:
            html = await self._make_request(self.BLOOD_BANK_DIRECTORY_URL)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Submit search if criteria provided
            if state or district:
                search_data = {}
                if state:
                    search_data['state'] = state
                if district:
                    search_data['district'] = district
                
                search_html = await self._make_request(
                    self.BLOOD_BANK_DIRECTORY_URL,
                    method="POST",
                    data=search_data
                )
                if search_html:
                    soup = BeautifulSoup(search_html, 'html.parser')
            
            return self._parse_blood_banks(soup)
            
        except Exception as e:
            logger.error(f"Error scraping blood banks: {str(e)}")
            return []
    
    def _parse_blood_banks(self, soup: BeautifulSoup) -> List[BloodBankInfo]:
        """Parse blood bank information from HTML"""
        blood_banks = []
        
        try:
            # Look for tables with blood bank data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            cell_data = [cell.get_text(strip=True) for cell in cells]
                            
                            blood_bank = BloodBankInfo(
                                name=cell_data[0] if len(cell_data) > 0 else "Unknown",
                                address=cell_data[1] if len(cell_data) > 1 else "",
                                contact=self._extract_contact(cell_data),
                                email=self._extract_email(cell_data),
                                state=self._extract_state(cell_data),
                                district=self._extract_district(cell_data),
                                is_government=self._is_government_bank(cell_data)
                            )
                            
                            blood_banks.append(blood_bank)
                            
                        except Exception as e:
                            logger.warning(f"Error parsing blood bank row: {str(e)}")
                            continue
            
            # If no structured data, try alternative parsing
            if not blood_banks:
                blood_banks = self._parse_unstructured_blood_banks(soup)
                
        except Exception as e:
            logger.error(f"Error parsing blood banks HTML: {str(e)}")
        
        return blood_banks
    
    def _extract_email(self, cell_data: List[str]) -> str:
        """Extract email from cell data"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for cell in cell_data:
            match = re.search(email_pattern, cell)
            if match:
                return match.group()
        return ""
    
    def _is_government_bank(self, cell_data: List[str]) -> bool:
        """Check if blood bank is government"""
        gov_keywords = ['government', 'govt', 'municipal', 'district', 'state', 'central']
        text = ' '.join(cell_data).lower()
        return any(keyword in text for keyword in gov_keywords)
    
    def _parse_unstructured_blood_banks(self, soup: BeautifulSoup) -> List[BloodBankInfo]:
        """Parse blood bank data from unstructured HTML"""
        blood_banks = []
        
        try:
            # Look for lists or divs containing bank information
            content_elements = soup.find_all(['li', 'div', 'p'])
            
            for element in content_elements:
                text = element.get_text(strip=True)
                
                # Look for patterns that indicate blood bank information
                if len(text) > 20 and ('hospital' in text.lower() or 'blood' in text.lower() or 'bank' in text.lower()):
                    try:
                        blood_bank = BloodBankInfo(
                            name=text[:100],  # First part as name
                            address=text,
                            contact=self._extract_contact([text]),
                            email=self._extract_email([text]),
                            state=self._extract_state([text]),
                            district=self._extract_district([text]),
                            is_government=self._is_government_bank([text])
                        )
                        
                        blood_banks.append(blood_bank)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing unstructured blood bank: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in unstructured blood bank parsing: {str(e)}")
        
        return blood_banks
    
    async def get_all_blood_availability(self) -> List[BloodAvailability]:
        """Get blood availability for all states and blood groups"""
        all_availability = []
        
        try:
            # Get data for major states
            major_states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Uttar Pradesh"]
            
            for state in major_states:
                try:
                    state_availability = await self.scrape_blood_availability(state=state)
                    all_availability.extend(state_availability)
                    
                    # Add small delay to avoid overwhelming the server
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error getting availability for {state}: {str(e)}")
                    continue
            
            # Also try without state filter to get general data
            try:
                general_availability = await self.scrape_blood_availability()
                all_availability.extend(general_availability)
            except Exception as e:
                logger.error(f"Error getting general availability: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in get_all_blood_availability: {str(e)}")
        
        return all_availability
    
    async def get_all_blood_banks(self) -> List[BloodBankInfo]:
        """Get blood banks for all states"""
        all_blood_banks = []
        
        try:
            # Get data for major states
            major_states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Uttar Pradesh"]
            
            for state in major_states:
                try:
                    state_banks = await self.scrape_blood_banks(state=state)
                    all_blood_banks.extend(state_banks)
                    
                    # Add small delay
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error getting banks for {state}: {str(e)}")
                    continue
            
            # Also try without state filter
            try:
                general_banks = await self.scrape_blood_banks()
                all_blood_banks.extend(general_banks)
            except Exception as e:
                logger.error(f"Error getting general banks: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in get_all_blood_banks: {str(e)}")
        
        return all_blood_banks
    
    def to_dict(self, obj) -> Dict:
        """Convert dataclass to dictionary"""
        if hasattr(obj, '__dataclass_fields__'):
            return {
                field.name: getattr(obj, field.name) for field in obj.__dataclass_fields__.values()
            }
        return {}

# Test/Demo function
async def test_scraper():
    """Test the eRaktKosh scraper"""
    async with ERaktKoshScraper() as scraper:
        print("Testing eRaktKosh Scraper...")
        
        # Test blood availability
        print("\n=== Testing Blood Availability ===")
        availability = await scraper.scrape_blood_availability(state="Delhi")
        print(f"Found {len(availability)} availability records")
        
        if availability:
            for i, record in enumerate(availability[:3]):  # Show first 3
                print(f"{i+1}. {record.blood_bank_name} - {record.blood_group}: {record.units_available} units")
        
        # Test blood banks
        print("\n=== Testing Blood Banks ===")
        banks = await scraper.scrape_blood_banks(state="Delhi")
        print(f"Found {len(banks)} blood banks")
        
        if banks:
            for i, bank in enumerate(banks[:3]):  # Show first 3
                print(f"{i+1}. {bank.name} - {bank.address[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_scraper())