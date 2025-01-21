import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import plotly.express as px
import logging
from utils.data_fetcher import fetch_space_force_news, fetch_space_force_events, NEWS_SOURCES
from utils.data_processor import (
    filter_events_by_date,
    filter_events_by_category,
    search_events,
    get_event_categories,
    format_date,
    prepare_timeline_data
)
from utils.notification_manager import init_notification_state, check_new_events, get_notification_settings
from utils.timezone_utils import init_timezone_state, add_timezone_selector, convert_timezone
from utils.event_analyzer import (
    generate_event_stats,
    create_detailed_timeline,
    generate_event_heatmap,
    analyze_category_trends
)
from utils.category_manager import render_category_manager
from utils.ai_briefing import generate_briefing
from typing import List, Dict
import json
import html
from utils.browser_storage import load_dashboard_settings, save_dashboard_settings
from utils.performance_monitor import monitor_performance, optimize_cache
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
print(os.getenv('DATABASE_URL'))  # This should print the correct DATABASE_URL
print(os.getenv('PGUSER'))        # This should print 'jono'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log environment variables to verify
logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
logger.info(f"PGUSER: {os.getenv('PGUSER')}")
logger.info(f"PGPASSWORD: {os.getenv('PGPASSWORD')}")

def calculate_timeline_height(categories):
    """Calculate timeline height based on number of categories"""
    base_height = 150
    height_per_category = 30
    return base_height + len(categories) * height_per_category

# Initialize session state with saved settings
if 'settings_initialized' not in st.session_state:
    settings = load_dashboard_settings()

    # Initialize all session state variables from saved settings
    st.session_state.dashboard_sections = settings['dashboard_sections']
    st.session_state.last_refresh = datetime.now()
    st.session_state.settings_initialized = True

    # Update query parameters with current settings
    st.query_params.update({
        'auto_refresh': str(settings['auto_refresh']).lower(),
        'selected_category': settings['selected_category'],
        'search_query': settings['search_query']
    })

