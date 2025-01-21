import streamlit as st
from datetime import datetime, timedelta, timezone
from plyer import notification

def init_notification_state():
    """Initialize notification-related session state variables"""
    if 'last_notification_time' not in st.session_state:
        st.session_state.last_notification_time = datetime.now(timezone.utc)
    if 'notified_events' not in st.session_state:
        st.session_state.notified_events = set()
    if 'notifications_enabled' not in st.session_state:
        st.session_state.notifications_enabled = True

def check_new_events(events):
    """Check for new events and trigger notifications"""
    if not st.session_state.notifications_enabled:
        return []

    current_time = datetime.now(timezone.utc)
    new_events = []

    for event in events:
        event_id = f"{event['title']}_{event['date']}"
        event_date = event['date']
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)

        is_recent = (current_time - event_date) <= timedelta(hours=24)

        if event_id not in st.session_state.notified_events and is_recent:
            new_events.append(event)
            st.session_state.notified_events.add(event_id)

    if new_events and (current_time - st.session_state.last_notification_time) > timedelta(minutes=5):
        send_notification(new_events)
        st.session_state.last_notification_time = current_time
        return new_events

    return []

def send_notification(new_events):
    """Send desktop notification for new events"""
    try:
        notification.notify(
            title="New Space Force Events",
            message=f"{len(new_events)} new event(s) available!\n{new_events[0]['title']}",
            app_icon=None,
            timeout=10,
        )
    except Exception as e:
        st.warning(f"Could not send desktop notification: {str(e)}")

def get_notification_settings():
    """Add notification settings to sidebar"""
    st.sidebar.subheader("Notification Settings")
    st.session_state.notifications_enabled = st.sidebar.checkbox(
        "Enable Notifications",
        value=st.session_state.notifications_enabled,
        help="Get notified when new events are available"
    )