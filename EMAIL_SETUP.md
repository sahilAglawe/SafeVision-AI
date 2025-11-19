# Gmail Email Alert Setup Guide

## Current Status
The SafeVisionAI system is working perfectly with:
- ✅ Camera detection active
- ✅ Real-time video feed
- ✅ Threat detection (detected "Men attacking woman")
- ✅ Database storage
- ❌ Email alerts (needs Gmail configuration)

## To Fix Email Alerts

### Option 1: Use Gmail App Password (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account (shrikantambatkar8@gmail.com)
   - Go to Google Account settings
   - Security → 2-Step Verification → Turn it on

2. **Generate App Password**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. **Update the app.py file**
   - Replace `EMAIL_PASSWORD = "Shrikant@cse2025"` with your App Password
   - Example: `EMAIL_PASSWORD = "abcd efgh ijkl mnop"`

### Option 2: Use Less Secure App Access (Not Recommended)

1. Go to your Google Account settings
2. Security → Less secure app access
3. Turn on "Allow less secure apps"

### Option 3: Test with Different Email Service

You can also use other email services like:
- Outlook/Hotmail
- Yahoo Mail
- Or set up a local SMTP server

## Current Email Configuration
```python
EMAIL_SENDER = "shrikantambatkar8@gmail.com"
EMAIL_PASSWORD = "Shrikant@cse2025"  # ← This needs to be an App Password
EMAIL_RECEIVER = "shrikantambatkar115@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

## Testing Email
Once configured, you can test by:
1. Going to http://localhost:5000
2. Click "Live Detection" tab
3. Click "Test Email" button
4. Check shrikantambatkar115@gmail.com for the test email

## System Status
- Camera: ✅ Working (480x640 resolution)
- Detection: ✅ Working (detected threats)
- Video Feed: ✅ Working (real-time stream)
- Database: ✅ Working (incidents stored)
- Email: ⚠️ Needs Gmail App Password setup 