# Page configuration
st.set_page_config(
    page_title="Space Force Events",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Monitor and optimize performance
memory_usage = monitor_performance()
if memory_usage:
    logger.info(f"Current memory usage: RSS={memory_usage['rss']:.2f}MB, VMS={memory_usage['vms']:.2f}MB")

# Optimize cache periodically
optimize_cache()

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Initialize notification state
init_notification_state()

# Initialize timezone state
init_timezone_state()

# Fetch data first
with st.spinner("Fetching latest Space Force updates..."):
    news_items = fetch_space_force_news()
    events = fetch_space_force_events()

    # Check for new events and show notification
    new_events = check_new_events(events + news_items)
    if new_events:
        st.success(f"🔔 {len(new_events)} new events available!")

# Header
st.title("🚀 Space Force Events")

# Sidebar
st.sidebar.header("Dashboard Controls")

# Search box with saved value
search_query = st.sidebar.text_input(
    "🔍 Search events",
    value=st.session_state.get('search_box', ''),
    key="search_box",
    on_change=lambda: save_dashboard_settings({
        **load_dashboard_settings(),
        'search_query': st.session_state.search_box
    })
)

# Timezone selector with saved preference
add_timezone_selector()

# Notification settings with saved preferences
notification_settings = get_notification_settings()

# Auto-refresh toggle with saved state
auto_refresh = st.sidebar.checkbox(
    "Auto-refresh (5 min)",
    value=st.session_state.get('auto_refresh', True),
    key="auto_refresh",
    on_change=lambda: save_dashboard_settings({
        **load_dashboard_settings(),
        'auto_refresh': st.session_state.auto_refresh
    })
)

if auto_refresh and (datetime.now() - st.session_state.last_refresh) > timedelta(minutes=5):
    st.rerun()
    st.session_state.last_refresh = datetime.now()

# Category Management
render_category_manager()

# Date filter with saved range
st.sidebar.subheader("Date Range")
settings = load_dashboard_settings()
current_date = datetime.now().date()

start_date_input = st.sidebar.date_input(
    "Start date",
    value=datetime.fromisoformat(settings['date_range']['start_date']).date(),
    max_value=current_date,
    key="start_date",
    on_change=lambda: save_dashboard_settings({
        **load_dashboard_settings(),
        'date_range': {
            'start_date': st.session_state.start_date.isoformat(),
            'end_date': st.session_state.end_date.isoformat()
        }
    })
)

end_date_input = st.sidebar.date_input(
    "End date",
    value=datetime.fromisoformat(settings['date_range']['end_date']).date(),
    min_value=start_date_input,
    max_value=current_date,
    key="end_date",
    on_change=lambda: save_dashboard_settings({
        **load_dashboard_settings(),
        'date_range': {
            'start_date': st.session_state.start_date.isoformat(),
            'end_date': st.session_state.end_date.isoformat()
        }
    })
)

# Category filter with saved selection
categories = ["All"] + get_event_categories(news_items + events)
selected_category = st.sidebar.selectbox(
    "Filter by Category",
    categories,
    index=categories.index(settings['selected_category']) if settings['selected_category'] in categories else 0,
    key="selected_category",
    on_change=lambda: save_dashboard_settings({
        **load_dashboard_settings(),
        'selected_category': st.session_state.selected_category
    })
)

# Section visibility and order controls with saved state
st.sidebar.markdown("---")
st.sidebar.subheader("Sub-Section Controls")
section_controls = st.sidebar.container()

with section_controls:
    st.markdown("##### Visibility")

    # Batch update section visibility
    visibility_updates = {}
    for section_id, section in st.session_state.dashboard_sections.items():
        visibility_updates[section_id] = st.checkbox(
            f"Show {section['title']}",
            value=section['visible'],
            key=f"visible_{section_id}"
        )

    # Only update if changes detected
    if any(visibility_updates[sid] != section['visible']
           for sid, section in st.session_state.dashboard_sections.items()):
        for section_id, is_visible in visibility_updates.items():
            st.session_state.dashboard_sections[section_id]['visible'] = is_visible
        save_dashboard_settings({
            **load_dashboard_settings(),
            'dashboard_sections': st.session_state.dashboard_sections
        })


    st.markdown("##### Section Order")
    st.markdown("Drag sections to reorder:")

    ordered_sections = sorted(
        st.session_state.dashboard_sections.items(),
        key=lambda x: x[1]['order']
    )

    for i, (section_id, section) in enumerate(ordered_sections):
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if i > 0:
                if st.button("↑", key=f"up_{section_id}"):
                    prev_section = ordered_sections[i-1][0]
                    current_order = section['order']
                    st.session_state.dashboard_sections[section_id]['order'] = st.session_state.dashboard_sections[prev_section]['order']
                    st.session_state.dashboard_sections[prev_section]['order'] = current_order
                    save_dashboard_settings({
                        **load_dashboard_settings(),
                        'dashboard_sections': st.session_state.dashboard_sections
                    })
                    st.rerun()
        with col2:
            st.markdown(section['title'])



# RSS Feed Management
st.sidebar.markdown("---")
st.sidebar.subheader("RSS Feed Management")

# Display current feeds
st.sidebar.caption("Currently Monitored Feeds:")
for category, sources in NEWS_SOURCES.items():
    with st.sidebar.expander(f"📑 {category}"):
        for source in sources:
            st.write(f"• {source['name']}")

# Add new RSS feed
new_feed_name = st.sidebar.text_input("Feed Name", key="new_feed_name")
new_feed_url = st.sidebar.text_input("Feed URL", key="new_feed_url")
new_feed_category = st.sidebar.selectbox(
    "Feed Category",
    ["Military Space", "Space Industry", "Space Science", "Official Updates", "Defense Updates", "Space Technology"]
)

if st.sidebar.button("Add Feed"):
    st.sidebar.info("Feature coming soon: Add custom RSS feeds")

# Convert date inputs to datetime for filtering
start_datetime = datetime.combine(start_date_input, datetime.min.time())
end_datetime = datetime.combine(end_date_input, datetime.max.time())

# Filter data
filtered_items = news_items + events
filtered_items = filter_events_by_date(filtered_items, start_datetime, end_datetime)
filtered_items = filter_events_by_category(filtered_items, selected_category)
if search_query:
    filtered_items = search_events(filtered_items, search_query)

# Tabs for different views
tab1, tab2 = st.tabs(["📊 Dashboard", "📈 Detailed Analysis"])

with tab1:
    # Get visible sections in correct order
    visible_sections = sorted(
        [(section_id, section) for section_id, section in st.session_state.dashboard_sections.items() if section['visible']],
        key=lambda x: x[1]['order']
    )

    for section_id, section in visible_sections:
        if section_id == 'briefing' and section['visible']:
            st.subheader(section['title'])
            with st.spinner("Generating briefing..."):
                briefing = generate_briefing(filtered_items)
                st.markdown(
                    f"""
                    <div style='background: rgba(26, 31, 36, 0.8); padding: 1rem; border-radius: 5px; 
                    border: 1px solid rgba(0, 242, 255, 0.2);'>
                        {briefing}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        elif section_id == 'timeline' and section['visible']:
            st.subheader(section['title'])
            timeline_data = prepare_timeline_data(filtered_items)
            if not timeline_data.empty:
                # Convert timeline dates to selected timezone
                timeline_data['Start'] = timeline_data['Start'].apply(convert_timezone)
                timeline_data['Finish'] = timeline_data['Finish'].apply(convert_timezone)

                categories = timeline_data['Category'].unique()
                timeline_height = calculate_timeline_height(categories)

                fig = px.timeline(
                    timeline_data,
                    x_start="Start",
                    x_end="Finish",
                    y="Category",
                    color="Category",
                    hover_data=["Description"]
                )
                fig.update_layout(
                    showlegend=True,
                    height=timeline_height,  # Dynamic height based on categories
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    xaxis=dict(
                        title=f"Date ({st.session_state.display_timezone})",
                        type='date',
                        range=[
                            convert_timezone(start_datetime),
                            convert_timezone(end_datetime)
                        ]
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No events available for timeline visualization.")

        elif section_id == 'updates_stats' and section['visible']:
            # Create the columns for the paired sections
            main_col, stats_col = st.columns([2, 1])

            # Updates section
            with main_col:
                st.subheader("📰 Latest Updates")
                if not filtered_items:
                    st.info("No events found matching your criteria.")
                else:
                    for item in filtered_items:
                        with st.container():
                            is_new = any(new_event['title'] == item['title'] for new_event in (new_events or []))
                            title_prefix = "🔔 NEW! " if is_new else ""

                            # Sanitize text content
                            title = html.escape(item['title'])
                            description = html.escape(item.get('description', '')[:200]) + "..." if item.get('description') else ""
                            category = html.escape(item['category'])
                            has_image = 'image_url' in item and item['image_url']

                            st.markdown(
                                f"""
                                <div class="event-card{' new-event' if is_new else ''}" id="article-{hash(item['title'])}">
                                    <div class="event-card-header">
                                        <h3>{title_prefix}{title}</h3>
                                        <div class="event-card-meta">
                                            <span>{format_date(item['date'])}</span>
                                            <span class="category-pill">{category}</span>
                                        </div>
                                    </div>
                                    <div class="event-card-content{' has-image' if has_image else ''}">
                                        <div class="event-card-text">
                                            <p>{description}</p>
                                            {'<div class="event-card-link"><a href="' + item["link"] + '" target="_blank">Read more →</a></div>' if 'link' in item else ''}
                                        </div>
                                        {'<div class="event-card-image"><img src="' + item["image_url"] + '" class="event-image" alt="Event image" loading="lazy" /></div>' if has_image else ''}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

            # Stats section
            with stats_col:
                st.subheader("📊 Quick Stats")
                if filtered_items:
                    df_counts = pd.DataFrame(filtered_items)
                    category_counts = df_counts['category'].value_counts()
                    st.bar_chart(category_counts)

                    today_count = len([i for i in filtered_items if i['date'].date() == current_date])
                    st.metric(
                        label="Total Events",
                        value=len(filtered_items),
                        delta=f"{today_count} new today" if today_count > 0 else None
                    )
                else:
                    st.info("No data available for statistics.")

with tab2:
    st.header("📈 Detailed Event Analysis")

    if not filtered_items:
        st.info("No events available for analysis. Try adjusting your filters.")
    else:
        # Event Statistics
        stats = generate_event_stats(filtered_items)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Events", stats['total_events'])
        with col2:
            st.metric("Unique Categories", stats['unique_categories'])
        with col3:
            st.metric("Avg Events/Day", stats['avg_events_per_day'])

        # Detailed Timeline
        st.subheader("📅 Detailed Event Timeline")
        detailed_timeline = create_detailed_timeline(filtered_items)
        st.plotly_chart(detailed_timeline, use_container_width=True)

        # Event Frequency Heatmap
        st.subheader("🗓️ Event Frequency Heatmap")
        heatmap = generate_event_heatmap(filtered_items)
        st.plotly_chart(heatmap, use_container_width=True)

        # Category Trends
        st.subheader("📊 Category Trends")
        trends_data = analyze_category_trends(filtered_items)
        if not trends_data.empty:
            fig = px.line(
                trends_data,
                x='date',
                y='count',
                color='category',
                title="Category Trends Over Time"
            )
            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                xaxis=dict(
                    title="Date",
                    type='date',
                    range=[start_datetime, end_datetime]
                ),
                yaxis_title="Number of Events"
            )
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <small>Data refreshed at: {}</small>
    </div>
    """.format(format_date(datetime.now(timezone.utc))),
    unsafe_allow_html=True
)