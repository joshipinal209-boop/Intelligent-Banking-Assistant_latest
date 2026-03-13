# 🔑 API Key Rotation & Recovery Guide

## Current Status
Your Google Gemini API key has been flagged as compromised and disabled by Google. The system is now operating in **FALLBACK MODE** which means:

✅ **What's Still Working:**
- User authentication (login/register)
- Account balance inquiries (using cached data)
- Transaction history (using cached data)
- Audit logs and reporting
- All other banking features

❌ **What's Limited:**
- Real-time AI analysis (using Gemini)
- Natural language understanding improvements
- Complex query reasoning

---

## 🛠️ Solution: Get a New API Key

### Step 1: Create a New Google Gemini API Key

**Visit**: https://aistudio.google.com/app/apikeys

**Steps:**
1. Click on your **Google Account** profile picture (top right)
2. Click **"Create API key"**
3. Choose **"Create API key in new project"** or select existing project
4. A dialog will appear with your new key
5. **Copy the key** (you'll need it in Step 2)

**Example new key format**: `AIzaSy...` (39 characters starting with AIzaSy)

### Step 2: Safely Update Your .env File

**Important:** Never share or expose your API key!

#### Option A: Using Terminal (Secure)
```bash
# Navigate to project directory
cd "fincore-intelligent-banking-assistant"

# Edit .env file with secure editor
nano .env

# Find this line:
# GOOGLE_API_KEY=AIzaSyAFN6MB6QRLTOyp8POmqXy7BaxcKfMP6ck

# Replace with your new key:
# GOOGLE_API_KEY=AIzaSy<YOUR_NEW_KEY_HERE>

# Save and exit (Ctrl+X, then Y, then Enter)
```

#### Option B: Using Python Script (Most Secure)
```python
# Create a file: update_api_key.py

import os
from pathlib import Path

# Read user input securely (without echo)
import getpass

new_key = getpass.getpass("Enter your new Google Gemini API key: ")

# Update .env file
env_file = Path(".env")
content = env_file.read_text()

# Replace only the GOOGLE_API_KEY line
import re
new_content = re.sub(
    r'GOOGLE_API_KEY=.*',
    f'GOOGLE_API_KEY={new_key}',
    content
)

# Write back
env_file.write_text(new_content)
print("✅ API key updated successfully")
print("🔒 Restarting the application...")
```

Run it:
```bash
python update_api_key.py
```

#### Option C: Using Environment Variable (Runtime Only)
```bash
# Set environment variable before starting
export GOOGLE_API_KEY="AIzaSy<YOUR_NEW_KEY>"

# Start the application
./scripts/start_all.sh
```

### Step 3: Restart the Application

```bash
# Stop the current application
# (Ctrl+C in the terminal where it's running)

# Restart with new key
./scripts/start_all.sh
```

### Step 4: Verify the Fix

**Test in API Documentation:**
1. Go to: http://localhost:8000/docs
2. Authenticate with your user credentials
3. Try a query:
```json
{
  "session_id": "test-1",
  "customer_id": "fa800b9e",
  "query": "What is my account balance?"
}
```

**Expected Result:**
- Status: "SUCCESS" (not "DEGRADED")
- Response includes AI analysis
- final_response contains smart reasoning

---

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Generate new keys regularly (every 30-90 days)
- ✅ Use different keys for dev/staging/production
- ✅ Store keys in `.env` file (in `.gitignore`)
- ✅ Use environment variables for deployment
- ✅ Rotate keys immediately if compromised
- ✅ Monitor API usage for suspicious activity
- ✅ Delete old/unused keys

### ❌ DON'T:
- ❌ Share API keys in chat/email/slack
- ❌ Commit keys to git repositories
- ❌ Include keys in documentation
- ❌ Use the same key across multiple environments
- ❌ Hardcode keys in source code
- ❌ Expose keys in error messages/logs

### 🔒 Security Features:
- API keys in `.env` are listed in `.gitignore`
- Keys are never logged or printed
- Keys are never committed to git
- Keys are environment-specific
- Failed auth attempts are logged

---

## 📋 Step-by-Step Checklist

### For Getting New Key:
- [ ] Visit https://aistudio.google.com/app/apikeys
- [ ] Create new API key
- [ ] Copy the key to clipboard
- [ ] Do NOT close the page yet

### For Updating .env:
- [ ] Navigate to: `fincore-intelligent-banking-assistant/`
- [ ] Open `.env` file
- [ ] Find line: `GOOGLE_API_KEY=...`
- [ ] Replace with new key
- [ ] Save the file
- [ ] Close the file

### For Testing:
- [ ] Stop current application (Ctrl+C)
- [ ] Restart: `./scripts/start_all.sh`
- [ ] Wait for services to start (~5-10 seconds)
- [ ] Go to http://localhost:8000/docs
- [ ] Login with test credentials
- [ ] Make a test query
- [ ] Verify response shows "SUCCESS" (not "DEGRADED")

---

## 🆘 Troubleshooting

### Issue: Still Getting "Permission Denied" Error
**Solution:**
1. Verify you copied the full key (should be ~39 characters)
2. Check for extra spaces at beginning/end
3. Restart the application again
4. Generate a NEW key (the first one might still be processing)

### Issue: .env File Not Updating
**Solution:**
1. Make sure you're editing the right file:
   ```bash
   cat .env | grep GOOGLE_API_KEY
   ```
2. Check for read-only permissions:
   ```bash
   ls -la .env
   chmod 644 .env  # Make writable
   ```
3. Try using `nano .env` instead of other editors

### Issue: Application Won't Start After Update
**Solution:**
1. Check `.env` file for syntax errors:
   ```bash
   cat .env
   ```
2. Ensure no extra quotes around key:
   ```
   # Correct:
   GOOGLE_API_KEY=AIzaSy...
   
   # Wrong:
   GOOGLE_API_KEY="AIzaSy..."
   GOOGLE_API_KEY='AIzaSy...'
   ```
3. Restart with debug logging:
   ```bash
   DEBUG=True ./scripts/start_all.sh
   ```

### Issue: New Key Shows as "Invalid"
**Solution:**
1. Regenerate the key (wait 1-2 minutes)
2. Enable the Generative Language API:
   - Visit: https://console.cloud.google.com/
   - Search for "Generative Language API"
   - Click "Enable"
3. Check API quotas aren't exceeded
4. Verify key is for the right project

---

## 📞 Need More Help?

### Documentation Files:
- `QUICK_START.md` - General setup
- `README.md` - Project overview
- `AUTH_GUIDE.md` - Authentication

### Check API Status:
```bash
# Test if API key is working
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "customer_id": "fa800b9e",
    "query": "Test query"
  }' | jq '.status'

# Should show: "SUCCESS" (not "DEGRADED")
```

---

## ✨ After Successful Update

Once your new API key is working:

1. **Fallback Mode Disabled**: System will use Gemini AI for all queries
2. **Full AI Capabilities**: Multi-agent reasoning enabled
3. **Better Responses**: More intelligent query analysis
4. **Real-time Processing**: Faster response times

Test it with:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "final-test",
    "customer_id": "fa800b9e",
    "query": "Analyze my recent transactions for unusual patterns"
  }'
```

---

**Last Updated**: March 13, 2026
**Status**: System operational in fallback mode
**Action Required**: Update API key to restore full AI capabilities

