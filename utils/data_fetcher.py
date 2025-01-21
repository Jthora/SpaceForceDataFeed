import streamlit as st
import requests
import feedparser
import time
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Optional
from urllib.robotparser import RobotFileParser
from dateutil import parser as date_parser
import threading
from html import unescape
import re
from bs4 import BeautifulSoup
from utils.db import save_news, save_event, get_news, get_events
from utils.fallback_illustrations import get_fallback_image_url
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_featured_image_url(entry: Dict[str, Any]) -> Optional[str]:
    """Extract featured image URL from feed entry metadata"""
    try:
        # Try media_content first
        if hasattr(entry, 'media_content'):
            media_content = entry.get('media_content', [])
            if media_content and 'url' in media_content[0]:
                return media_content[0]['url']

        # Try media_thumbnail next
        if hasattr(entry, 'media_thumbnail'):
            thumbnails = entry.get('media_thumbnail', [])
            if thumbnails and 'url' in thumbnails[0]:
                return thumbnails[0]['url']

        # Finally try links
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    return link.get('href')

        return None
    except Exception as e:
        logger.error(f"Error extracting featured image URL: {str(e)}")
        return None

def extract_first_image_url(html_content: str) -> Optional[str]:
    """Extract the first image URL from HTML content"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # First try to find image in figure/img tags
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
        return None
    except Exception as e:
        logger.error(f"Error extracting image URL: {str(e)}")
        return None

def clean_html_content(html_content: str) -> str:
    """Clean HTML content to plain text"""
    try:
        # Remove HTML tags but preserve meaningful whitespace
        soup = BeautifulSoup(html_content, 'html.parser')
        # Get text while preserving some structure
        text = soup.get_text(separator=' ', strip=True)
        # Clean up extra whitespace
        text = ' '.join(text.split())
        return text
    except Exception as e:
        logger.error(f"Error cleaning HTML content: {str(e)}")
        return html_content

def process_html_content(content: str, source_name: str, category: str) -> Dict[str, str]:
    """Process HTML content to extract clean text and images"""
    try:
        logger.info(f"Processing HTML content from {source_name}")

        # Extract image first
        image_url = extract_first_image_url(content)
        if image_url:
            logger.debug(f"Found image URL in content from {source_name}: {image_url}")

        # Clean text content
        clean_text = clean_html_content(content)
        logger.debug(f"Cleaned text from {source_name}: {clean_text[:100]}...")

        return {
            'text': clean_text,
            'image_url': image_url
        }
    except Exception as e:
        logger.error(f"Error processing HTML content from {source_name}: {str(e)}")
        return {
            'text': content,
            'image_url': None
        }

def fetch_feed(source: Dict[str, str]) -> List[Dict[str, Any]]:
    """Fetch and process a single RSS feed"""
    try:
        if not check_robots_txt(source['url']):
            logger.warning(f"Robots.txt disallows scraping {source['url']}")
            return []

        domain = '/'.join(source['url'].split('/')[:3])
        rate_limiter.wait(domain)

        logger.info(f"Fetching feed from {source['name']} ({source['url']})")
        feed = feedparser.parse(source['url'])
        news_items = []

        for entry in feed.entries:
            try:
                # Get publication date
                pub_date = entry.get('published', entry.get('updated', None))
                if pub_date:
                    parsed_date = parse_date(pub_date)
                else:
                    parsed_date = datetime.now(timezone.utc)

                # Get description and process content
                description = entry.get('summary', entry.get('description', ''))
                processed_content = process_html_content(description, source['name'], source['category'])

                # Try to get image URL in order of preference:
                # 1. Featured image from feed metadata
                # 2. Image from HTML content
                # 3. Fallback category-based image
                image_url = get_featured_image_url(entry)
                if not image_url:
                    image_url = processed_content['image_url']
                if not image_url:
                    image_url = get_fallback_image_url(source['category'])

                news_data = {
                    'title': clean_html_content(entry.get('title', '')),
                    'date': parsed_date,
                    'description': processed_content['text'],
                    'link': entry.get('link', ''),
                    'category': source['category'],
                    'source': source['name'],
                    'image_url': image_url
                }

                save_news(news_data)
                news_items.append(news_data)
                logger.debug(f"Successfully processed entry: {news_data['title']}")

            except Exception as e:
                logger.error(f"Error processing entry from {source['name']}: {str(e)}")
                continue

        logger.info(f"Successfully fetched {len(news_items)} items from {source['name']}")
        return news_items

    except Exception as e:
        logger.error(f"Error fetching feed from {source['name']}: {str(e)}")
        return []

class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.delay = 60.0 / requests_per_minute
        self.last_request: Dict[str, float] = {}
        self.lock = threading.Lock()

    def wait(self, domain: str) -> None:
        with self.lock:
            if domain in self.last_request:
                elapsed = time.time() - self.last_request[domain]
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
            self.last_request[domain] = time.time()

rate_limiter = RateLimiter()

def check_robots_txt(url: str) -> bool:
    """Check if scraping is allowed for the URL"""
    try:
        rp = RobotFileParser()
        domain = '/'.join(url.split('/')[:3])
        rp.set_url(f"{domain}/robots.txt")
        rp.read()
        return rp.can_fetch("*", url)
    except Exception as e:
        logging.warning(f"Could not check robots.txt for {url}: {str(e)}")
        return True

def parse_date(date_str: str) -> datetime:
    """Parse date string to timezone-aware datetime"""
    try:
        dt = date_parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        logging.error(f"Error parsing date {date_str}: {str(e)}")
        return datetime.now(timezone.utc)


NEWS_SOURCES = {
    'Military': [
        {
            'name': 'Defense News',
            'url': 'https://www.defensenews.com/arc/outboundfeeds/rss/category/space/?outputType=xml',
            'category': 'Military Space'
        },
        {
            'name': 'Military.com',
            'url': 'https://www.military.com/rss-feeds/space-force-news.xml',
            'category': 'Military Space'
        }
    ],
    'Space Industry': [
        {
            'name': 'SpaceNews',
            'url': 'https://spacenews.com/feed/',
            'category': 'Space Industry'
        },
        {
            'name': 'Space.com',
            'url': 'https://www.space.com/feeds/all',
            'category': 'Space Science'
        }
    ],
    'Government': [
        {
            'name': 'Space Force',
            'url': 'https://www.spaceforce.mil/DesktopModules/ArticleCS/RSS.aspx?ContentType=1&Site=1060',
            'category': 'Official Updates'
        },
        {
            'name': 'Defense.gov',
            'url': 'https://www.defense.gov/News/RSS/GeographicRegions/',
            'category': 'Defense Updates'
        }
    ],
    'Science/Tech': [
        {
            'name': 'NASA',
            'url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
            'category': 'Space Science'
        },
        {
            'name': 'Space Tech',
            'url': 'https://techcrunch.com/tag/space/feed/',
            'category': 'Space Technology'
        }
    ]
}

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_space_force_news() -> List[Dict[str, Any]]:
    """Fetch Space Force news from multiple sources"""
    all_news = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_source = {}

        for category in NEWS_SOURCES.values():
            for source in category:
                future = executor.submit(fetch_feed, source)
                future_to_source[future] = source['name']

        for future in concurrent.futures.as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                news_items = future.result()
                all_news.extend(news_items)
                logger.info(f"Successfully fetched {len(news_items)} items from {source_name}")
            except Exception as e:
                logger.error(f"Error processing {source_name}: {str(e)}")

    return get_news()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_space_force_events() -> List[Dict[str, Any]]:
    """Fetch Space Force upcoming events"""
    try:
        # In a real implementation, this would fetch from an events API
        events = [
            {
                'title': 'Space Force Training Program',
                'date': datetime.now(timezone.utc),
                'description': 'Annual training program for Space Force personnel',
                'category': 'Training',
                'location': 'Virtual Event'
            },
            {
                'title': 'Space Systems Command Briefing',
                'date': datetime.now(timezone.utc),
                'description': 'Monthly briefing on space systems and operations',
                'category': 'Briefing',
                'location': 'Colorado Springs, CO'
            }
        ]

        for event in events:
            save_event(event)

        return get_events()
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        return []

def init_background_scraping() -> None:
    """Initialize background scraping thread"""
    def scrape_periodically() -> None:
        while True:
            try:
                fetch_space_force_news()
                fetch_space_force_events()
                logger.info("Background scraping completed successfully")
            except Exception as e:
                logger.error(f"Error in background scraping: {str(e)}")
            time.sleep(1800)  # Wait 30 minutes

    thread = threading.Thread(target=scrape_periodically, daemon=True)
    thread.start()
    logger.info("Background scraping initialized")

# Initialize background scraping when the module is imported
init_background_scraping()