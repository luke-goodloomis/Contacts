# Paste & Parse Contact Feature - User Guide

## Overview

The **Paste & Parse** feature allows you to quickly add new contacts by simply copying and pasting text from emails, documents, business card scanners, or any other source. The system automatically:

1. **Parses** unformatted text into structured contact fields
2. **Detects duplicates** against existing contacts
3. **Handles merge conflicts** with clear resolution options
4. **Creates or updates** contacts with minimal effort

## Quick Start

### 1. Access the Paste Area

In the left sidebar under **"📋 Paste New Contact"**, you'll find a text area where you can paste contact information.

### 2. Paste Contact Text

Copy and paste any contact information you want to add. The feature handles various formats:

```
Name: John Smith
Email: john.smith@company.com
Phone: 555-123-4567
Mobile: 555-987-6543
Company: Tech Corp Inc
Title: Senior Engineer
```

Or copy directly from an email/document (less structured):

```
John Smith, Senior Engineer
john.smith@company.com
(D) 555-123-4567 | (M) 555-987-6543
Tech Corp Inc
```

### 3. Click "Parse & Check"

Click the **"Parse & Check"** button to parse the text. The system will:
- Extract all recognizable fields
- Check for potential duplicates in your contact database
- Show a confidence score for the extraction

### 4. Review Results

You'll see:
- **Parsed Contact Data**: All extracted fields with confidence score
- **Duplicate Warnings** (if any): Existing contacts that match on email, phone, or name
- **Action Buttons**: Create new or update existing

### 5. Choose Your Action

#### Option A: Create New Contact
Click **"+ Create New Contact"** to add this as a new contact to your database.

#### Option B: Update Existing Contact
If duplicates were found, you can:
1. Select "Select & Review" for any duplicate
2. Review field-by-field comparison
3. Choose which fields to update
4. Click "✓ Update Contact"

## Supported Formats

### Phone Numbers with Labels

The system recognizes phone labels to properly categorize numbers:

- **(D)** = Desk/Office phone → stored as "Phone"
- **(M)** = Mobile/Cell phone → stored as "Mobile"
- **(O)** = Office phone → stored as "Phone" (or Mobile if Phone exists)

Example:
```
(D) 206-829-7330 | (M) 206-794-0762 | (O) 206-256-0800
```

### Name Formats

Handles various name formats including:
- Simple: "John Smith"
- With credentials: "Megan Stewart PE, LEED AP"
- With titles: "Dr. Robert Johnson, Jr."
- With suffixes: "Sarah Jones III"

### Contact Information Extraction

The parser automatically detects and extracts:

| Field | Detection Method |
|-------|-----------------|
| **Email** | Standard email format (name@domain.com) |
| **Phone** | 10-digit numbers, various formatting |
| **Mobile** | Labeled (M) or second phone number |
| **Company** | Longest non-title line, usually at end |
| **Title** | Keywords: Director, Manager, Engineer, VP, CEO, etc. |
| **Credentials** | After commas in first line (PE, MBA, etc.) |

## Duplicate Detection

The system checks for three types of matches:

### 1. Email Match (100% confidence)
If the email address already exists in your database, it's a definite duplicate.

### 2. Phone Match (85% confidence)
If the phone or mobile number matches an existing contact.

### 3. Name Similarity (50-100% confidence)
Fuzzy matching for similar names (e.g., "Jon Smith" vs "John Smyth").

## Merge Options

When updating an existing contact:

### Selective Merge (Default)
- Only updates fields that you explicitly enter
- Preserves existing data unless you provide new values
- Safe - won't overwrite existing good data with blanks

### Overwrite Merge
- Replaces all fields with new values
- Use when you want complete replacement

## Examples

### Example 1: Simple Email Contact

**Pasted Text:**
```
John Doe
john@acme.com
555-1234
```

**Parsed Result:**
- ✓ First Name: John
- ✓ Last Name: Doe
- ✓ Email: john@acme.com
- ✓ Phone: 555-1234
- ✓ Confidence: 70%

**Action:** Create New Contact

---

### Example 2: Detailed Contact

**Pasted Text:**
```
Megan Stewart PE, LEED AP 
Principal
(D) 206-829-7330 | (M) 206-794-0762 | (O) 206-256-0800
Affiliated Engineers, Inc.
```

