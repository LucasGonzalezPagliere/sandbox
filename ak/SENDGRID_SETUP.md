# SendGrid Email Forwarding Setup

This guide will help you set up email forwarding so you can forward newsletters and articles directly to your Reading List app.

## Why SendGrid?

- **Free tier**: 100 emails/day (3,000/month) - permanently free
- **Inbound Parse**: Receives emails via webhook
- **Easy setup**: No complex email server configuration needed

## Setup Steps

### 1. Create SendGrid Account

1. Go to [SendGrid.com](https://sendgrid.com)
2. Click "Start for Free"
3. Sign up with your email
4. Verify your email address

### 2. Set Up Inbound Parse

1. Log in to SendGrid dashboard
2. Navigate to **Settings** → **Inbound Parse**
3. Click **Add Host & URL**

### 3. Configure the Webhook

For **testing locally**, you'll need to expose your local server to the internet using ngrok:

#### Install ngrok (if not already installed)
```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

#### Start your Flask app
```bash
cd ~/Documents/testing
source venv/bin/activate
python app.py
```

#### In a new terminal, start ngrok
```bash
ngrok http 5001
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5001
```

Copy the `https://` URL (e.g., `https://abc123.ngrok.io`)

### 4. Add the Webhook in SendGrid

Back in SendGrid's Inbound Parse settings:

1. **Hostname**: Choose a subdomain (e.g., `reading` - this will create `reading@yourdomain.com`)
   - For testing, you can use SendGrid's domain: leave blank or use a placeholder
   - **Note**: SendGrid requires a domain for production. For testing, we'll use a workaround below.

2. **URL**: Enter your webhook URL:
   ```
   https://abc123.ngrok.io/api/ingest
   ```
   Replace `abc123.ngrok.io` with your actual ngrok URL

3. **Check "POST the raw, full MIME message"** - Leave UNCHECKED (we want parsed data)

4. Click **Add**

### 5. Get Your Forwarding Email Address

SendGrid will generate an email address like:
```
reading@inbound.yourdomain.com
```

Or for testing, SendGrid provides a generic domain. Check the Inbound Parse settings page for your assigned address.

**Alternative for Testing**: If SendGrid requires a domain you don't have, you can:
- Use a free service like [improvmx.com](https://improvmx.com) to forward emails
- Or set up MX records with a domain you own

### 6. Test It Out

1. Forward an email (like a Stratechery newsletter) to your SendGrid inbound address
2. Or compose a new email with article URLs in the body
3. Send it to the inbound address
4. Check your Flask app logs - you should see:
   ```
   Received email: [Subject] from [email]
   Processing email as article: [Subject]
   ```
5. Refresh your Reading List app - the article should appear!

## How It Works

The app will:
- **If email contains URLs**: Extract and scrape those article URLs
- **If no URLs found**: Save the entire email content as an article (perfect for newsletters like Stratechery)
- Generate AI summaries for everything
- Include it in your daily digest

## For Production (Later)

For reliable daily use, you'll want to:

1. Deploy the app to a cloud service (Heroku, Railway, Render, etc.)
2. Get a permanent webhook URL (e.g., `https://yourapp.railway.app/api/ingest`)
3. Update the SendGrid webhook to use that URL
4. Set up a custom domain (optional) for nicer forwarding addresses

## Troubleshooting

### Emails not showing up?
- Check Flask app logs for errors
- Verify ngrok is still running (it expires after a few hours on free tier)
- Check SendGrid's Inbound Parse activity log
- Make sure your Flask app is running

### ngrok URL changed?
- ngrok free tier gives you a new URL each time you restart
- Update the webhook URL in SendGrid settings
- Or upgrade to ngrok paid for a permanent URL

### Need help?
Check the Flask app logs - all email processing is logged there.
