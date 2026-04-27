"""
Text Parser for Contact Information
Extracts contact data from unformatted text (pasted from emails, documents, etc.)
Handles various formats including credentials, phone labels (D/M/O), and company names
"""

import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import sqlite3

# Regular expressions for parsing
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
PHONE_LABEL_REGEX = r'\(([DMO])\)\s*(\+?\d[\d\s().-]{7,})'

class TextParser:
    """Parse unformatted contact text into structured contact data"""
    
    def __init__(self, db_connection=None):
        """
        Initialize parser
        
        Args:
            db_connection: Optional SQLite connection for duplicate detection
        """
        self.db_conn = db_connection
    
    def parse(self, text: str) -> Dict:
        """
        Parse unformatted text and extract contact information
        
        Args:
            text: Raw text containing contact information
            
        Returns:
            Dictionary with extracted contact data
        """
        if not text or not text.strip():
            return self._empty_contact()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
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
        
        # Extract email addresses first (easier to identify)
        emails = self._extract_emails(text)
        if emails:
            contact['email'] = emails[0].lower()
        
        # Parse phones with labels (D/M/O)
        labeled_phones = self._extract_labeled_phones(text)
        if labeled_phones:
            contact.update(labeled_phones)
        
        # If no labeled phones, try extracting plain phone numbers
        if not contact['phone'] and not contact['mobile']:
            phones = self._extract_phones(text)
            if len(phones) >= 1:
                contact['phone'] = phones[0]
            if len(phones) >= 2:
                contact['mobile'] = phones[1]
        
        # Extract name from first line (usually contains name and possibly credentials)
        if lines:
            name_and_title = self._parse_name_and_title(lines[0])
            contact['first_name'] = name_and_title['first_name']
            contact['last_name'] = name_and_title['last_name']
            if name_and_title['title']:
                contact['title'] = name_and_title['title']
        
        # Extract company from remaining lines
        company = self._extract_company(lines)
        if company:
            contact['company'] = company
        
        # If title wasn't found in first line, look for it in other lines
        if not contact['title']:
            title = self._extract_title(lines)
            if title:
                contact['title'] = title
        
        return contact
    
    def _empty_contact(self) -> Dict:
        """Return empty contact template"""
        return {
            'first_name': '',
            'last_name': '',
            'email': '',
            'phone': '',
            'mobile': '',
            'company': '',
            'title': '',
            'raw_text': ''
        }
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        return re.findall(EMAIL_REGEX, text)
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers in standard format"""
        matches = re.findall(PHONE_REGEX, text)
        phones = []
        for match in matches:
            phone = f"{match[0]}-{match[1]}-{match[2]}"
            if phone not in phones:
                phones.append(phone)
        return phones
    
    def _extract_labeled_phones(self, text: str) -> Dict[str, str]:
        """
        Extract phone numbers with labels (D=desk, M=mobile, O=office)
        Format: (D) 206-829-7330 | (M) 206-794-0762 | (O) 206-256-0800
        """
        result = {}
        
        # Find all labeled phone numbers
        matches = re.finditer(PHONE_LABEL_REGEX, text)
        
        for match in matches:
            label = match.group(1).upper()
            phone = self._normalize_phone(match.group(2))
            
            if not phone:
                continue
            
            if label == 'D':
                # D = Desk, typically goes to 'phone' field
                if not result.get('phone'):
                    result['phone'] = phone
            elif label == 'M':
                # M = Mobile, goes to 'mobile' field
                if not result.get('mobile'):
                    result['mobile'] = phone
            elif label == 'O':
                # O = Office, could be main company number
                # If no phone yet, use it as phone; otherwise mobile
                if not result.get('phone'):
                    result['phone'] = phone
                elif not result.get('mobile'):
                    result['mobile'] = phone
        
        return result
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to consistent format"""
        # Remove all non-digit characters except leading +
        normalized = re.sub(r'[^\d+]', '', phone)
        
        # If it looks like a standard 10-digit US number, format it
        if len(normalized) == 10 and not normalized.startswith('+'):
            return f"{normalized[0:3]}-{normalized[3:6]}-{normalized[6:10]}"
        
        return normalized if normalized else ''
    
    def _parse_name_and_title(self, first_line: str) -> Dict[str, str]:
        """
        Parse name and title from first line
        Examples:
        - "John Smith"
        - "Jane Doe, CEO"
        - "Megan Stewart PE, LEED AP"
        - "Dr. Robert Johnson, Jr."
        """
        result = {
            'first_name': '',
            'last_name': '',
            'title': ''
        }
        
        # Split by comma to separate name from credentials/title
        parts = first_line.split(',')
        name_part = parts[0].strip()
        
        # Extract credentials/title from comma-separated parts
        if len(parts) > 1:
            creds = [p.strip() for p in parts[1:]]
            result['title'] = ', '.join(creds)
        
        # Parse the name part
        # Remove common prefixes and suffixes
        name = self._clean_name(name_part)
        name_words = name.split()
        
        if len(name_words) >= 2:
            result['first_name'] = name_words[0]
            result['last_name'] = ' '.join(name_words[1:])
        elif len(name_words) == 1:
            result['first_name'] = name_words[0]
        
        return result
    
    def _clean_name(self, name: str) -> str:
        """Remove credentials and artifacts from name"""
        # Remove common credentials that might appear in the name
        credentials = [
            r'\b(PE|LEED|PMP|MBA|PhD|MD|JD|RN|CPA|CFA)\b',
            r'\b(AP|BD|BID|CSM|DAMA|CSCP|PgMP|SAFe|CISSP|Security\+)\b'
        ]
        
        for cred in credentials:
            name = re.sub(cred, '', name, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _extract_company(self, lines: List[str]) -> str:
        """Extract company name from lines"""
        # Company is usually a longer line that looks like a company name
        # Skip first line (has name), skip lines that are just numbers/emails/phones
        
        for i, line in enumerate(lines[1:], start=1):
            # Skip if it's an email, phone number, or has phone-like patterns
            if '@' in line or re.match(r'^\(?\d', line) or '|' in line or re.search(r'\(\w\)\s*\d', line):
                continue
            
            # Skip very short lines (likely titles)
            if len(line) < 4:
                continue
            
            # Skip lines that are all credentials or special characters
            if re.match(r'^[A-Z\s,\.]*$', line) and len(line) > 8:
                # This might be a company name (all caps with spaces/commas/dots)
                # But check if it looks like a title instead (like "Principal", "Director")
                title_words = ['principal', 'director', 'manager', 'engineer', 'consultant', 
                              'officer', 'executive', 'analyst', 'specialist', 'architect']
                line_lower = line.lower()
                is_title = any(word in line_lower for word in title_words)
                if not is_title:
                    return line
            
            # For non-title lines of reasonable length that don't match other patterns
            if len(line) > 6 and not re.match(r'^\d{3}', line):
                # Check if this looks like a title (single word or 2-3 words that are titles)
                title_words = ['principal', 'director', 'manager', 'engineer', 'consultant',
                              'officer', 'executive', 'analyst', 'specialist', 'architect',
                              'lead', 'supervisor', 'head', 'vice', 'president', 'ceo', 'cto', 'cfo',
                              'developer', 'designer', 'coordinator']
                line_lower = line.lower()
                word_count = len(line.split())
                
                # If it's a short phrase that's in the title list, it's likely a title
                if word_count <= 2 and any(word in line_lower for word in title_words):
                    continue
                
                # Otherwise, treat as potential company
                return line
        
        return ''
    
    def _extract_title(self, lines: List[str]) -> str:
        """Extract job title from lines"""
        # Look for lines that have common title patterns
        # Prefer shorter lines (more likely to be titles)
        title_keywords = [
            'director', 'manager', 'engineer', 'analyst', 'consultant',
            'officer', 'executive', 'principal', 'associate', 'specialist',
            'coordinator', 'lead', 'supervisor', 'head', 'vice', 'president',
            'ceo', 'cto', 'cfo', 'developer', 'architect', 'designer'
        ]
        
        candidates = []
        
        for line in lines[1:]:
            if len(line) < 3:
                continue
                
            line_lower = line.lower()
            
            # Check if line contains any title keywords
            for keyword in title_keywords:
                if keyword in line_lower:
                    # Shorter lines are more likely to be titles
                    word_count = len(line.split())
                    candidates.append((word_count, line))
                    break
        
        # Return the shortest candidate (most likely a title)
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        return ''
    
    def normalize_for_comparison(self, text: str) -> str:
        """Normalize text for duplicate comparison"""
        # Lowercase, remove extra spaces
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def find_duplicates(self, contact: Dict, db_conn) -> List[Dict]:
        """
        Find potential duplicate contacts in database
        Returns list of duplicates sorted by match quality (highest first)
        """
        duplicates = []
        
        if not db_conn:
            return duplicates
        
        try:
            c = db_conn.cursor()
            
            # Check 1: Email exact match (highest priority)
            if contact.get('email'):
                c.execute(
                    "SELECT * FROM contacts WHERE LOWER(email) = LOWER(?)",
                    (contact['email'],)
                )
                row = c.fetchone()
                if row:
                    dup = dict(row)
                    dup['match_type'] = 'email_exact'
                    dup['match_score'] = 100.0
                    duplicates.append(dup)
            
            # Check 2: Phone number exact match (after normalization)
            if contact.get('phone'):
                normalized_phone = self._normalize_phone(contact['phone'])
                if normalized_phone:
                    c.execute(
                        "SELECT * FROM contacts WHERE LOWER(REPLACE(REPLACE(REPLACE(phone, '-', ''), '(', ''), ')', '')) = LOWER(?)",
                        (normalized_phone,)
                    )
                    row = c.fetchone()
                    if row and row['email'] != contact.get('email'):  # Don't duplicate email matches
                        dup = dict(row)
                        dup['match_type'] = 'phone_exact'
                        dup['match_score'] = 85.0
                        duplicates.append(dup)
            
            # Check 3: Mobile number exact match
            if contact.get('mobile'):
                normalized_mobile = self._normalize_phone(contact['mobile'])
                if normalized_mobile:
                    c.execute(
                        "SELECT * FROM contacts WHERE LOWER(REPLACE(REPLACE(REPLACE(mobile, '-', ''), '(', ''), ')', '')) = LOWER(?)",
                        (normalized_mobile,)
                    )
                    row = c.fetchone()
                    if row and row['email'] != contact.get('email'):
                        dup = dict(row)
                        dup['match_type'] = 'mobile_exact'
                        dup['match_score'] = 85.0
                        # Check if already added via phone
                        if not any(d['email'] == dup['email'] for d in duplicates):
                            duplicates.append(dup)
            
            # Check 4: Fuzzy name matching
            if contact.get('first_name') and contact.get('last_name'):
                new_name = f"{contact['first_name']} {contact['last_name']}".lower()
                c.execute("SELECT * FROM contacts")
                
                for row in c.fetchall():
                    existing = dict(row)
                    if existing['email'] == contact.get('email'):
                        continue  # Already matched on email
                    
                    existing_name = f"{existing['first_name']} {existing['last_name']}".lower()
                    similarity = self._similarity_ratio(new_name, existing_name)
                    
                    # If names are very similar (>80% match), it's a potential duplicate
                    if similarity > 0.80:
                        # Check if already added
                        if not any(d['email'] == existing['email'] for d in duplicates):
                            dup = existing.copy()
                            dup['match_type'] = 'name_fuzzy'
                            dup['match_score'] = round(similarity * 100, 1)
                            duplicates.append(dup)
        
        except Exception as e:
            print(f"Error finding duplicates: {e}")
        
        # Sort by match score (highest first)
        duplicates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return duplicates
    
    def _similarity_ratio(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)"""
        return SequenceMatcher(None, a, b).ratio()


def parse_contact_text(text: str, db_conn=None) -> Dict:
    """
    Convenience function to parse contact text
    
    Args:
        text: Raw contact text
        db_conn: Optional SQLite connection for duplicate detection
        
    Returns:
        Dictionary with parsed contact data and potential duplicates
    """
    parser = TextParser(db_conn)
    contact = parser.parse(text)
    duplicates = parser.find_duplicates(contact, db_conn) if db_conn else []
    
    return {
        'contact': contact,
        'duplicates': duplicates,
        'has_duplicates': len(duplicates) > 0
    }
