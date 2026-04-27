"""
OCR Processor - Extract contact information from images
Supports business cards, name tags, and document photos
"""

import re
import pytesseract
from PIL import Image
import io
from typing import Dict, List, Optional

class OCRProcessor:
    """Process images and extract contact information"""
    
    @staticmethod
    def extract_text_from_image(image_data: bytes) -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Extracted text from image
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            # Enhance image for better OCR
            image = image.convert('RGB')
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"OCR Error: {str(e)}")
    
    @staticmethod
    def parse_contact_info(text: str) -> Dict:
        """
        Parse contact information from extracted text
        
        Args:
            text: Extracted text from image
            
        Returns:
            Dictionary with extracted contact fields
        """
        contact = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'phone': '',
            'mobile': '',
            'company': '',
            'title': '',
            'raw_text': text
        }
        
        lines = text.strip().split('\n')
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group().lower()
        
        # Extract phone numbers
        phone_pattern = r'(\+?1?[\s\-\(]?\d{3}[\s\-\)]?\d{3}[\s\-]?\d{4}|1?\s?\(\d{3}\)\s?\d{3}[\s\-]?\d{4})'
        phone_matches = re.findall(phone_pattern, text)
        
        if phone_matches:
            # First phone is usually main, second is mobile/cell
            if len(phone_matches) >= 1:
                contact['phone'] = OCRProcessor._normalize_phone(phone_matches[0])
            if len(phone_matches) >= 2:
                contact['mobile'] = OCRProcessor._normalize_phone(phone_matches[1])
        
        # Extract company (look for common company indicators)
        company_patterns = [
            r'(?:at|from|company|corp|inc|llc|ltd)\s+([A-Z][A-Za-z\s&.,-]+)',
            r'^([A-Z][A-Za-z\s&.,-]+?)(?:\s+(?:Inc|Corp|LLC|Ltd|Company|Inc\.|Corp\.|LLC\.|Ltd\.))?$'
        ]
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Check if line looks like company name
            if any(keyword in line_clean.upper() for keyword in ['INC', 'CORP', 'LLC', 'LTD', 'COMPANY', 'SYSTEMS', 'SOLUTIONS', 'GROUP', 'ENTERPRISES']):
                contact['company'] = line_clean
                break
        
        # Extract job title (look for common titles)
        title_keywords = [
            'CEO', 'CTO', 'CFO', 'COO', 'President', 'Vice President', 'VP',
            'Director', 'Manager', 'Engineer', 'Developer', 'Architect', 'Designer',
            'Sales', 'Account Executive', 'Consultant', 'Lead', 'Senior', 'Junior',
            'Specialist', 'Analyst', 'Coordinator', 'Assistant', 'Support', 'Admin',
            'Operations', 'Finance', 'Marketing', 'Business Development'
        ]
        
        for line in lines:
            line_upper = line.strip().upper()
            for keyword in title_keywords:
                if keyword.upper() in line_upper:
                    contact['title'] = line.strip()
                    break
            if contact['title']:
                break
        
        # Extract names (usually first few lines without special characters)
        name_candidates = []
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if not line or len(line) < 2:
                continue
            if '@' in line or re.search(r'\d{3}[\s\-]?\d{3}[\s\-]?\d{4}', line):
                continue  # Skip email and phone lines
            if any(keyword in line.upper() for keyword in ['COMPANY', 'INC', 'CORP', 'LLC']):
                continue  # Skip company lines
            if re.match(r'^[A-Za-z\s\-\'\.]+$', line):  # Only letters and common name chars
                name_candidates.append(line)
        
        # Try to split first candidate into first and last name
        if name_candidates:
            first_candidate = name_candidates[0]
            parts = first_candidate.split()
            
            if len(parts) >= 2:
                contact['first_name'] = parts[0]
                contact['last_name'] = ' '.join(parts[1:])
            elif len(parts) == 1:
                contact['first_name'] = parts[0]
        
        return contact
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize phone number"""
        # Remove all non-digit characters except +
        normalized = re.sub(r'[^\d+]', '', phone)
        return normalized
    
    @staticmethod
    def confidence_score(contact: Dict) -> float:
        """
        Calculate confidence score for extracted contact (0.0 to 1.0)
        Higher score = more likely to be correct
        """
        score = 0.0
        max_score = 0.0
        
        # Email is highly reliable
        if contact.get('email'):
            score += 0.3
        max_score += 0.3
        
        # Name
        if contact.get('first_name'):
            score += 0.15
        max_score += 0.15
        
        if contact.get('last_name'):
            score += 0.15
        max_score += 0.15
        
        # Phone
        if contact.get('phone') or contact.get('mobile'):
            score += 0.15
        max_score += 0.15
        
        # Company
        if contact.get('company') and len(contact['company']) > 2:
            score += 0.1
        max_score += 0.1
        
        # Title
        if contact.get('title'):
            score += 0.15
        max_score += 0.15
        
        return score / max_score if max_score > 0 else 0.0


def process_image_file(file_path: str) -> Dict:
    """
    Process an image file and extract contact information
    
    Args:
        file_path: Path to image file
        
    Returns:
        Dictionary with extracted contact info
    """
    with open(file_path, 'rb') as f:
        image_data = f.read()
    
    processor = OCRProcessor()
    text = processor.extract_text_from_image(image_data)
    contact = processor.parse_contact_info(text)
    confidence = processor.confidence_score(contact)
    
    return {
        'contact': contact,
        'confidence': confidence,
        'extracted_text': text
    }
