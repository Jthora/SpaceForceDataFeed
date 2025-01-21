import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
import hashlib
import json
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection"""
    print(os.getenv('DATABASE_URL'))  # Add this line to debug
    logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    return psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=RealDictCursor
    )

def calculate_content_hash(content_dict: Dict[str, Any]) -> str:
    """Calculate hash of content for deduplication"""
    # Sort dictionary to ensure consistent hash
    content_str = json.dumps(dict(sorted(content_dict.items())), sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()

def ensure_category(category_name: str) -> Optional[int]:
    """Ensure category exists and return its ID"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Try to get existing category
                cur.execute(
                    "SELECT id FROM categories WHERE name = %s",
                    (category_name,)
                )
                result = cur.fetchone()

                if result and isinstance(result, dict):
                    return int(result['id'])

                # Create new category if it doesn't exist
                cur.execute(
                    "INSERT INTO categories (name) VALUES (%s) RETURNING id",
                    (category_name,)
                )
                conn.commit()
                result = cur.fetchone()
                return int(result['id']) if result and isinstance(result, dict) else None
    except Exception:
        return None

# db.py
def save_event(event_data):
    """Save an event to the database with deduplication"""
    logger.debug(f"Saving event: {event_data}")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            category_id = ensure_category(event_data['category'])
            if not category_id:
                logger.error("Failed to ensure category")
                return None
            
            # Ensure date is timezone-aware
            event_date = event_data['date']
            if event_date.tzinfo is None:
                event_date = event_date.replace(tzinfo=timezone.utc)
            
            # Calculate content hash
            content_for_hash = {
                'title': event_data['title'],
                'description': event_data.get('description', ''),
                'location': event_data.get('location', ''),
                'category': event_data['category']
            }
            content_hash = calculate_content_hash(content_for_hash)
            
            # Check for existing event with same hash
            cur.execute(
                "SELECT id FROM events WHERE content_hash = %s",
                (content_hash,)
            )
            if cur.fetchone():
                logger.debug("Event already exists")
                return None  # Event already exists
            
            try:
                cur.execute("""
                    INSERT INTO events (
                        title, description, event_date, location, 
                        category_id, content_hash
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (content_hash) DO NOTHING
                    RETURNING id
                """, (
                    event_data['title'],
                    event_data.get('description', ''),
                    event_date,
                    event_data.get('location', ''),
                    category_id,
                    content_hash
                ))
                conn.commit()
                result = cur.fetchone()
                logger.debug(f"Event saved with ID: {result['id'] if result else 'None'}")
                return result['id'] if result else None
            except Exception as e:
                logger.error(f"Error saving event: {str(e)}")
                conn.rollback()
                return None

# filepath: /Users/jono/Documents/GitHub/SpaceForceDataFeed/utils/db.py
def save_news(news_data):
    """Save a news item to the database with deduplication"""
    logger.debug(f"Saving news: {news_data}")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            category_id = ensure_category(news_data['category'])
            if not category_id:
                logger.error("Failed to ensure category")
                return None
            
            # Ensure date is timezone-aware
            news_date = news_data['date']
            if news_date.tzinfo is None:
                news_date = news_date.replace(tzinfo=timezone.utc)
            
            # Calculate content hash
            content_for_hash = {
                'title': news_data['title'],
                'description': news_data.get('description', ''),
                'source': news_data.get('source', ''),
                'category': news_data['category']
            }
            content_hash = calculate_content_hash(content_for_hash)
            
            try:
                cur.execute("""
                    INSERT INTO news (
                        title, description, publication_date, source, 
                        link, category_id, content_hash, image_url
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (title, source) DO UPDATE
                    SET 
                        description = EXCLUDED.description,
                        publication_date = EXCLUDED.publication_date,
                        link = EXCLUDED.link,
                        content_hash = EXCLUDED.content_hash,
                        image_url = EXCLUDED.image_url,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (
                    news_data['title'],
                    news_data.get('description', ''),
                    news_date,
                    news_data.get('source', ''),
                    news_data.get('link', ''),
                    category_id,
                    content_hash,
                    news_data.get('image_url')
                ))
                conn.commit()
                result = cur.fetchone()
                logger.debug(f"News saved with ID: {result['id'] if result else 'None'}")
                return result['id'] if result else None
            except Exception as e:
                logger.error(f"Error saving news: {str(e)}")
                conn.rollback()
                return None

def convert_to_dict(row):
    """Convert database row to dictionary with proper date field name"""
    if not row:
        return None
    
    result = dict(row)
    
    # Convert publication_date or event_date to date for consistency and ensure timezone awareness
    if 'publication_date' in result:
        date = result.pop('publication_date')
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        result['date'] = date
    elif 'event_date' in result:
        date = result.pop('event_date')
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        result['date'] = date
    
    # Ensure all required fields are present
    if 'category_id' in result:
        result.pop('category_id')  # Remove as we're using the category name
    
    return result

def get_events(start_date=None, end_date=None, category=None):
    """Retrieve events from the database with optional filters"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT e.*, c.name as category
                FROM events e
                JOIN categories c ON e.category_id = c.id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                if start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=timezone.utc)
                query += " AND e.event_date >= %s"
                params.append(start_date)
            if end_date:
                if end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=timezone.utc)
                query += " AND e.event_date <= %s"
                params.append(end_date)
            if category and category != "All":
                query += " AND c.name = %s"
                params.append(category)
            
            query += " ORDER BY e.event_date DESC"
            
            cur.execute(query, params)
            results = cur.fetchall()
            return [convert_to_dict(row) for row in results]

def get_news(start_date=None, end_date=None, category=None):
    """Retrieve news from the database with optional filters"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT n.*, c.name as category
                FROM news n
                JOIN categories c ON n.category_id = c.id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                if start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=timezone.utc)
                query += " AND n.publication_date >= %s"
                params.append(start_date)
            if end_date:
                if end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=timezone.utc)
                query += " AND n.publication_date <= %s"
                params.append(end_date)
            if category and category != "All":
                query += " AND c.name = %s"
                params.append(category)
            
            query += " ORDER BY n.publication_date DESC"
            
            cur.execute(query, params)
            results = cur.fetchall()
            return [convert_to_dict(row) for row in results]