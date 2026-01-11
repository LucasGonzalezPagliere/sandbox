import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailHandler:
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD

    def parse_inbound_email(self, email_data):
        """Parse inbound email from SendGrid webhook

        Returns:
            dict with 'subject', 'from', 'text', 'html', 'urls'
        """
        parsed = {
            'subject': '',
            'from': '',
            'text': '',
            'html': '',
            'urls': []
        }

        if isinstance(email_data, dict):
            # SendGrid sends: subject, from, text, html
            parsed['subject'] = email_data.get('subject', '')
            parsed['from'] = email_data.get('from', '')
            parsed['text'] = email_data.get('text', '') or email_data.get('plain', '') or \
                           email_data.get('body-plain', '') or email_data.get('stripped-text', '')
            parsed['html'] = email_data.get('html', '') or email_data.get('body-html', '')

            # Extract URLs from the email content
            parsed['urls'] = self.extract_urls_from_email(email_data)

        return parsed

    def extract_urls_from_email(self, email_data):
        """Extract URLs from email content"""
        urls = []

        # Get email body (different formats depending on source)
        text = ''
        if isinstance(email_data, dict):
            # Try different possible fields
            text = email_data.get('text', '') or email_data.get('plain', '') or \
                   email_data.get('body-plain', '') or email_data.get('stripped-text', '') or \
                   email_data.get('subject', '')
        else:
            text = str(email_data)

        # Extract URLs using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        found_urls = re.findall(url_pattern, text)

        # Clean and validate URLs
        for url in found_urls:
            # Remove trailing punctuation
            url = re.sub(r'[.,;:!?\)]$', '', url)
            # Basic validation
            if self._is_valid_article_url(url):
                urls.append(url)

        return urls

    def _is_valid_article_url(self, url):
        """Check if URL is likely an article (not image, video, etc.)"""
        # Skip common non-article URLs
        skip_patterns = [
            r'\.(jpg|jpeg|png|gif|bmp|svg|ico)$',
            r'\.(mp4|avi|mov|wmv|flv|webm)$',
            r'\.(mp3|wav|ogg|flac)$',
            r'\.(pdf|doc|docx|xls|xlsx|zip)$',
            r'(youtube\.com|youtu\.be)',
            r'(twitter\.com/.+/status/\d+/photo)',
            r'(instagram\.com)',
        ]

        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email

            # Add plain text version if provided
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False
