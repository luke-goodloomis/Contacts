"""
Contact Management API - FastAPI Backend
Interactive web interface for viewing and updating contacts in real-time
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import sqlite3
from datetime import datetime
import os
import tempfile
from ocr_processor import OCRProcessor
from text_parser import parse_contact_text, TextParser

app = FastAPI(title="Contact Manager", version="1.0.0")

# Database configuration
DB_PATH = "contacts.db"
CONTACTS_JSON = "../all_contacts.json"

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================================
# DATA MODELS
# ============================================================================

class Contact(BaseModel):
    email: str
    first_name: str
    last_name: str
    company: str = ""
    phone: str = ""
    mobile: str = ""
    notes: str = ""
    updated_at: Optional[str] = None

class ContactUpdate(BaseModel):
    first_name: str = ""
    last_name: str = ""
    company: str = ""
    phone: str = ""
    mobile: str = ""
    notes: str = ""

class OCRResult(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    mobile: str = ""
    company: str = ""
    title: str = ""
    confidence: float = 0.0
    extracted_text: str = ""

class ParseRequest(BaseModel):
    text: str

class MergeContactRequest(BaseModel):
    existing_email: str
    updates: Dict[str, Any]
    merge_strategy: str = "selective"  # selective or overwrite

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize SQLite database from JSON data"""
    if os.path.exists(DB_PATH):
        return  # Already initialized
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create contacts table
    c.execute('''
        CREATE TABLE contacts (
            email TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            mobile TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create search index table
    c.execute('''
        CREATE TABLE search_index (
            id INTEGER PRIMARY KEY,
            email TEXT,
            full_text TEXT,
            FOREIGN KEY (email) REFERENCES contacts(email) ON DELETE CASCADE
        )
    ''')
    
    # Load contacts from JSON
    try:
        with open(CONTACTS_JSON, 'r', encoding='utf-8') as f:
            contacts_data = json.load(f)
        
        for email, contact in contacts_data.items():
            c.execute('''
                INSERT INTO contacts 
                (email, first_name, last_name, company, phone, mobile, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email,
                contact.get('first_name', ''),
                contact.get('last_name', ''),
                contact.get('company', ''),
                contact.get('phone', ''),
                contact.get('mobile', ''),
                ''
            ))
            
            # Add to search index
            full_text = f"{contact.get('first_name', '')} {contact.get('last_name', '')} {email} {contact.get('company', '')}".lower()
            c.execute('''
                INSERT INTO search_index (email, full_text)
                VALUES (?, ?)
            ''', (email, full_text))
        
        conn.commit()
        print(f"✓ Database initialized with {len(contacts_data)} contacts")
    except Exception as e:
        print(f"Error loading contacts from JSON: {e}")
    finally:
        conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    """Serve main HTML page"""
    return FileResponse("templates/index.html", media_type="text/html")

@app.get("/api/contacts")
async def list_contacts(
    skip: int = Query(0),
    limit: int = Query(100),
    search: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    sort_by: str = Query("last_name")
):
    """
    Get list of contacts with optional filtering and search
    """
    conn = get_db()
    c = conn.cursor()
    
    query = "SELECT * FROM contacts WHERE 1=1"
    params = []
    
    if search:
        # Search across email, names, and company
        search_term = f"%{search.lower()}%"
        query += " AND (LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ? OR LOWER(email) LIKE ? OR LOWER(company) LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term])
    
    if company:
        query += " AND LOWER(company) LIKE ?"
        params.append(f"%{company.lower()}%")
    
    # Validate sort_by to prevent SQL injection
    valid_sorts = ["first_name", "last_name", "email", "company", "updated_at"]
    if sort_by not in valid_sorts:
        sort_by = "last_name"
    
    query += f" ORDER BY {sort_by} ASC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    c.execute(query, params)
    contacts = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return {
        "total": len(contacts),
        "contacts": contacts,
        "skip": skip,
        "limit": limit
    }