**Parsed Result:**
- ✓ First Name: Megan
- ✓ Last Name: Stewart
- ✓ Email: (not found)
- ✓ Phone: 206-829-7330 (from D)
- ✓ Mobile: 206-794-0762 (from M)
- ✓ Company: Affiliated Engineers, Inc.
- ✓ Title: LEED AP (credentials)
- ✓ Confidence: 70%

**Action:** Create New Contact (note: email not found, but other fields sufficient)

---

### Example 3: Duplicate Detection

**Pasted Text:**
```
John Smith
john.smith@company.com
Updated Mobile: 415-555-9999
Tech Corp
```

**Parsed Result:**
- Existing contact found with same email!
- ⚠️ **1 Duplicate Detected**
- Option to update existing with new mobile number

**Action:** Select "Select & Review" → Update Mobile field → "✓ Update Contact"

## Confidence Scoring

The confidence score (0-100%) indicates how completely the parser extracted information:

| Score | Quality | Typical Example |
|-------|---------|-----------------|
| 80-100% | Excellent | Email + Name + Phone + Company |
| 60-79% | Good | Name + Phone + Company (no email) |
| 40-59% | Fair | Name + Phone only |
| <40% | Poor | Incomplete data |

**Higher confidence means more fields were successfully extracted.**

## Tips for Best Results

✓ **Do:**
- Copy complete contact blocks from emails
- Include company names when possible
- Use phone numbers with labels when available
- Check for duplicates before creating new contacts

✗ **Don't:**
- Paste unrelated text mixed with contact info
- Expect perfect parsing of very unstructured text
- Ignore duplicate warnings
- Create duplicate entries when updating is available

## API Reference (For Developers)

### Parse Contact Endpoint

```http
POST /api/parse-contact
Content-Type: application/json

{
  "text": "Contact text to parse..."
}

Response:
{
  "success": true,
  "confidence": 85.5,
  "contact": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@example.com",
    "phone": "555-123-4567",
    "mobile": "555-987-6543",
    "company": "Example Corp",
    "title": "Manager"
  },
  "duplicates": [
    {
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Smith",
      "match_type": "email_exact",
      "match_score": 100.0
    }
  ],
  "has_duplicates": true
}
```

### Merge Contact Endpoint

```http
POST /api/merge-contact
Content-Type: application/json

{
  "existing_email": "john@example.com",
  "updates": {
    "phone": "555-999-9999",
    "mobile": "555-888-8888"
  },
  "merge_strategy": "selective"
}

Response:
{
  "status": "updated",
  "email": "john@example.com",
  "fields_updated": ["phone", "mobile"],
  "message": "Updated 2 fields"
}
```

## Troubleshooting

### Q: My contact didn't parse correctly
**A:** Try these steps:
1. Check for formatting - ensure contact info is on separate lines
2. Include an email if possible (improves parsing)
3. Use phone numbers with (D)/(M)/(O) labels for clarity
4. Review the confidence score - very low scores mean incomplete data

### Q: A duplicate was detected but I want to create as new
**A:** You can choose "Create New Contact" even if duplicates are found. The system will create a second entry (useful if you have multiple contacts with same name/email for different purposes).

### Q: The company name is wrong
**A:** The parser uses heuristics to distinguish between job titles and company names:
- Shorter lines with job-related keywords are treated as titles
- Longer lines are treated as company names
- Ensure company name is on its own line at the end

### Q: How do I update an existing contact?
**A:** Two options:
1. **Use Paste Feature**: Paste updated info, parser will detect duplicate, click "Select & Review" and update
2. **Manual Edit**: Click the contact in the list, click "Edit", update fields manually

## Mobile Friendly

The Paste & Parse feature is fully responsive and works on:
- Desktop browsers
- Tablets (landscape recommended for best experience)
- Mobile phones (portrait or landscape)

All modals, buttons, and text areas are touch-friendly.

## Keyboard Shortcuts

- **Escape** - Close any modal or dialog
- **Ctrl/Cmd + N** - Open new contact form
- **Ctrl/Cmd + F** - Focus search box

## Security & Privacy

- All parsing happens locally on your server
- Contact data never leaves your network
- No cloud processing or external API calls
- Duplicate detection works only against your local database

## Performance

- Parsing typically completes in <500ms
- Works smoothly with 1000+ existing contacts
- Duplicate detection optimized with indexed search

## What's Next?

Future enhancements planned:
- Batch import of multiple contacts at once
- CSV/Excel file import
- Contact photo storage
- Phone number standardization by country
- Automatic deduplication suggestions
- Integration with email/calendar

---

**Questions?** Check the main Contact Manager documentation or contact your administrator.
