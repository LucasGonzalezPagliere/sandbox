import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'reading_list.db')

    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    DIGEST_EMAIL = os.getenv('DIGEST_EMAIL')
    DIGEST_TIME = os.getenv('DIGEST_TIME', '08:00')
    INGESTION_EMAIL = os.getenv('INGESTION_EMAIL')

    # Application
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
