# Contact Manager with OCR - Quick Start Guide

## Overview
This is a full-featured contact management web application with real-time editing and **optical character recognition (OCR) for extracting contacts from images** like business cards and name tags. The app is accessible from desktop and mobile devices.

## Features
- 📇 **View & Search Contacts** - Real-time search, filter by company, sort options
- ✏️ **CRUD Operations** - Create, edit, delete contacts in real-time
- 📸 **OCR Image Processing** - Extract contact info from business cards, name tags, documents
- 📱 **Mobile Friendly** - Responsive design works on phones and tablets
- 🌐 **Web-Based** - Access from any device on your network
- 🔍 **Smart Parsing** - Automatically parses names, emails, phone numbers, company info
- 📊 **Advanced Search** - Search across email, names, company

## Installation & Setup

### Prerequisites
- Python 3.8+
- Tesseract OCR engine (required for image processing)
- pip (Python package manager)

### Step 1: Install Python Dependencies
```bash
cd J:\contacts\app
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR (Windows)
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default path: `C:\Program Files\Tesseract-OCR`)
3. The system will find it automatically

**Alternative (if not found):** Add this line to `main.py` before imports:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Step 3: Verify Installation
```bash
python -c "from PIL import Image; import pytesseract; print('✓ OCR ready!')"
```

## Running the Application

### Local Server (Desktop)
```bash
cd J:\contacts\app
python main.py
```

Then open your browser to: **http://localhost:8000**

### Network Access (Mobile Devices)
1. Get your computer's IP address:
   ```bash
   ipconfig | findstr "IPv4"
   ```

2. Start server accessible to network:
   ```bash
   cd J:\contacts\app
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. On mobile, go to: `http://<YOUR_IP>:8000`
   - Example: `http://192.168.1.100:8000`

### Remote Access (Across Internet)
To access from outside your network, use ngrok tunnel:

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# You'll get a URL like: https://abcd1234.ngrok.io
# Use this URL on any device across the internet
```

## Using OCR Feature

### Extract Contact from Business Card
1. Click **📸 Scan Card** button in top menu
2. Either:
   - Click the dashed box to select image from device
   - Drag & drop an image onto the box
3. Wait for OCR processing (usually <5 seconds)
4. Review extracted information
5. Adjust any fields as needed
6. Click **✓ Import Contact** to save

### Image Tips for Best Results
- **Lighting:** Use good lighting, avoid shadows
- **Angle:** Hold camera perpendicular to card/tag
- **Focus:** Ensure text is sharp and readable
- **Contrast:** Black text on white background works best
- **Formats:** JPG, PNG, GIF, TIFF, BMP (max 10MB)

### Confidence Score
- **80-100%:** High confidence, likely accurate
- **50-79%:** Medium confidence, review before importing
- **<50%:** Low confidence, may need significant corrections

The confidence score indicates how many contact fields were successfully extracted.

## Using Contact Manager

### Search & Filter
- **Real-time Search:** Type in search box to find contacts by email, name, or company
- **Company Filter:** Dropdown to show only contacts from specific company
- **Sort Options:** Click column headers to sort

### Create New Contact
1. Press **Ctrl+N** or click **+ New Contact**
2. Fill in contact information
3. Email is required (acts as unique identifier)
4. Click **Save Contact**

### Edit Existing Contact
1. Click on any contact in the list
2. Click **Edit** in details panel
3. Modify information
4. Click **Save Contact**

### Delete Contact
1. Open contact and click **Edit**
2. Click **Delete** button (red)
3. Confirm deletion

### Keyboard Shortcuts
- **Ctrl+N**: New contact
- **Escape**: Close modal or details panel
- **Ctrl+F**: Focus search box

## Database

### File Locations
- **contacts.db** - SQLite database (created automatically)
- **all_contacts.json** - Master JSON backup (imported on first startup)
- **contacts_for_outlook.csv** - Outlook-compatible export

### Schema
```
contacts table:
  - email (TEXT, PRIMARY KEY)
  - first_name, last_name (TEXT)
  - company (TEXT)
  - phone, mobile (TEXT)
  - notes (TEXT)
  - created_at, updated_at (TIMESTAMP)
