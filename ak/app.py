from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from database import Database
from article_processor import ArticleProcessor
from audio_generator import AudioGenerator
from email_handler import EmailHandler
from digest_generator import DigestGenerator
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize components
db = Database()
processor = ArticleProcessor()
audio_gen = AudioGenerator()
email_handler = EmailHandler()
digest_gen = DigestGenerator(db, processor, audio_gen, email_handler)

# API Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get all articles with optional filtering"""
    status = request.args.get('status')
    favorited = request.args.get('favorited')

    if favorited is not None:
        favorited = favorited.lower() == 'true'

    articles = db.get_articles(status=status, favorited=favorited)
    return jsonify(articles)

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article"""
    article = db.get_article(article_id)
    if article:
        return jsonify(article)
    return jsonify({'error': 'Article not found'}), 404

@app.route('/api/articles', methods=['POST'])
def add_article():
    """Add a new article from URL or text"""
    data = request.json
    url = data.get('url')
    text_content = data.get('text')  # Allow direct text paste
    custom_title = data.get('title')

    if not url and not text_content:
        return jsonify({'error': 'URL or text content is required'}), 400

    try:
        if text_content:
            # User pasted article text directly (for paywalled content)
            article_data = {
                'url': url or 'pasted-content',
                'title': custom_title or 'Pasted Article',
                'author': None,
                'source': 'Manual Entry',
                'content': text_content
            }
            print(f"Processing pasted content: {article_data['title']}")
        else:
            # Extract article content from URL
            article_data = processor.extract_article(url)
            print(f"Extracted article: {article_data.get('title') if article_data else 'None'}")

        if not article_data or not article_data.get('content'):
            return jsonify({'error': 'Failed to extract article content from URL. Try pasting the article text instead.'}), 400

        # Add to database
        article_id = db.add_article(
            url=article_data['url'],
            title=article_data['title'],
            author=article_data['author'],
            source=article_data['source'],
            content=article_data['content']
        )

        # Generate summary (with recent articles for context)
        recent_articles = db.get_articles(limit=5)
        summary_data = processor.generate_summary(article_data, recent_articles)
        print(f"Generated summary: {summary_data.get('summary')[:50] if summary_data and summary_data.get('summary') else 'None'}...")

        if not summary_data:
            summary_data = {'summary': 'Summary generation failed', 'key_insights': [], 'implications': ''}

        # Update article with summary
        db.update_article(
            article_id,
            summary=summary_data.get('summary', ''),
            key_insights=summary_data.get('key_insights', []),
            implications=summary_data.get('implications', '')
        )

        # Get updated article
        article = db.get_article(article_id)
        return jsonify(article), 201

    except Exception as e:
        print(f"Error in add_article: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles/<int:article_id>/read', methods=['POST'])
def mark_read(article_id):
    """Mark article as read"""
    db.mark_as_read(article_id)
    return jsonify({'success': True})

@app.route('/api/articles/<int:article_id>/unread', methods=['POST'])
def mark_unread(article_id):
    """Mark article as unread"""
    db.mark_as_unread(article_id)
    return jsonify({'success': True})

@app.route('/api/articles/<int:article_id>/archive', methods=['POST'])
def archive_article(article_id):
    """Archive an article"""
    db.archive_article(article_id)
    return jsonify({'success': True})

@app.route('/api/articles/<int:article_id>/favorite', methods=['POST'])
def toggle_favorite(article_id):
    """Toggle favorite status"""
    favorited = db.toggle_favorite(article_id)
    return jsonify({'favorited': favorited})

@app.route('/api/articles/<int:article_id>/audio', methods=['POST'])
def generate_audio(article_id):
    """Generate audio for an article"""
    article = db.get_article(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    audio_path = audio_gen.generate_audio(article, article_id)
    if audio_path:
        db.update_article(article_id, audio_path=audio_path)
        return jsonify({'audio_path': audio_path})

    return jsonify({'error': 'Failed to generate audio'}), 500

@app.route('/api/ingest', methods=['POST'])
def ingest_article():
    """Endpoint for email webhook to ingest articles and newsletters"""
    try:
        # This will be called by email service webhooks (e.g., SendGrid)
        # SendGrid sends form data, not JSON
        email_data = request.form.to_dict() if request.form else request.json

        # Parse the email
        parsed_email = email_handler.parse_inbound_email(email_data)
        print(f"Received email: {parsed_email['subject']} from {parsed_email['from']}")

        results = []

        # If email contains URLs, extract those articles
        if parsed_email['urls']:
            for url in parsed_email['urls']:
                try:
                    # Extract and process article
                    article_data = processor.extract_article(url)
                    if not article_data or not article_data.get('content'):
                        results.append({'url': url, 'error': 'Failed to extract article', 'success': False})
                        continue

                    article_id = db.add_article(
                        url=article_data['url'],
                        title=article_data['title'],
                        author=article_data['author'],
                        source=article_data['source'],
                        content=article_data['content']
                    )

                    # Generate summary
                    recent_articles = db.get_articles(limit=5)
                    summary_data = processor.generate_summary(article_data, recent_articles)

                    if summary_data:
                        db.update_article(
                            article_id,
                            summary=summary_data.get('summary', ''),
                            key_insights=summary_data.get('key_insights', []),
                            implications=summary_data.get('implications', '')
                        )

                    results.append({'url': url, 'article_id': article_id, 'success': True})
                except Exception as e:
                    results.append({'url': url, 'error': str(e), 'success': False})

        # If no URLs found, treat the entire email as an article (for newsletters)
        else:
            try:
                article_data = {
                    'url': f'email-{parsed_email["from"]}',
                    'title': parsed_email['subject'] or 'Forwarded Email',
                    'author': parsed_email['from'],
                    'source': 'Email',
                    'content': parsed_email['text'] or parsed_email['html']
                }

                if not article_data['content']:
                    return jsonify({'error': 'Email has no content'}), 400

                print(f"Processing email as article: {article_data['title']}")

                article_id = db.add_article(
                    url=article_data['url'],
                    title=article_data['title'],
                    author=article_data['author'],
                    source=article_data['source'],
                    content=article_data['content']
                )

                # Generate summary
                recent_articles = db.get_articles(limit=5)
                summary_data = processor.generate_summary(article_data, recent_articles)

                if summary_data:
                    db.update_article(
                        article_id,
                        summary=summary_data.get('summary', ''),
                        key_insights=summary_data.get('key_insights', []),
                        implications=summary_data.get('implications', '')
                    )

                results.append({'type': 'email', 'article_id': article_id, 'success': True})

            except Exception as e:
                results.append({'type': 'email', 'error': str(e), 'success': False})

        return jsonify({'results': results}), 200

    except Exception as e:
        print(f"Error in ingest endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/digest/send', methods=['POST'])
def send_digest():
    """Manually trigger digest email"""
    try:
        digest_gen.send_daily_digest()
        return jsonify({'success': True, 'message': 'Digest sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files"""
    return send_from_directory('static/audio', filename)

# Scheduler for daily digest
scheduler = BackgroundScheduler()

def schedule_digest():
    """Schedule daily digest based on config time"""
    hour, minute = Config.DIGEST_TIME.split(':')
    scheduler.add_job(
        digest_gen.send_daily_digest,
        'cron',
        hour=int(hour),
        minute=int(minute),
        id='daily_digest'
    )

if __name__ == '__main__':
    # Start scheduler
    schedule_digest()
    scheduler.start()

    # Run app
    app.run(host=Config.HOST, port=Config.PORT, debug=True)
