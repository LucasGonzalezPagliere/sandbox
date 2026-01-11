from datetime import datetime, timedelta
from config import Config
import json
import markdown
import html
import re

class DigestGenerator:
    def __init__(self, database, processor, audio_gen, email_handler):
        self.db = database
        self.processor = processor
        self.audio_gen = audio_gen
        self.email_handler = email_handler
        self.md = markdown.Markdown(extensions=['nl2br', 'smarty'])

    def _render_markdown(self, text):
        """Convert markdown text to clean HTML"""
        if not text:
            return ""
        self.md.reset()
        return self.md.convert(text)

    def _clean_text(self, text):
        """Escape HTML entities for safe display"""
        if not text:
            return ""
        return html.escape(str(text))

    def _strip_markdown(self, text):
        """Remove markdown formatting for plain text emails"""
        if not text:
            return ""
        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # Convert markdown links to plain text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove code backticks
        text = re.sub(r'`(.+?)`', r'\1', text)
        return text

    def send_daily_digest(self):
        """Generate and send the daily digest email"""
        # Get unread articles from the last 24 hours
        articles = self.db.get_unread_articles_for_digest(hours=24)

        if len(articles) == 0:
            print("No new articles for digest")
            return

        # Generate cross-article insights
        cross_article_insights = self.processor.generate_cross_article_insights(articles)

        # Save digest to database
        article_ids = [a['id'] for a in articles]
        digest_id = self.db.add_digest(article_ids, cross_article_insights)

        # Generate digest email HTML
        html_content = self._build_digest_html(articles, cross_article_insights)
        text_content = self._build_digest_text(articles, cross_article_insights)

        # Send email
        subject = f"Your Daily Reading Digest - {len(articles)} New Articles"
        success = self.email_handler.send_email(
            Config.DIGEST_EMAIL,
            subject,
            html_content,
            text_content
        )

        if success:
            print(f"Digest sent successfully: {len(articles)} articles")
        else:
            print("Failed to send digest")

        return digest_id

    def _build_digest_html(self, articles, cross_article_insights):
        """Build HTML email content for digest"""
        date_str = datetime.now().strftime('%A, %B %d')
        article_count = len(articles)
        base_url = Config.BASE_URL
        ingestion_email = Config.INGESTION_EMAIL or 'reading@yourdomain.com'

        email_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.7;
            color: #2c2c2c;
            background-color: #e8ebe4;
            -webkit-font-smoothing: antialiased;
        }}
        .wrapper {{
            max-width: 640px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .header {{
            text-align: center;
            padding-bottom: 32px;
            border-bottom: 1px solid #d4d9cf;
            margin-bottom: 32px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 400;
            color: #1a1a1a;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}
        .header .date {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .intro {{
            font-size: 17px;
            color: #444;
            margin-bottom: 36px;
            text-align: center;
        }}
        .intro strong {{
            color: #1a1a1a;
        }}

        /* Cross-article insights */
        .themes {{
            background: #ffffff;
            border-radius: 12px;
            padding: 28px 32px;
            margin-bottom: 40px;
            border: 1px solid #d4d9cf;
        }}
        .themes-label {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #5a6550;
            margin-bottom: 16px;
        }}
        .themes-content {{
            font-size: 15px;
            line-height: 1.8;
            color: #333;
        }}
        .themes-content h1, .themes-content h2, .themes-content h3 {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 20px 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .themes-content h1:first-child, .themes-content h2:first-child, .themes-content h3:first-child {{
            margin-top: 0;
        }}
        .themes-content p {{
            margin-bottom: 12px;
        }}
        .themes-content ul, .themes-content ol {{
            margin: 12px 0;
            padding-left: 20px;
        }}
        .themes-content li {{
            margin-bottom: 8px;
        }}
        .themes-content strong {{
            color: #1a1a1a;
        }}

        /* Article cards */
        .article {{
            background: #ffffff;
            border-radius: 12px;
            padding: 28px 32px;
            margin-bottom: 24px;
            border: 1px solid #d4d9cf;
        }}
        .article-number {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: #7a8570;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .article-title {{
            font-size: 20px;
            font-weight: 400;
            color: #111827;
            line-height: 1.4;
            margin-bottom: 8px;
        }}
        .article-meta {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #555;
            margin-bottom: 20px;
        }}
        .article-meta .source {{
            font-weight: 500;
            color: #333;
        }}
        .summary {{
            font-size: 16px;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}

        /* Key insights */
        .insights-section {{
            margin-bottom: 20px;
        }}
        .insights-label {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #5a6550;
            margin-bottom: 12px;
        }}
        .insight-item {{
            display: block;
            margin-bottom: 10px;
            font-size: 14px;
            color: #333;
            line-height: 1.6;
            padding-left: 16px;
            position: relative;
        }}
        .insight-item:before {{
            content: "\\2022";
            color: #7a8570;
            position: absolute;
            left: 0;
        }}

        /* Implications */
        .implications {{
            background: #faf8f3;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 20px;
            border: 1px solid #e8e4d9;
        }}
        .implications-label {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #8b7355;
            margin-bottom: 8px;
        }}
        .implications-text {{
            font-size: 14px;
            color: #5c4a32;
            line-height: 1.6;
        }}

        /* Action link */
        .article-link {{
            display: inline-block;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            font-weight: 500;
            color: #4a7c59;
            text-decoration: none;
        }}
        .article-link:hover {{
            text-decoration: underline;
        }}
        .link-arrow {{
            margin-left: 4px;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding-top: 32px;
            margin-top: 16px;
            border-top: 1px solid #d4d9cf;
        }}
        .footer p {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }}
        .footer a {{
            color: #4a7c59;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .footer .email-hint {{
            font-size: 12px;
            color: #888;
            margin-top: 16px;
        }}

        /* Mobile optimizations */
        @media only screen and (max-width: 480px) {{
            .wrapper {{
                padding: 24px 16px;
            }}
            .article, .themes {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 24px;
            }}
            .article-title {{
                font-size: 18px;
            }}
            .summary {{
                font-size: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>Your Reading Digest</h1>
            <div class="date">{date_str}</div>
        </div>

        <p class="intro"><strong>{article_count} article{"s" if article_count != 1 else ""}</strong> curated for you today</p>
"""

        # Add cross-article insights if available
        if cross_article_insights:
            rendered_insights = self._render_markdown(cross_article_insights)
            email_html += f"""
        <div class="themes">
            <div class="themes-label">Themes &amp; Patterns</div>
            <div class="themes-content">{rendered_insights}</div>
        </div>
"""

        # Add each article
        for idx, article in enumerate(articles, 1):
            key_insights = article.get('key_insights', [])
            if isinstance(key_insights, str):
                try:
                    key_insights = json.loads(key_insights)
                except:
                    key_insights = []

            title = self._clean_text(article.get('title', 'Untitled'))
            source = self._clean_text(article.get('source', 'Unknown'))
            author = article.get('author')
            summary = self._clean_text(article.get('summary', 'No summary available'))
            article_url = article.get('url', '#')

            meta_parts = [f'<span class="source">{source}</span>']
            if author:
                meta_parts.append(self._clean_text(author))
            meta_text = " &middot; ".join(meta_parts)

            email_html += f"""
        <div class="article">
            <div class="article-number">Article {idx}</div>
            <div class="article-title">{title}</div>
            <div class="article-meta">{meta_text}</div>
            <div class="summary">{summary}</div>
"""

            if key_insights and len(key_insights) > 0:
                email_html += """
            <div class="insights-section">
                <div class="insights-label">Key Insights</div>
"""
                for insight in key_insights:
                    clean_insight = self._clean_text(insight)
                    email_html += f"""                <div class="insight-item">{clean_insight}</div>
"""
                email_html += """            </div>
"""

            if article.get('implications'):
                implications = self._clean_text(article.get('implications'))
                email_html += f"""
            <div class="implications">
                <div class="implications-label">Why It Matters</div>
                <div class="implications-text">{implications}</div>
            </div>
"""

            email_html += f"""
            <a href="{article_url}" class="article-link">Read full article<span class="link-arrow">&rarr;</span></a>
        </div>
"""

        email_html += f"""
        <div class="footer">
            <p><a href="{base_url}">Open Dashboard</a></p>
            <p class="email-hint">Forward articles to <strong>{ingestion_email}</strong> to add them to your reading list</p>
        </div>
    </div>
</body>
</html>
"""

        return email_html

    def _build_digest_text(self, articles, cross_article_insights):
        """Build plain text email content for digest"""
        date_str = datetime.now().strftime('%A, %B %d, %Y')
        text = f"YOUR READING DIGEST\n{date_str}\n"
        text += "\n" + "─" * 50 + "\n\n"
        text += f"{len(articles)} article{'s' if len(articles) != 1 else ''} curated for you today\n\n"

        if cross_article_insights:
            text += "─" * 50 + "\n"
            text += "THEMES & PATTERNS\n"
            text += "─" * 50 + "\n\n"
            text += self._strip_markdown(cross_article_insights) + "\n\n"

        text += "─" * 50 + "\n"
        text += "ARTICLES\n"
        text += "─" * 50 + "\n"

        for idx, article in enumerate(articles, 1):
            text += f"\n[{idx}] {article.get('title', 'Untitled')}\n"
            meta_parts = [article.get('source', 'Unknown')]
            if article.get('author'):
                meta_parts.append(article.get('author'))
            text += f"    {' · '.join(meta_parts)}\n"
            text += f"    {article.get('url', '')}\n\n"

            if article.get('summary'):
                text += f"    {article.get('summary')}\n\n"

            key_insights = article.get('key_insights', [])
            if isinstance(key_insights, str):
                try:
                    key_insights = json.loads(key_insights)
                except:
                    key_insights = []

            if key_insights:
                text += "    KEY INSIGHTS:\n"
                for insight in key_insights:
                    text += f"    → {self._strip_markdown(insight)}\n"
                text += "\n"

            if article.get('implications'):
                text += f"    WHY IT MATTERS:\n"
                text += f"    {self._strip_markdown(article.get('implications'))}\n\n"

        text += "─" * 50 + "\n"
        text += "Curated by your reading assistant\n"

        return text