```

## API Reference

### Core Endpoints
```
GET  /api/contacts              - List all contacts
GET  /api/contacts/{email}      - Get specific contact
POST /api/contacts              - Create new contact
PUT  /api/contacts/{email}      - Update contact
DELETE /api/contacts/{email}    - Delete contact
```

### Search & Filter
```
GET /api/contacts?search=query     - Search contacts
GET /api/contacts?company=acme     - Filter by company
GET /api/contacts?sort=name        - Sort results
```

### OCR Endpoints
```
POST /api/ocr/process              - Process single image
POST /api/ocr/bulk-process         - Process multiple images
```

### Utilities
```
GET /api/companies                 - List all companies
GET /api/stats                     - Get statistics
POST /api/export                   - Export all contacts
```

## Troubleshooting

### OCR Not Working
1. **Verify Tesseract installation:**
   ```bash
   tesseract --version
   ```
2. **If not found,** install from: https://github.com/UB-Mannheim/tesseract/wiki
3. **Update pytesseract path in main.py if needed**

### Image Upload Errors
- **File too large:** Max 10MB, compress image first
- **Unsupported format:** Use JPG, PNG, GIF, TIFF, or BMP
- **No text found:** Try different angle, lighting, or higher resolution

### Port Already in Use
```bash
# Use different port
uvicorn main:app --port 8001

# Then access: http://localhost:8001
```

### Mobile Device Can't Connect
1. Ensure phone is on same WiFi as computer
2. Check firewall isn't blocking port 8000
3. Try pinging computer from phone
4. Use correct IP address format (no "localhost")

## Performance Notes
- **1000 contacts:** Loads in <1 second
- **OCR processing:** 2-5 seconds per image depending on resolution
- **Mobile performance:** Optimized for phones, works offline when cached
- **Search:** Real-time with <100ms response time

## Security Considerations
- Application is **not encrypted** by default
- For sensitive data, use VPN for remote access
- Don't share ngrok URLs publicly
- Consider firewall rules for network access
- No authentication layer currently implemented

## Advanced Configuration

### Custom Tesseract Path (if not auto-detected)
Edit `ocr_processor.py` line 20:
```python
pytesseract.pytesseract_pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Adjust OCR Confidence Threshold
Edit `ocr_processor.py` `confidence_score()` function to weight fields differently.

### Change Database Location
Edit `main.py` line 19:
```python
DB_PATH = "path/to/your/contacts.db"
```

## Backup & Restore

### Backup Contacts
```bash
# Export to JSON (manual backup)
curl http://localhost:8000/api/export > backup.json

# Or copy the database file
copy contacts.db backup.db
```

### Restore Contacts
```bash
# Replace contacts.db with backup
copy backup.db contacts.db

# Restart server
```

## Accessing on Mobile from Internet

### Option 1: ngrok (Recommended for Testing)
```bash
ngrok http 8000
# Share the HTTPS URL with anyone
```

### Option 2: Port Forwarding (Advanced)
1. Log into router admin panel
2. Forward port 8000 to your computer's local IP
3. Find your public IP: https://whatismyipaddress.com/
4. Access from: `http://YOUR_PUBLIC_IP:8000`

### Option 3: VPN
1. Set up VPN on computer
2. Connect from phone to same VPN
3. Access via local IP on VPN network

## Tips & Best Practices

1. **Business Cards:** Good lighting, straight angle works best
2. **Name Tags:** Ensure name is in focus, crop if needed
3. **Documents:** High resolution photos preferred
4. **Corrections:** Always review OCR results before importing
5. **Duplicates:** Search before importing to avoid duplicates
6. **Mobile:** Use portrait orientation for phone camera

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console for JavaScript errors (F12)
3. Check server logs for API errors
4. Verify file formats and sizes

## Version Information
- **FastAPI:** 0.104.1
- **Tesseract OCR:** Latest
- **Python:** 3.8+
- **Updated:** 2024

---

**Happy scanning! 📸 📇**
