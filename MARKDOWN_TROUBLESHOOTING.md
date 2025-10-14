# 🔧 Markdown Rendering - Troubleshooting Guide

## ❓ Issue: "Output is still in markdown format"

If you're still seeing markdown syntax (like `###`, `**text**`, etc.) instead of formatted content, follow these steps:

---

## ✅ Solution Steps

### Step 1: Hard Refresh Your Browser

**Reason**: Your browser may have cached the old JavaScript files.

**How to do it**:

| Browser | Windows | Mac |
|---------|---------|-----|
| Chrome | `Ctrl + Shift + R` | `Cmd + Shift + R` |
| Firefox | `Ctrl + F5` | `Cmd + Shift + R` |
| Edge | `Ctrl + F5` | `Cmd + Shift + R` |
| Safari | N/A | `Cmd + Option + E` then refresh |

**Alternative**: Clear browser cache manually:
1. Open Developer Tools (F12)
2. Right-click the refresh button
3. Click "Empty Cache and Hard Reload"

---

### Step 2: Restart the Chatbot Server

**Reason**: Ensure the server is serving the latest files.

```bash
# Stop the server (Ctrl+C if running)

# Start fresh
python quick_start_openai.py
```

---

### Step 3: Verify marked.js is Loading

1. Open the chatbot in your browser: http://localhost:3000
2. Press `F12` to open Developer Tools
3. Go to the **Console** tab
4. Look for these messages:
   - ✅ `"marked.js loaded successfully"`
   - ✅ `"Parsing markdown with marked.js"`

**If you see**:
- ❌ `"Waiting for marked.js..."` → Network issue, check internet connection
- ❌ `"Using fallback markdown parser"` → marked.js didn't load, but fallback will work

---

### Step 4: Check Network Tab

1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Refresh the page (`Ctrl + R`)
4. Look for `marked.min.js` in the list
5. Click on it

**Should see**:
- ✅ Status: 200 OK
- ✅ Size: ~35 KB

**If you see**:
- ❌ Status: 404 → CDN issue
- ❌ Failed/Blocked → Firewall/antivirus blocking it

---

### Step 5: Test with a Sample Question

Ask the chatbot:
```
"Tell me about the co-op program"
```

**Expected Output**: Should see:
- ✅ Large red heading for "Overview"
- ✅ Bold text highlighted in red
- ✅ Bullet points properly formatted
- ✅ Clear sections and structure

**If you still see markdown**:
```
### Overview
**co-op program**
- Item 1
```
→ Continue to Step 6

---

### Step 6: Check Console for Errors

1. Open Developer Tools (F12)
2. Go to **Console** tab
3. Look for red error messages

**Common Errors & Solutions**:

#### Error: "marked is not defined"
**Solution**: marked.js didn't load
```html
<!-- Verify this line exists in frontend/index.html -->
<script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
```

#### Error: "parseMarkdown is not a function"
**Solution**: JavaScript file not updated properly
- Re-download or re-copy the updated `script.js`

#### Error: "Cannot read property 'innerHTML'"
**Solution**: DOM element issue
- Hard refresh the browser

---

### Step 7: Manual Verification

Check if files are updated:

#### Check `index.html`:
```bash
# Should contain this line:
grep "marked" frontend/index.html
```

**Expected output**:
```html
<script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
```

#### Check `script.js`:
```bash
# Should contain parseMarkdown function:
grep "parseMarkdown" frontend/script.js
```

**Expected output**: Should show the function exists

#### Check `styles.css`:
```bash
# Should contain markdown-content styles:
grep "markdown-content" frontend/styles.css
```

**Expected output**: Should show CSS rules

---

### Step 8: Test Without Cache

**Use Incognito/Private Mode**:

1. Open browser in **Incognito/Private** mode:
   - Chrome: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`
   - Edge: `Ctrl + Shift + N`

2. Go to: http://localhost:3000

3. Test a question

**If it works in Incognito**:
- ✅ Issue was browser cache
- Solution: Clear cache in normal browser

**If it still doesn't work**:
- Continue to Step 9

---

### Step 9: Verify File Contents

Read the actual files to ensure they're updated:

#### `frontend/index.html` (line 11-12):
```html
<!-- Marked.js for Markdown parsing -->
<script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
```

#### `frontend/script.js` (around line 203-248):
```javascript
parseMarkdown(text) {
    // Try using marked.js if available
    if (typeof marked !== 'undefined' && this.markdownReady) {
        try {
            console.log('Parsing markdown with marked.js');
            return marked.parse(text);
        }
        // ... rest of function
    }
}
```

#### `frontend/script.js` (around line 398-401):
```javascript
if (sender === 'bot') {
    let htmlContent = this.parseMarkdown(text);
    messageText.innerHTML = htmlContent;
    messageText.classList.add('markdown-content');
}
```

---

### Step 10: Nuclear Option - Complete Refresh

If nothing works, do a complete refresh:

```bash
# 1. Stop the server (Ctrl+C)

