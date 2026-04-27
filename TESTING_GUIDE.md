# OCR Feature - Testing & Demo Guide

## Pre-Flight Checklist

Before using the OCR feature, verify everything is set up:

```bash
cd J:\contacts\app
python verify_setup.py
```

Expected output:
- ✓ Python 3.8+ installed
- ✓ All dependencies installed (FastAPI, Uvicorn, Pytesseract, Pillow)
- ✓ Tesseract OCR found
- ✓ All required files present
- ✓ OCR module imports successfully

## Starting the Application

### Method 1: One-Click (Easiest)
```bash
Double-click: J:\contacts\app\START.bat
```

### Method 2: Manual Start
```bash
cd J:\contacts\app
python main.py
```

Browser should automatically open to `http://localhost:8000`

### Method 3: Network Access (Mobile/Other Devices)
```bash
# Get your computer's IP
ipconfig | findstr "IPv4"

# Start server accessible to network
cd J:\contacts\app
uvicorn main:app --host 0.0.0.0 --port 8000

# From mobile/other device: http://YOUR_IP_HERE:8000
```

## Testing the OCR Feature

### Test 1: Basic Business Card Scan

**Setup:**
1. Have a business card photo ready
2. Navigate to http://localhost:8000
3. Click "📸 Scan Card" button in header

**Steps:**
1. Click the dashed upload area or drag & drop image
2. Wait for processing (should take 2-5 seconds)
3. Review the extracted information
4. Verify confidence score
5. Click "✓ Import Contact"

**Expected Results:**
- All contact fields extracted
- Confidence score: 80-95% (good lighting, clear card)
- Can immediately search for contact

**Success Criteria:**
✓ Image uploads without error
✓ OCR processes within 5 seconds
✓ Contact appears in search results

---

### Test 2: Blurry/Low Quality Image

**Setup:**
1. Take a blurry photo of business card
2. Navigate to OCR modal
3. Upload blurry image

**Expected Results:**
- Lower confidence score (50-70%)
- Some fields may be missing or incorrect
- Warning that manual review recommended

**Success Criteria:**
✓ Still processes without crashing
✓ Shows low confidence score
✓ User can manually correct fields

---

### Test 3: Multiple Images (Bulk Processing)

**Via API (Advanced):**
```bash
curl -X POST http://localhost:8000/api/ocr/bulk-process \
  -F "files=@card1.jpg" \
  -F "files=@card2.jpg" \
  -F "files=@card3.jpg"
```

**Expected Response:**
```json
{
  "processed": 3,
  "failed": 0,
  "results": [
    {"file": "card1.jpg", "success": true, "confidence": 92.0},
    {"file": "card2.jpg", "success": true, "confidence": 87.5},
    {"file": "card3.jpg", "success": true, "confidence": 85.0}
  ],
  "errors": []
}
```

---

### Test 4: Different Image Formats

Test each format to ensure compatibility:

| Format | File | Expected | Status |
|--------|------|----------|--------|
| JPEG | card.jpg | ✓ Works | |
| PNG | card.png | ✓ Works | |
| GIF | card.gif | ✓ Works | |
| TIFF | card.tiff | ✓ Works | |
| BMP | card.bmp | ✓ Works | |

---

### Test 5: File Size Limits

**Test 1: File Under 10MB**
- Upload normal-sized image
- Expected: ✓ Processes normally

**Test 2: File Over 10MB**
- Try uploading large file
- Expected: ✗ Error message "File too large (max 10MB)"

**Test 3: File Near Limit (9.5MB)**
- Upload large but valid file
- Expected: ✓ Processes successfully

---

### Test 6: Mobile Device Testing

**Setup:**
1. Start server with `--host 0.0.0.0`
2. Get computer IP: `ipconfig | findstr "IPv4"`
3. Open mobile browser: `http://COMPUTER_IP:8000`

**Tests:**
1. Navigation - Can scroll contact list on mobile
2. OCR Modal - Modal fits on mobile screen
3. Upload - Can select photo from camera roll
4. Processing - Shows spinner while processing
5. Preview - Image preview is readable on mobile
6. Form - Can edit fields on mobile keyboard
7. Import - Successfully imports contact

**Expected:**
- All UI elements visible and functional
- Responsive design adapts to screen size
- Touch targets are appropriately sized

---

### Test 7: Error Handling

**Test Case 1: Unsupported Format**
```
Upload: document.pdf
Expected: Error "Unsupported file type"
Allowed: JPG, PNG, GIF, TIFF, BMP
```

**Test Case 2: Corrupted Image**
```
Upload: Corrupted JPG file
Expected: Error during OCR processing
Message: "Error processing image: [details]"
```

**Test Case 3: Image With No Text**
```
Upload: Blank image or pure photo
Expected: Error "No text could be extracted from image"
Suggestion: "Try a clearer photo"
```

**Test Case 4: Missing Required Fields**
```
Try importing: Contact with no email
Expected: Error "Email is required"
```

---

### Test 8: Data Quality Tests

**Test 1: Email Extraction**
```
Input Card Text: "john.smith@acmecorp.com"
Expected Output: "john.smith@acmecorp.com"
Status: ✓
```

