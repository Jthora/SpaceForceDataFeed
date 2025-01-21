import streamlit as st
import json
from datetime import datetime, timezone, timedelta
import logging
from typing import Any, Dict, Optional
import time

logger = logging.getLogger(__name__)

# Add debounce mechanism
def debounce(key: str, value: Any, delay: float = 0.5) -> bool:
    """Debounce frequent updates to the same key"""
    current_time = time.time()

    if 'last_update_time' not in st.session_state:
        st.session_state.last_update_time = {}

    if key in st.session_state.last_update_time:
        last_update = st.session_state.last_update_time[key]
        if current_time - last_update < delay:
            return False

    st.session_state.last_update_time[key] = current_time
    return True

def get_cookie(key: str) -> Optional[Any]:
    """Get value from browser cookie"""
    try:
        if 'browser_storage' not in st.session_state:
            st.session_state.browser_storage = {}
        return st.session_state.browser_storage.get(key)
    except Exception as e:
        logger.error(f"Error getting cookie {key}: {str(e)}")
        return None

def set_cookie(key: str, value: Any) -> None:
    """Set value in browser cookie with debouncing"""
    try:
        # Skip update if too frequent
        if not debounce(key, value):
            return

        if 'browser_storage' not in st.session_state:
            st.session_state.browser_storage = {}

        # Only update if value actually changed
        current_value = st.session_state.browser_storage.get(key)
        if current_value != value:
            st.session_state.browser_storage[key] = value

            # Update query parameters using the new API
            current_params = dict(st.query_params)
            current_params[key] = json.dumps(value)
            st.query_params.update(current_params)

            logger.debug(f"Updated browser storage for key: {key}")
    except Exception as e:
        logger.error(f"Error setting cookie {key}: {str(e)}")

def cleanup_old_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Remove old or invalid settings"""
    cleaned_settings = settings.copy()
    current_time = datetime.now(timezone.utc)

    # Clean up old date ranges
    if 'date_range' in cleaned_settings:
        try:
            start_date = datetime.fromisoformat(cleaned_settings['date_range']['start_date'])
            if (current_time - start_date).days > 90:  # Reset if older than 90 days
                cleaned_settings['date_range']['start_date'] = (current_time - timedelta(days=30)).date().isoformat()
        except (ValueError, TypeError):
            cleaned_settings['date_range']['start_date'] = (current_time - timedelta(days=30)).date().isoformat()

    return cleaned_settings

def load_dashboard_settings() -> Dict[str, Any]:
    """Load all dashboard settings from browser storage with cleanup"""
    default_settings = {
        'auto_refresh': True,
        'display_timezone': 'UTC',
        'dashboard_sections': {
            'briefing': {'visible': True, 'order': 1, 'title': '🎯 Strategic Briefing'},
            'timeline': {'visible': True, 'order': 2, 'title': '📅 Event Timeline'},
            'updates_stats': {'visible': True, 'order': 3, 'title': '📰 Updates & Stats'}
        },
        'notification_settings': {
            'desktop_notifications': True,
            'sound_notifications': True,
            'notification_interval': 300
        },
        'date_range': {
            'start_date': (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat(),
            'end_date': datetime.now(timezone.utc).date().isoformat()
        },
        'selected_category': 'All',
        'search_query': ''
    }

    try:
        # Try to load settings from query parameters first
        stored_settings = get_cookie('dashboard_settings')
        if stored_settings:
            # Merge stored settings with defaults to handle new settings
            settings = {**default_settings, **stored_settings}
            # Clean up old settings
            settings = cleanup_old_settings(settings)
            logger.info("Successfully loaded dashboard settings from browser storage")
            return settings
    except Exception as e:
        logger.error(f"Error loading dashboard settings: {str(e)}")

    return default_settings

def save_dashboard_settings(settings: Dict[str, Any]) -> None:
    """Save all dashboard settings to browser storage with optimization"""
    try:
        # Clean up settings before saving
        settings = cleanup_old_settings(settings)
        set_cookie('dashboard_settings', settings)
        logger.info("Successfully saved dashboard settings to browser storage")
    except Exception as e:
        logger.error(f"Error saving dashboard settings: {str(e)}")