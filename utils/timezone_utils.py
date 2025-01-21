import pytz
from datetime import datetime, timezone
import streamlit as st

def init_timezone_state():
    """Initialize timezone-related session state"""
    if 'display_timezone' not in st.session_state:
        st.session_state.display_timezone = 'UTC'

def get_timezone_list():
    """Get list of common timezones"""
    common_zones = [
        'UTC',
        'US/Pacific',
        'US/Mountain',
        'US/Central',
        'US/Eastern',
        'Europe/London',
        'Europe/Paris',
        'Asia/Tokyo',
        'Australia/Sydney'
    ]
    return common_zones

def add_timezone_selector():
    """Add timezone selector to sidebar"""
    st.sidebar.subheader("Timezone Settings")
    zones = get_timezone_list()
    st.session_state.display_timezone = st.sidebar.selectbox(
        "Display Timezone",
        zones,
        index=zones.index(st.session_state.display_timezone)
    )

def convert_timezone(dt, target_timezone=None):
    """Convert datetime to target timezone"""
    if dt is None:
        return None
        
    # Ensure datetime is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # If no target timezone specified, use session state
    if target_timezone is None:
        target_timezone = st.session_state.display_timezone
    
    # Convert to target timezone
    target_tz = pytz.timezone(target_timezone)
    return dt.astimezone(target_tz)

def format_datetime(dt):
    """Format datetime with timezone indicator"""
    if dt is None:
        return ""
        
    converted_dt = convert_timezone(dt)
    return converted_dt.strftime("%Y-%m-%d %H:%M %Z")
