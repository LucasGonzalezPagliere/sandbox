import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse
import anthropic
from config import Config
import json
import re

class ArticleProcessor:
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY) if Config.ANTHROPIC_API_KEY else None

    def extract_article(self, url):
        """Extract article content from URL using multiple methods for reliability"""
        article_data = {
            'url': url,
            'title': None,
            'author': None,
            'content': None,
            'source': None
        }

        try:
            # Method 1: Try trafilatura (fast and clean)
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                metadata = trafilatura.extract_metadata(downloaded)

                if content:
                    article_data['content'] = content
                    if metadata:
                        article_data['title'] = metadata.title
                        article_data['author'] = metadata.author
                        article_data['source'] = metadata.sitename or self._get_domain(url)

            # Method 2: Fallback to BeautifulSoup if trafilatura fails
            if not article_data['content']:
                response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.content, 'html.parser')

                # Try to extract title
                if not article_data['title']:
                    title_tag = soup.find('title') or soup.find('h1')
                    if title_tag:
                        article_data['title'] = title_tag.get_text().strip()

                # Extract text from paragraphs
                paragraphs = soup.find_all('p')
                article_data['content'] = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                article_data['source'] = self._get_domain(url)

            # Clean up
            if not article_data['title'] and article_data['content']:
                # Try to extract title from first line
                first_line = article_data['content'].split('\n')[0]
                if len(first_line) < 200:
                    article_data['title'] = first_line

            if not article_data['source']:
                article_data['source'] = self._get_domain(url)

            return article_data

        except Exception as e:
            print(f"Error extracting article from {url}: {e}")
            return article_data

    def _get_domain(self, url):
        """Extract clean domain name from URL"""
        try:
            domain = urlparse(url).netloc
            # Remove www. and common subdomains
            domain = re.sub(r'^www\.', '', domain)
            return domain
        except:
            return 'Unknown'

    def generate_summary(self, article_data, context_articles=None):
        """Generate AI summary with key insights and implications"""
        if not self.anthropic_client:
            return {
                'summary': 'AI summarization not configured. Please add ANTHROPIC_API_KEY.',
                'key_insights': [],
                'implications': ''
            }

        # Build prompt
        prompt = self._build_summary_prompt(article_data, context_articles)

        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            result = self._parse_summary_response(response.content[0].text)
            return result

        except Exception as e:
            print(f"Error generating summary: {e}")
            return {
                'summary': 'Error generating summary',
                'key_insights': [],
                'implications': str(e)
            }

    def _build_summary_prompt(self, article_data, context_articles=None):
        """Build prompt for summary generation"""
        prompt = f"""You are analyzing an article for a venture capitalist. Provide a crisp, actionable analysis.

ARTICLE:
Title: {article_data.get('title', 'Untitled')}
Source: {article_data.get('source', 'Unknown')}
Author: {article_data.get('author', 'Unknown')}

Content:
{article_data.get('content', '')[:8000]}

"""

        if context_articles and len(context_articles) > 0:
            prompt += "\nRECENT ARTICLES FOR CONTEXT:\n"
            for idx, ctx in enumerate(context_articles[:3], 1):
                summary = ctx.get('summary') or ''
                prompt += f"{idx}. {ctx.get('title', 'Untitled')} - {summary[:200]}\n"

        prompt += """
Please provide:

1. SUMMARY (2-3 sentences): The core message in clear, concise language

2. KEY INSIGHTS (3-5 bullet points): What matters most
   - Focus on: Market shifts, competitive dynamics, technology trends, investment implications
   - Be specific and quantitative where possible

3. IMPLICATIONS (1-2 paragraphs): Why this matters
   - How this connects to broader trends
   - Potential investment or strategic opportunities
   - What questions this raises
"""

        if context_articles and len(context_articles) > 0:
            prompt += "   - How this relates to or contradicts the recent articles mentioned above\n"

        prompt += """
Format your response as JSON:
{
  "summary": "...",
  "key_insights": ["...", "...", "..."],
  "implications": "..."
}
"""

        return prompt

    def _parse_summary_response(self, response_text):
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'summary': data.get('summary', ''),
                    'key_insights': data.get('key_insights', []),
                    'implications': data.get('implications', '')
                }
        except:
            pass

        # Fallback: return raw text
        return {
            'summary': response_text[:500],
            'key_insights': [],
            'implications': response_text[500:1500] if len(response_text) > 500 else ''
        }

    def generate_cross_article_insights(self, articles):
        """Generate insights across multiple articles"""
        if not self.anthropic_client or len(articles) == 0:
            return ""

        prompt = f"""Analyze these {len(articles)} articles saved today by a venture capitalist.

ARTICLES:
"""

        for idx, article in enumerate(articles, 1):
            prompt += f"""
{idx}. {article.get('title', 'Untitled')}
   Source: {article.get('source', 'Unknown')}
   Summary: {article.get('summary', 'No summary')[:300]}
"""

        prompt += """
Your task: Provide a brief synthesis that helps the reader quickly understand what they saved.

IMPORTANT GUIDELINES:
- If articles share genuine themes or connections, highlight them concisely
- If articles are unrelated, simply acknowledge the variety and briefly note each topic area
- Do NOT force artificial connections between unrelated topics
- Do NOT pad with filler phrases like "These articles collectively suggest..."
- Be direct and crisp - every sentence should add value

FORMAT:
- Use short paragraphs or bullet points
- Aim for 3-5 sentences total for related articles
- For unrelated articles, a simple list of topic areas is sufficient
- No section headers needed - just clean, readable prose

Focus on what's genuinely useful: real patterns, surprising connections, or notable gaps.
"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error generating cross-article insights: {e}")
            return ""