@app.get("/api/contacts/{email}")
async def get_contact(email: str):
    """Get specific contact by email"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM contacts WHERE email = ?", (email.lower(),))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return dict(row)

@app.post("/api/contacts")
async def create_contact(contact: Contact):
    """Create new contact"""
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO contacts 
            (email, first_name, last_name, company, phone, mobile, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact.email.lower(),
            contact.first_name,
            contact.last_name,
            contact.company,
            contact.phone,
            contact.mobile,
            contact.notes
        ))
        
        # Add to search index
        full_text = f"{contact.first_name} {contact.last_name} {contact.email} {contact.company}".lower()
        c.execute('''
            INSERT INTO search_index (email, full_text)
            VALUES (?, ?)
        ''', (contact.email.lower(), full_text))
        
        conn.commit()
        conn.close()
        return {"status": "created", "email": contact.email.lower()}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="Contact already exists")

@app.put("/api/contacts/{email}")
async def update_contact(email: str, update: ContactUpdate):
    """Update existing contact"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if contact exists
    c.execute("SELECT * FROM contacts WHERE email = ?", (email.lower(),))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Update contact
    c.execute('''
        UPDATE contacts 
        SET first_name = ?, last_name = ?, company = ?, phone = ?, mobile = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE email = ?
    ''', (
        update.first_name,
        update.last_name,
        update.company,
        update.phone,
        update.mobile,
        update.notes,
        email.lower()
    ))
    
    # Update search index
    full_text = f"{update.first_name} {update.last_name} {email} {update.company}".lower()
    c.execute('''
        UPDATE search_index 
        SET full_text = ?
        WHERE email = ?
    ''', (full_text, email.lower()))
    
    conn.commit()
    conn.close()
    return {"status": "updated", "email": email.lower()}

@app.delete("/api/contacts/{email}")
async def delete_contact(email: str):
    """Delete contact"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("DELETE FROM contacts WHERE email = ?", (email.lower(),))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    
    conn.commit()
    conn.close()
    return {"status": "deleted", "email": email.lower()}

@app.get("/api/companies")
async def list_companies():
    """Get unique list of companies"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT company FROM contacts WHERE company != '' ORDER BY company")
    companies = [row[0] for row in c.fetchall()]
    conn.close()
    return {"companies": companies}

@app.get("/api/stats")
async def get_stats():
    """Get database statistics"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as total FROM contacts")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT company) as companies FROM contacts WHERE company != ''")
    companies = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) as with_phone FROM contacts WHERE phone != '' OR mobile != ''")
    with_phone = c.fetchone()[0]
    
    conn.close()
    
    return {
        "total_contacts": total,
        "companies": companies,
        "contacts_with_phone": with_phone
    }

@app.post("/api/export")
async def export_contacts():
    """Export all contacts as JSON"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM contacts")
    contacts = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return {
        "exported": datetime.now().isoformat(),
        "count": len(contacts),
        "contacts": contacts
    }

# ============================================================================
# OCR ENDPOINTS - IMAGE PROCESSING FOR CONTACT EXTRACTION
# ============================================================================

