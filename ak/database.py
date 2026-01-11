import sqlite3
from datetime import datetime
from config import Config
import json

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                author TEXT,
                source TEXT,
                content TEXT,
                summary TEXT,
                key_insights TEXT,
                implications TEXT,
                audio_path TEXT,
                status TEXT DEFAULT 'unread',
                favorited BOOLEAN DEFAULT 0,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                archived_at TIMESTAMP
            )
        ''')

        # Digests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                article_ids TEXT,
                cross_article_insights TEXT
            )
        ''')

        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_article(self, url, title=None, author=None, source=None, content=None, tags=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO articles (url, title, author, source, content, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, title, author, source, content, json.dumps(tags) if tags else None))

            article_id = cursor.lastrowid
            conn.commit()
            return article_id
        except sqlite3.IntegrityError:
            # Article already exists
            cursor.execute('SELECT id FROM articles WHERE url = ?', (url,))
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def update_article(self, article_id, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Build dynamic update query
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            if isinstance(value, (list, dict)):
                values.append(json.dumps(value))
            else:
                values.append(value)

        values.append(article_id)

        query = f"UPDATE articles SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def get_article(self, article_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        article = cursor.fetchone()
        conn.close()
        return dict(article) if article else None

    def get_articles(self, status=None, limit=None, favorited=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM articles WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if favorited is not None:
            query += ' AND favorited = ?'
            params.append(1 if favorited else 0)

        query += ' ORDER BY created_at DESC'

        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        cursor.execute(query, params)
        articles = cursor.fetchall()
        conn.close()

        return [dict(article) for article in articles]

    def mark_as_read(self, article_id):
        self.update_article(article_id, status='read', read_at=datetime.now().isoformat())

    def mark_as_unread(self, article_id):
        self.update_article(article_id, status='unread', read_at=None)

    def archive_article(self, article_id):
        self.update_article(article_id, status='archived', archived_at=datetime.now().isoformat())

    def toggle_favorite(self, article_id):
        article = self.get_article(article_id)
        if article:
            new_favorited = 0 if article['favorited'] else 1
            self.update_article(article_id, favorited=new_favorited)
            return new_favorited
        return None

    def add_digest(self, article_ids, cross_article_insights):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO digests (article_ids, cross_article_insights)
            VALUES (?, ?)
        ''', (json.dumps(article_ids), cross_article_insights))

        digest_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return digest_id

    def get_unread_articles_for_digest(self, hours=24):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM articles
            WHERE status = 'unread'
            AND datetime(created_at) > datetime('now', '-' || ? || ' hours')
            ORDER BY created_at DESC
        ''', (hours,))

        articles = cursor.fetchall()
        conn.close()

        return [dict(article) for article in articles]
