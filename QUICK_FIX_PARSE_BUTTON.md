# Parse & Check Button - Quick Troubleshooting

## The Problem
Button click doesn't seem to do anything.

## The Likely Culprit
**Browser cache** - Your browser has cached an old version of the JavaScript file

## The Fix (2 steps)

### Step 1: Clear Cache with Hard Refresh
**Do this first:**

**Windows/Linux:**
```
Press: Ctrl + Shift + R
(or try: Ctrl + F5)
```

**Mac:**
```
Press: Cmd + Shift + R
```

This forces the browser to:
- Download fresh JavaScript
- Forget the old cached version
- Reload the page

### Step 2: Test the Button
After the hard refresh:

1. **Paste text** in the "📋 Paste New Contact" box (left sidebar)
   - Example: `John Smith\njohn@test.com\n555-1234567`

2. **Click "Parse & Check"** button

3. **What you should see:**
   - A popup alert that says: `DEBUG: Parse button was clicked!`

## What This Means

| What You See | What It Means |
|---|---|
| ✓ Alert appears | Button works! Cache was the issue. |
| ✗ No alert | Button not responding. Need deeper debug. |

## If No Alert Appears

Try these alternatives:

**Option 1: Full cache clear**
- Open Settings/Preferences
- Find "Clear browsing data" or "Clear cache"
- Select "All time" or "Everything"
- Restart browser
- Go to http://localhost:8000

**Option 2: Private/Incognito window**
- Open new private window
- Go to http://localhost:8000
- Test the button there
- (Private windows don't cache)

**Option 3: Different browser**
- Try Chrome, Firefox, Edge, or Safari
- See if button works in another browser

## If Alert DOES Appear

Great! That means:
- The button is wired correctly ✓
- The function is being called ✓
- Any other issues are deeper in the code

Next, check for errors:
1. Open Developer Console (F12)
2. Go to "Console" tab
3. Click "Parse & Check" again
4. Look for red error messages

## Still Not Working?

1. Make sure you did a **hard refresh** (not just regular refresh)
2. Check that http://localhost:8000 is the correct address
3. Try a different browser
4. Restart your browser completely

Once the alert appears, we can debug the next step!

---

**Key Point:** The alert `'DEBUG: Parse button was clicked!'` is the proof that everything is wired correctly. If you see it, the rest will work!
