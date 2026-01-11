# Setup Guide

This guide will walk you through setting up Reading Agent step-by-step.

## Prerequisites

- Python 3.8 or higher
- A Gmail account (for sending digest emails)
- An Anthropic API key (for AI summaries)

## Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd /path/to/reading-list

# Install Python packages
pip install -r requirements.txt
```

## Step 2: Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys" in the dashboard
4. Click "Create Key"
5. Copy the API key (it starts with `sk-ant-`)
6. Keep this somewhere safe - you'll need it in the next step

## Step 3: Configure Email (Gmail)

### Enable App Passwords

1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in the left sidebar
3. Under "Signing in to Google", enable "2-Step Verification" if not already enabled
4. Once 2FA is enabled, go back to Security
5. Click "App passwords" (you may need to sign in again)
6. Select "Mail" and "Other (Custom name)"
7. Enter "Reading List" as the name
8. Click "Generate"
9. Copy the 16-character password (no spaces)

## Step 4: Create Configuration File

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file
nano .env  # or use your preferred editor
```

Fill in these values:

```bash
# Your Anthropic API key from Step 2
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Gmail settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-16-char-app-password-here
DIGEST_EMAIL=your.email@gmail.com

# When you want to receive your daily digest (24-hour format)
DIGEST_TIME=08:00

# Optional: Change if you want to use a different port
# PORT=5000
```

Save and exit (Ctrl+X, then Y, then Enter in nano)

## Step 5: Test the Application

```bash
# Start the server
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

## Step 6: Access the Web Interface

1. Open your browser
2. Go to `http://localhost:5000`
3. You should see the Reading List dashboard

## Step 7: Add Your First Article

### Method 1: Web Interface
1. Click the "+" button in the top right
2. Paste an article URL (try: https://www.wsj.com or https://techcrunch.com)
3. Click "Add Article"
4. Wait a few seconds for processing

### Method 2: API Test
```bash
# In a new terminal window
curl -X POST http://localhost:5000/api/articles \
  -H "Content-Type: application/json" \
  -d '{"url": "https://techcrunch.com/2024/01/15/your-article-here"}'
```

## Step 8: Test the Digest Email

```bash
# Manually trigger a digest (instead of waiting for scheduled time)
curl -X POST http://localhost:5000/api/digest/send
```

Check your email - you should receive a formatted digest!

## Step 9: Set Up Email Ingestion (Optional)

This allows you to forward articles via email.

### Option A: Using ngrok (for testing)

1. Install ngrok: https://ngrok.com/download
2. Run ngrok:
```bash
ngrok http 5000
```
3. Copy the https URL (e.g., `https://abc123.ngrok.io`)
4. Use this URL + `/api/ingest` as your webhook

### Option B: Deploy to production

See README.md for deployment options (Heroku, Railway, etc.)

## Verification Checklist

- [ ] Application starts without errors
- [ ] Web interface loads at http://localhost:5000
- [ ] Can add an article via the web UI
- [ ] Article is processed and shows summary
- [ ] Can mark article as read/unread
- [ ] Can generate audio for an article
- [ ] Digest email sends successfully
- [ ] Email contains formatted articles

## Common Issues

### "ModuleNotFoundError"
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

### "Authentication failed" (Email)
- Double-check you're using the 16-character app password, not your regular password
- Ensure 2FA is enabled on your Google account
- Try generating a new app password

### "Invalid API key" (Anthropic)
- Verify the key starts with `sk-ant-`
- Make sure there are no extra spaces in .env
- Check your API quota at https://console.anthropic.com/

### Articles not extracting
- Some sites block automated scraping
- Try different article URLs
- Check the terminal for specific errors

### Database errors
```bash
# Reset the database
rm reading_list.db
python -c "from database import Database; Database()"
```

## Next Steps

1. **Customize summaries**: Edit `article_processor.py` to focus on topics relevant to you
2. **Adjust digest time**: Change `DIGEST_TIME` in `.env`
3. **Set up email forwarding**: Configure email ingestion for mobile article saving
4. **Deploy to cloud**: Make it accessible from anywhere

## Getting Help

If you encounter issues:
1. Check the terminal output for error messages
2. Review the relevant section in README.md
3. Check that all API keys are valid and have quota remaining
4. Ensure all dependencies are installed

---

Enjoy your new reading list manager! 📚
