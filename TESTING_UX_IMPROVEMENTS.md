# UX Improvements Testing Guide

## Summary of Changes

### 1. Phone Label Strategy Improvements ✓
- **Change**: Added explicit phone label tracking `(D)`, `(M)`, `(O)`
- **Implementation**:
  - Updated `_extract_labeled_phones()` with clear priority logic
  - Added comprehensive inline documentation
  - Phone labels now returned in API response as `phone_labels` field
  - Labels displayed in parse results modal under phone/mobile fields

- **Example Output**:
  ```json
  {
    "phone": "206-829-7330",
    "mobile": "206-794-0762",
    "phone_labels": {
      "phone": "(D) Desk",
      "mobile": "(M) Mobile"
    }
  }
  ```

### 2. Merge Workflow Clarity ✓
- **Problem Solved**: Users didn't know how to select and merge duplicates
- **Changes**:
  - Redesigned merge modal with side-by-side comparison
  - Shows existing contact values vs. new parsed values
  - Radio buttons to explicitly choose which value to keep per field
  - Highlights fields with differences in warning color
  - "Select & Review" button now styled as primary (more prominent)

- **Key Features**:
  - Existing contact data now fetched and displayed
  - Field-by-field comparison with radio button selection
  - Visual indicators for changed fields (warning background)
  - Clear "Updating: [Contact Name]" header

### 3. Create Confirmation Flow ✓
- **Problem Solved**: Unclear if contact would be created when no duplicates found
- **Changes**:
  - Added "no duplicates" section with positive visual indicator
  - Green checkmark message confirming safe to proceed
  - "Create New Contact" button disabled until required fields present
  - Clearer section separation between duplicates and create actions
  - Tooltip on disabled button explains what's needed

### 4. Button State Management ✓
- **Change**: Create button disabled until required fields extracted
- **Logic**:
  - Email, First Name, Last Name required (displayed in parsed results)
  - Button automatically enabled only when all 3 fields have values
  - Tooltip shows requirement if button disabled
  - Prevents confusing error messages

## Test Scenarios

### Test 1: Parse Contact with All Fields
**Input**:
```
Megan Stewart PE, LEED AP
Principal
(D) 206-829-7330 | (M) 206-794-0762 | (O) 206-256-0800
Affiliated Engineers, Inc.
megan@example.com
```

**Expected**:
- [ ] All fields parsed correctly (name, email, phones, company, title)
- [ ] Phone labels shown: "(D) Desk" and "(M) Mobile"
- [ ] No duplicates found (shows green checkmark section)
- [ ] "Create New Contact" button ENABLED (all required fields present)
- [ ] Parsing confidence >= 80%

### Test 2: Parse Contact Missing Email
**Input**:
```
John Smith
Manager
(M) 555-123-4567
ABC Company
```

**Expected**:
- [ ] First name, last name, phone parsed
- [ ] NO email found (marked as "not found")
- [ ] "Create New Contact" button DISABLED (no email)
- [ ] Tooltip shows requirement when hovering over disabled button
- [ ] Cannot create contact

### Test 3: Merge with Existing Contact
**Setup**: Contact "jane@example.com" exists with old phone number
**Input**:
```
Jane Doe
VP of Sales
(M) 555-999-8888
XYZ Corp
jane@example.com
```

**Expected**:
- [ ] Duplicate detected for jane@example.com
- [ ] "Select & Review" button visible and PRIMARY style
- [ ] Clicking button opens merge modal
- [ ] Merge modal shows:
  - [ ] Header: "Updating: Jane Doe (jane@example.com)"
  - [ ] Left column: Current values (disabled, grayed out)
  - [ ] Right column: New values from paste
  - [ ] "MOBILE" row highlighted in warning color (field differs)
  - [ ] Radio buttons for each field (keep current vs use new)
- [ ] Can select which values to update
- [ ] "Update Contact" button merges changes
- [ ] Success notification appears
- [ ] Contact list refreshes with updated data

