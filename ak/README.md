# Smart Reading List & Research Manager

A powerful, AI-powered reading list manager designed for venture capitalists and busy professionals. Seamlessly save articles, get intelligent summaries with cross-article insights, and receive daily digests - all optimized for mobile use.

## Features

### 📱 Frictionless Capture
- **Email Ingestion**: Forward any article or paste URLs in an email to automatically add to your reading list
- **Web Interface**: Add articles directly from the mobile-optimized dashboard
- **Smart Extraction**: Automatically extracts title, author, content, and source

### 🧠 AI-Powered Intelligence
- **Crisp Summaries**: Claude AI generates concise, actionable summaries focused on what matters
- **Key Insights**: Bullet-pointed highlights of the most important points
- **Implications**: Analysis of why this matters and potential opportunities
- **Cross-Article Insights**: Daily themes and patterns across your saved articles

### 📧 Daily Digest
- **Scheduled Emails**: Receive a beautifully formatted digest every morning
- **Customizable Time**: Set when you want to receive your digest
- **Themed Insights**: See how articles connect and what trends are emerging

### 🎧 Audio Summaries
- **Text-to-Speech**: Generate audio versions of articles for commute listening
- **On-Demand**: Create audio for any article with one click
- **Digest Audio**: Listen to your entire daily digest

### 📊 Mobile-First Interface
- **Responsive Design**: Works perfectly on phones, tablets, and desktops
- **Read/Unread Workflow**: Swipe through articles and mark as read
- **Favorites**: Star important articles for quick access
- **Archive**: Clean up your list by archiving processed articles

## Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create your configuration file
cp .env.example .env
```

### 2. Configuration

Edit `.env` and add your API keys and email settings:

```bash
# Required: AI Summarization
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Required: Email Digest
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
DIGEST_EMAIL=your_email@gmail.com

# Optional: Set digest time (default: 08:00)
DIGEST_TIME=08:00
```

#### Getting API Keys

**Anthropic API Key** (Required for AI summaries):
1. Sign up at https://console.anthropic.com/
2. Navigate to API Keys section
3. Create a new API key
4. Add it to your `.env` file

**Gmail App Password** (Required for email digest):
1. Go to Google Account settings
2. Enable 2-factor authentication if not already enabled
3. Go to Security → App passwords
4. Generate a new app password for "Mail"
5. Use this password (not your regular password) in `SMTP_PASSWORD`

### 3. Run the Application

```bash
# Start the server
python app.py
```

The app will be available at `http://localhost:5000`

### 4. Set Up Email Ingestion

There are several ways to set up email ingestion:

#### Option A: Gmail Forwarding (Simplest)
1. Set up a Gmail filter to auto-forward emails to your server's `/api/ingest` endpoint
2. Use a service like [ngrok](https://ngrok.com/) to expose localhost: `ngrok http 5000`
3. Configure the webhook URL in Gmail filters

#### Option B: Email Service Webhook (Recommended for production)
1. Sign up for [SendGrid](https://sendgrid.com/) or [Mailgun](https://mailgun.com/)
2. Set up an inbound parse webhook pointing to `your-domain.com/api/ingest`
3. Get your custom email address (e.g., `reading@inbound.yourdomain.com`)
4. Add this email to your `.env` as `INGESTION_EMAIL`

#### Option C: Manual Entry
Simply use the "+" button in the web interface to add articles manually

## Usage

### Adding Articles

**Via Email:**
1. Forward any email with article links to your ingestion email
2. Or compose a new email with article URLs in the body
3. Articles are automatically extracted and processed

**Via Web Interface:**
1. Click the "+" button in the header
2. Paste article URL
3. Click "Add Article"

### Reading Workflow

1. **Browse**: View unread articles in your dashboard
2. **Read**: Click an article to see summary, insights, and implications
3. **Listen**: Generate audio to listen during commute
4. **Mark Read**: Tap "Mark as Read" when done
5. **Archive**: Archive articles you no longer need

### Daily Digest

Every morning (or your configured time), you'll receive an email with:
- Overview of all new articles
- Cross-article themes and insights
- Individual article summaries
- Links to read full articles
- Quick actions to mark as read

## Project Structure

```
.
├── app.py                    # Flask application and API routes
├── config.py                 # Configuration management
├── database.py              # SQLite database operations
├── article_processor.py     # Article extraction and AI summarization
├── audio_generator.py       # Text-to-speech audio generation
├── email_handler.py         # Email parsing and sending
├── digest_generator.py      # Daily digest creation
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html          # Main web interface
├── static/
│   ├── css/
│   │   └── styles.css      # Mobile-first styling
│   ├── js/
│   │   └── app.js          # Frontend JavaScript
│   └── audio/              # Generated audio files
└── reading_list.db         # SQLite database (auto-created)
```

## API Endpoints

### Articles
- `GET /api/articles` - Get all articles (supports filters: `?status=unread`, `?favorited=true`)
- `GET /api/articles/<id>` - Get specific article
- `POST /api/articles` - Add new article (body: `{"url": "..."}`)
- `POST /api/articles/<id>/read` - Mark as read
- `POST /api/articles/<id>/unread` - Mark as unread
- `POST /api/articles/<id>/archive` - Archive article
- `POST /api/articles/<id>/favorite` - Toggle favorite
- `POST /api/articles/<id>/audio` - Generate audio

### Digest
- `POST /api/digest/send` - Manually trigger digest email

### Ingestion
- `POST /api/ingest` - Email webhook for article ingestion

## Customization

### Adjust Summary Focus
Edit `article_processor.py` → `_build_summary_prompt()` to customize what the AI focuses on in summaries.

### Change Digest Time
Update `DIGEST_TIME` in `.env` (format: `HH:MM`, e.g., `08:30`)

### Modify UI Theme
Edit `static/css/styles.css` to change colors, fonts, and layout.

## Deployment

### Deploy to Cloud (Heroku, Railway, etc.)

1. Add a `Procfile`:
```
web: python app.py
```

2. Set environment variables in your hosting platform

3. Set up a custom domain for email ingestion

### Deploy with Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

## Troubleshooting

### Articles not being extracted
- Check if the URL is publicly accessible
- Some sites block automated scraping - try a different source
- Check logs for specific errors

### Email digest not sending
- Verify SMTP credentials in `.env`
- For Gmail, ensure you're using an app password, not your regular password
- Check that 2FA is enabled on your Google account

### AI summaries not generating
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check API quota at https://console.anthropic.com/
- Review logs for specific errors

### Audio not generating
- Check that `static/audio` directory exists and is writable
- Verify gTTS is installed correctly
- Some text may fail to convert - try regenerating

## Future Enhancements

Potential features to add:
- [ ] Browser extension for one-click saving
- [ ] Telegram/WhatsApp bot integration
- [ ] PDF export of digests
- [ ] Tags and custom collections
- [ ] Search and full-text search
- [ ] Integration with note-taking apps (Notion, Roam)
- [ ] RSS feed support
- [ ] Reading time estimates
- [ ] Highlights and annotations

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **AI**: Anthropic Claude (Sonnet 3.5)
- **Article Extraction**: Trafilatura, Newspaper3k
- **Audio**: Google Text-to-Speech (gTTS)
- **Frontend**: Vanilla JavaScript, Mobile-first CSS
- **Email**: SMTP (Gmail, SendGrid, Mailgun compatible)

## License

MIT License - feel free to use and modify for your needs!

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Open an issue if you find bugs or have feature requests

---

Built with ❤️ for busy professionals who want to stay informed without the overwhelm.