**Test 2: Phone Number Variations**
```
Input Formats:
  - (555) 123-4567
  - 555-123-4567
  - 555.123.4567
  - +1 555 123 4567
  - 5551234567

Expected: All normalized to same format
Status: ✓
```

**Test 3: Name Parsing**
```
Input: "John David Smith"
Expected: First Name: "John", Last Name: "David Smith"
Status: ✓
```

**Test 4: Company Detection**
```
Input: "ACME Corporation Inc."
Expected: "ACME Corporation Inc."
Status: ✓
```

**Test 5: Title Recognition**
```
Input: "Senior Software Engineer"
Expected: Title field populated
Status: ✓
```

---

### Test 9: Confidence Scoring

| Test Case | Score | Interpretation |
|-----------|-------|-----------------|
| Clear business card | 90% | High - Import as-is |
| Partial text visible | 60% | Medium - Review fields |
| Blurry image | 40% | Low - Needs editing |
| Only company visible | 15% | Very Low - Needs major editing |
| All fields present | 100% | Perfect - Import immediately |

---

### Test 10: Integration Tests

**Test: New Contact Workflow**
1. Scan business card
2. Review OCR results
3. Import to database
4. Search for contact by name
5. Search by email
6. Search by company
7. Edit contact
8. Verify changes saved

**Test: Export Integration**
1. Import contacts via OCR
2. Export to Outlook CSV
3. Verify new contacts in export
4. Count total contacts

---

## Performance Benchmarks

### Expected Performance

| Operation | Expected Time | Acceptable Range |
|-----------|---------------|------------------|
| Single image OCR | 3-5 seconds | 2-10 seconds |
| API response | <500ms | <1000ms |
| Image upload | <100ms | <500ms |
| Database save | <100ms | <500ms |
| Search 1000 contacts | <100ms | <500ms |

### Load Testing

```bash
# Process 10 sequential images
time python -c "
for i in range(10):
    # Process image
    pass
"

# Expected: ~30-50 seconds total
```

---

## Debugging Tips

### View API Responses
```bash
# In browser console (F12), check network tab
# Look for /api/ocr/process requests
# View response JSON for debugging
```

### Check Server Logs
```bash
# Server logs will show:
# - File upload received
# - OCR processing started/finished
# - Parsing results
# - Confidence calculation
# - API response time
```

### Enable Verbose Logging
```python
# In main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test API Directly
```bash
# Using curl (Windows: install via Chocolatey or use Git Bash)
curl -X POST http://localhost:8000/api/ocr/process \
  -F "file=@business_card.jpg" \
  -H "Accept: application/json"
```

---

## Sample Test Data

### Business Card Template
```
John Smith
Senior Software Engineer

ACME Corporation
john.smith@acmecorp.com
(555) 123-4567 (office)
(555) 987-6543 (mobile)
```

### Expected Extraction
```
First Name: John
Last Name: Smith
Email: john.smith@acmecorp.com
Phone: (555) 123-4567
Mobile: (555) 987-6543
Company: ACME Corporation
Title: Senior Software Engineer
Confidence: 95%
```

---

## Troubleshooting During Testing

### Issue: No text extracted from clear image
**Solutions:**
- Ensure Tesseract is installed: `tesseract --version`
- Check image is actually a photo (not graphic)
- Try different image angle or lighting
- Try higher resolution image

### Issue: Wrong phone numbers extracted
**Causes:**
- Multiple numbers on card
- Phone format not standard
- Number mixed with other text

**Fix:**
- Manually edit in form before import
- Try better image crop
- Ensure clear separation between fields

### Issue: Company name not detected
**Causes:**
- Company name at bottom of card
- Using abbreviation instead of full name
- Special characters in company name

**Fix:**
- Manually enter in form
- Adjust parsing logic if pattern not recognized

---

## Performance Optimization Tips

### For Faster OCR:
1. Use lower resolution images (saves processing)
2. Crop to just business card area
3. Ensure good lighting
4. Use high contrast (black on white)

### For Better Accuracy:
1. High resolution images (300+ DPI)
2. Straight angle, no perspective distortion
3. Well-lit, no shadows
4. Sharp focus on text

---

## Success Criteria Checklist

- [ ] Server starts without errors
- [ ] Web interface loads at http://localhost:8000
- [ ] "📸 Scan Card" button visible
- [ ] Can upload image file
- [ ] OCR processes within 5 seconds
- [ ] Confidence score displays (0-100%)
- [ ] Form fields populate with extracted data
- [ ] Can manually edit fields
- [ ] Can import contact to database
- [ ] Imported contact searchable
- [ ] Works on mobile device
- [ ] Error messages are helpful
- [ ] Different image formats work
- [ ] File size limit enforced

---

## What to Do Next

1. ✓ Run verification: `python verify_setup.py`
2. ✓ Start server: `python main.py`
3. ✓ Test basic scan with business card
4. ✓ Test on mobile device
5. ✓ Test with various image types
6. ✓ Test error scenarios
7. ✓ Review confidence scores
8. ✓ Verify database integration
9. ✓ Test export to Outlook
10. ✓ Deploy to production if satisfied

---

**Test Version:** 1.0
**Date:** 2024
**Status:** Ready for testing