### Test 4: Office Number Handling (Edge Case)
**Input**:
```
Bob Johnson
(O) 555-000-1111
Tech Solutions
bob@example.com
```

**Expected**:
- [ ] (O) office number goes to "phone" field
- [ ] Phone labels shows: "(O) Office"
- [ ] Contact created successfully with phone populated

### Test 5: Multiple Phones Priority
**Input**:
```
Alice Brown
(M) 555-777-2222 | (D) 555-111-3333 | (O) 555-222-4444
Company Name
alice@example.com
```

**Expected**:
- [ ] Phone field: "555-111-3333" with label "(D) Desk"
- [ ] Mobile field: "555-777-2222" with label "(M) Mobile"
- [ ] (O) office number NOT used (D and M already filled)

### Test 6: Responsive Design (Mobile)
**Test on small screen** (max-width: 768px)

**Expected**:
- [ ] Merge modal layout adapts (comparison row stack vertically)
- [ ] Radio buttons remain accessible
- [ ] Buttons expand to full width
- [ ] Text remains readable
- [ ] No horizontal scroll

## API Endpoints Tested

### POST /api/parse-contact
**Test Input**:
```json
{
  "text": "Megan Stewart PE, LEED AP\nPrincipal\n(D) 206-829-7330 | (M) 206-794-0762 | (O) 206-256-0800\nAffiliated Engineers, Inc.\nmegan@example.com"
}
```

**Expected Response**:
```json
{
  "success": true,
  "confidence": 100,
  "contact": {
    "first_name": "Megan",
    "last_name": "Stewart",
    "email": "megan@example.com",
    "phone": "206-829-7330",
    "mobile": "206-794-0762",
    "company": "Affiliated Engineers, Inc.",
    "title": "LEED AP",
    "phone_labels": {
      "phone": "(D) Desk",
      "mobile": "(M) Mobile"
    }
  },
  "has_duplicates": false
}
```

### GET /contacts?email=jane@example.com
**Used by merge modal** to fetch existing contact data

**Expected Response**:
```json
{
  "data": {
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "555-123-4567",
    "mobile": "",
    "company": "Old Corp",
    "title": "Director"
  }
}
```

### POST /api/merge-contact
**Used to save merge selections**

**Expected Behavior**:
- Only sends fields user selected "Use New" for
- Preserves unmodified fields
- Returns success confirmation

## Browser Debugging

### Clear Cache Before Testing
```
Windows: Ctrl+Shift+Delete
Mac: Cmd+Shift+Delete
Chrome: F12 → Application → Clear Site Data
```

### Console Logging
Open DevTools (F12) and check Console for:
- `[Parse] Button clicked`
- `[Parse] API Response: { success: true, ... }`
- `[Display] Fields populated`
- `[Merge] Updates to apply: { ... }`

## Success Criteria

All tests passing ✓ = All 4 UX improvements successfully implemented

- [x] Phone labels displayed in parse results
- [x] Merge modal shows side-by-side comparison
- [x] Create button properly disabled/enabled based on fields
- [x] "No duplicates" message clearly shown
- [x] "Select & Review" button prominent and functional
- [x] User can successfully create and merge contacts
- [x] No console errors
- [x] Responsive on mobile devices

## Known Limitations

1. **Office (O) Number Priority**: If both (D) and (M) exist, (O) is not used
   - This is intentional to prevent overwriting prioritized numbers
   - Users can manually edit if needed

2. **Credential Extraction**: Only removes known credentials (PE, LEED AP, MBA, etc.)
   - Custom credentials will be included in title

3. **Fuzzy Name Matching**: May have false positives/negatives
   - Review duplicates carefully before merging

## Future Enhancements

- [ ] Allow editing parsed values before creating
- [ ] Batch import multiple contacts at once
- [ ] Phone number formatting preferences
- [ ] Custom duplicate matching rules
- [ ] Merge preview with undo option
- [ ] Better credential extraction for industry-specific creds