@app.post("/api/ocr/process")
async def process_image(file: UploadFile = File(...)):
    """
    Process image file (business card, name tag, etc.) and extract contact info
    
    Supported formats: JPG, PNG, GIF, TIFF, BMP
    """
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/tiff', 'image/bmp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Check file size (max 10MB)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Process image with OCR
        processor = OCRProcessor()
        text = processor.extract_text_from_image(contents)
        
        if not text.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text could be extracted from image. Try a clearer photo."
            )
        
        contact_data = processor.parse_contact_info(text)
        confidence = processor.confidence_score(contact_data)
        
        return {
            "success": True,
            "confidence": round(confidence * 100, 1),
            "first_name": contact_data.get('first_name', ''),
            "last_name": contact_data.get('last_name', ''),
            "email": contact_data.get('email', ''),
            "phone": contact_data.get('phone', ''),
            "mobile": contact_data.get('mobile', ''),
            "company": contact_data.get('company', ''),
            "title": contact_data.get('title', ''),
            "extracted_text": text[:500]  # First 500 chars of raw text
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/api/ocr/bulk-process")
async def bulk_process_images(files: List[UploadFile] = File(...)):
    """
    Process multiple images at once
    Returns list of extracted contacts
    """
    results = []
    errors = []
    
    for i, file in enumerate(files):
        try:
            contents = await file.read()
            processor = OCRProcessor()
            text = processor.extract_text_from_image(contents)
            contact_data = processor.parse_contact_info(text)
            confidence = processor.confidence_score(contact_data)
            
            results.append({
                "file": file.filename,
                "success": True,
                "confidence": round(confidence * 100, 1),
                "contact": {
                    "first_name": contact_data.get('first_name', ''),
                    "last_name": contact_data.get('last_name', ''),
                    "email": contact_data.get('email', ''),
                    "phone": contact_data.get('phone', ''),
                    "mobile": contact_data.get('mobile', ''),
                    "company": contact_data.get('company', ''),
                    "title": contact_data.get('title', '')
                }
            })
        except Exception as e:
            errors.append({
                "file": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

# ============================================================================
# TEXT PARSING ENDPOINTS - PASTE & PARSE CONTACT INGESTION
# ============================================================================

@app.post("/api/parse-contact")
async def parse_contact(request: ParseRequest):
    """
    Parse unformatted text and extract contact information
    Includes duplicate detection against existing contacts
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Please provide contact text to parse"
            )
        
        # Get database connection for duplicate checking
        conn = get_db()
        
        # Parse the contact text
        result = parse_contact_text(request.text, conn)
        contact = result['contact']
        duplicates = result['duplicates']
        
        # Calculate confidence score based on fields extracted
        confidence = _calculate_parse_confidence(contact)
        
        conn.close()
        
        return {
            "success": True,
            "confidence": round(confidence * 100, 1),
            "contact": contact,
            "duplicates": [
                {
                    "email": dup['email'],
                    "first_name": dup['first_name'],
                    "last_name": dup['last_name'],
                    "company": dup['company'],
                    "phone": dup['phone'],
                    "mobile": dup['mobile'],
                    "match_type": dup.get('match_type', 'unknown'),
                    "match_score": dup.get('match_score', 0)
                }
                for dup in duplicates
            ],
            "has_duplicates": len(duplicates) > 0
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing contact: {str(e)}"
        )

@app.post("/api/merge-contact")
async def merge_contact(request: MergeContactRequest):
    """
    Merge parsed contact data with existing contact
    Allows selective field updates
    """
    try:
        if not request.existing_email:
            raise HTTPException(
                status_code=400,
                detail="existing_email is required"
            )
        
        conn = get_db()
        c = conn.cursor()
        
        # Verify contact exists
        c.execute("SELECT * FROM contacts WHERE LOWER(email) = LOWER(?)", (request.existing_email,))
        existing = c.fetchone()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Determine which fields to update based on merge strategy
        if request.merge_strategy == "overwrite":
            # Update all provided fields
            update_fields = {}
            for field in ['first_name', 'last_name', 'company', 'phone', 'mobile', 'notes']:
                if field in request.updates and request.updates[field]:
                    update_fields[field] = request.updates[field]
        else:
            # selective - only update non-empty fields that are different from existing
            update_fields = {}
            for field in ['first_name', 'last_name', 'company', 'phone', 'mobile', 'notes']:
                if field in request.updates and request.updates[field]:
                    # Only update if different from existing value
                    existing_val = existing[field] or ''
                    new_val = request.updates[field] or ''
                    if new_val.lower() != existing_val.lower():
                        update_fields[field] = new_val
        
        if not update_fields:
            conn.close()
            return {
                "status": "no_changes",
                "email": request.existing_email.lower(),
                "message": "No changes to apply"
            }
        
        # Build update query dynamically
        set_clauses = []
        params = []
        for field, value in update_fields.items():
            set_clauses.append(f"{field} = ?")
            params.append(value)
        
        # Add updated timestamp
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(request.existing_email.lower())
        
        query = f"UPDATE contacts SET {', '.join(set_clauses)} WHERE LOWER(email) = LOWER(?)"
        c.execute(query, params)
        
        # Update search index
        updated_contact = dict(c.execute("SELECT * FROM contacts WHERE LOWER(email) = LOWER(?)", (request.existing_email,)).fetchone())
        full_text = f"{updated_contact['first_name']} {updated_contact['last_name']} {request.existing_email} {updated_contact['company']}".lower()
        c.execute(
            "UPDATE search_index SET full_text = ? WHERE email = ?",
            (full_text, request.existing_email.lower())
        )
        
        conn.commit()
        conn.close()
        
        return {
            "status": "updated",
            "email": request.existing_email.lower(),
            "fields_updated": list(update_fields.keys()),
            "message": f"Updated {len(update_fields)} fields"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error merging contact: {str(e)}"
        )

def _calculate_parse_confidence(contact: Dict) -> float:
    """Calculate confidence score for parsed contact"""
    confidence = 0.0
    
    # Email is highly reliable (30 points)
    if contact.get('email'):
        confidence += 0.30
    
    # Name is important (30 points)
    if contact.get('first_name'):
        confidence += 0.15
    if contact.get('last_name'):
        confidence += 0.15
    
    # Phone numbers (20 points)
    if contact.get('phone'):
        confidence += 0.10
    if contact.get('mobile'):
        confidence += 0.10
    
    # Company (15 points)
    if contact.get('company'):
        confidence += 0.15
    
    # Title (5 points)
    if contact.get('title'):
        confidence += 0.05
    
    return min(confidence, 1.0)  # Cap at 100%

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
