from gtts import gTTS
import os
from config import Config

class AudioGenerator:
    def __init__(self):
        self.audio_dir = 'static/audio'
        os.makedirs(self.audio_dir, exist_ok=True)

    def generate_audio(self, article_data, article_id):
        """Generate audio summary of article"""
        try:
            # Build text to speak
            text = self._build_audio_text(article_data)

            # Generate audio file
            filename = f"article_{article_id}.mp3"
            filepath = os.path.join(self.audio_dir, filename)

            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filepath)

            return f"/audio/{filename}"

        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    def _build_audio_text(self, article_data):
        """Build text for audio narration"""
        parts = []

        # Title
        if article_data.get('title'):
            parts.append(f"Article: {article_data['title']}")

        # Source
        if article_data.get('source'):
            parts.append(f"From {article_data['source']}")

        # Summary
        if article_data.get('summary'):
            parts.append(f"Summary: {article_data['summary']}")

        # Key insights
        if article_data.get('key_insights'):
            insights = article_data['key_insights']
            if isinstance(insights, str):
                import json
                try:
                    insights = json.loads(insights)
                except:
                    insights = []

            if insights and len(insights) > 0:
                parts.append("Key insights:")
                for idx, insight in enumerate(insights, 1):
                    parts.append(f"{idx}. {insight}")

        # Implications
        if article_data.get('implications'):
            parts.append(f"Implications: {article_data['implications']}")

        return ". ".join(parts)

    def generate_digest_audio(self, articles, cross_article_insights, digest_id):
        """Generate audio for entire digest"""
        try:
            text = self._build_digest_audio_text(articles, cross_article_insights)

            filename = f"digest_{digest_id}.mp3"
            filepath = os.path.join(self.audio_dir, filename)

            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filepath)

            return f"/audio/{filename}"

        except Exception as e:
            print(f"Error generating digest audio: {e}")
            return None

    def _build_digest_audio_text(self, articles, cross_article_insights):
        """Build text for digest audio"""
        parts = []

        parts.append(f"Your daily reading digest. You have {len(articles)} new articles.")

        if cross_article_insights:
            parts.append(f"Overall themes: {cross_article_insights}")

        for idx, article in enumerate(articles, 1):
            parts.append(f"Article {idx}: {article.get('title', 'Untitled')}")
            parts.append(f"From {article.get('source', 'Unknown source')}")

            if article.get('summary'):
                parts.append(article['summary'])

        return ". ".join(parts)