# 2. Clear ALL browser data for localhost
# - Open browser settings
# - Clear site data for localhost:3000

# 3. Restart computer (to clear all file caches)

# 4. Start server fresh
python quick_start_openai.py

# 5. Open browser (not incognito this time)

# 6. Go to http://localhost:3000

# 7. Test
```

---

## 🧪 Testing Checklist

Use this checklist to verify everything is working:

### Visual Tests

Ask: **"Tell me about the co-op program"**

Expected result:
- [ ] Heading "Overview" is large and red
- [ ] "co-op program" is bold and red
- [ ] "Main Points" is bold and red
- [ ] Bullet points have disc markers
- [ ] List items are properly indented
- [ ] Text is well-spaced and readable
- [ ] No visible markdown syntax (no `###`, `**`, `-`, etc.)

### Console Tests

Open Developer Tools (F12) → Console:
- [ ] "marked.js loaded successfully" appears
- [ ] "Parsing markdown with marked.js" appears when you ask a question
- [ ] No red error messages

### Network Tests

Open Developer Tools (F12) → Network:
- [ ] `marked.min.js` shows status 200
- [ ] File size ~35 KB
- [ ] No failed requests

---

## 🔍 Common Issues & Solutions

### Issue 1: Firewall Blocking CDN

**Symptom**: marked.js fails to load, Status 0 or "blocked"

**Solution A**: Whitelist `cdn.jsdelivr.net` in firewall

**Solution B**: Download marked.js locally
```bash
# Download marked.js
curl -o frontend/marked.min.js https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js

# Update index.html
# Change:
<script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
# To:
<script src="marked.min.js"></script>
```

---

### Issue 2: Syntax Errors in JavaScript

**Symptom**: Console shows "Unexpected token" or similar

**Solution**: Re-copy the `script.js` file exactly as provided

---

### Issue 3: CSS Not Applied

**Symptom**: Markdown converts but looks plain (no red colors, etc.)

**Solution**: Hard refresh (Ctrl+Shift+R) or clear CSS cache

---

### Issue 4: Partial Formatting

**Symptom**: Some markdown works (bold) but not others (headers)

**Solution**: 
1. Check if marked.js loaded (might be using fallback)
2. If fallback is being used, it has limited features
3. Fix marked.js loading issue (see Issue 1)

---

## 📞 Still Not Working?

If you've tried everything above and it still doesn't work:

### Diagnostic Report

Run this in your browser console (F12):

```javascript
console.log('=== Diagnostic Report ===');
console.log('marked available:', typeof marked !== 'undefined');
console.log('marked version:', typeof marked !== 'undefined' ? marked.options : 'N/A');
console.log('parseMarkdown exists:', typeof window.chatbot?.parseMarkdown === 'function');
console.log('markdownReady:', window.chatbot?.markdownReady);

// Test parse
const test = '### Test\n**Bold text**';
console.log('Test input:', test);
if (window.chatbot) {
    console.log('Test output:', window.chatbot.parseMarkdown(test));
}
```

**Send the output** for further diagnosis.

---

## ✅ Success Indicators

You'll know it's working when you see:

1. **In Console**:
   ```
   marked.js loaded successfully
   Parsing markdown with marked.js
   ```

2. **In Chat**:
   - Large red headings
   - Bold text in red
   - Proper bullet/numbered lists
   - Clean, readable formatting
   - NO visible `###`, `**`, `-` symbols

3. **In Network Tab**:
   - `marked.min.js` loaded (200 OK)

---

## 🎉 Quick Fix Summary

**Most Common Solution**:
```
1. Hard refresh browser (Ctrl + Shift + R)
2. Clear browser cache
3. Restart chatbot server
4. Test again
```

This solves 90% of issues!

---

## 📚 Additional Resources

- `MARKDOWN_RENDERING_GUIDE.md` - Full technical guide
- `MARKDOWN_QUICK_REFERENCE.md` - Quick reference
- Browser Console (F12) - Your best debugging tool

---

**Remember**: Always check the browser console (F12) first! It will tell you exactly what's wrong.

