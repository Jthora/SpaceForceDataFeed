from datetime import datetime, timedelta, timezone
import pandas as pd
from utils.timezone_utils import convert_timezone, format_datetime

def filter_events_by_date(events, start_date, end_date):
    """Filter events based on date range"""
    # Ensure start and end dates are timezone-aware
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    return [
        event for event in events
        if start_date <= event['date'].replace(tzinfo=timezone.utc) <= end_date
    ]

def filter_events_by_category(events, category):
    """Filter events by category"""
    if category == "All":
        return events
    return [
        event for event in events
        if event['category'] == category
    ]

def search_events(events, search_query):
    """Search events by title and description"""
    search_query = search_query.lower()
    return [
        event for event in events
        if search_query in event['title'].lower()
        or search_query in event['description'].lower()
    ]

def get_event_categories(events):
    """Get unique categories from events"""
    categories = set()
    for event in events:
        categories.add(event['category'])
    return sorted(list(categories))

def format_date(date):
    """Format datetime object to string with timezone"""
    return format_datetime(date)

def prepare_timeline_data(events):
    """Prepare data for timeline visualization"""
    timeline_data = []
    for event in events:
        # Ensure date is timezone-aware
        event_date = event['date']
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)

        timeline_data.append({
            'Category': event['category'],  # Changed from 'Task' to 'Category'
            'Start': event_date,
            'Finish': event_date + timedelta(hours=1),  # Assume 1-hour duration for visualization
            'Description': event['title']
        })
    return pd.DataFrame(timeline_data)