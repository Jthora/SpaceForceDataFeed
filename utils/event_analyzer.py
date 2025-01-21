from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def analyze_event_frequency(events, time_window='D'):
    """Analyze event frequency over time"""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    if not events:
        # Create empty DataFrame with proper structure and default range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        return pd.DataFrame({'count': [0] * len(dates)}, index=dates)
    
    df = pd.DataFrame([{'date': event['date']} for event in events])
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure dates are timezone-aware
    if df['date'].dt.tz is None:
        df['date'] = df['date'].dt.tz_localize(timezone.utc)
    
    # Ensure minimum date range
    if len(df) == 1:
        df = pd.concat([
            df,
            pd.DataFrame([{'date': df['date'].iloc[0] + timedelta(days=1)}])
        ])
    
    # Create continuous date range
    date_range = pd.date_range(
        start=min(df['date'].min(), start_date),
        end=max(df['date'].max(), end_date),
        freq=time_window
    )
    
    # Calculate frequency with proper resampling
    frequency = df.resample(time_window, on='date').size()
    
    # Ensure all dates in range are included
    frequency = frequency.reindex(date_range, fill_value=0)
    
    return pd.DataFrame({'count': frequency})

def analyze_category_trends(events):
    """Analyze trends in event categories over time"""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    if not events:
        return pd.DataFrame({
            'date': [start_date, end_date],
            'category': ['No Data'] * 2,
            'count': [0] * 2
        })
    
    df = pd.DataFrame(events)
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure dates are timezone-aware
    if df['date'].dt.tz is None:
        df['date'] = df['date'].dt.tz_localize(timezone.utc)
    
    # Create date range from min to max date
    date_range = pd.date_range(
        start=min(df['date'].min(), start_date),
        end=max(df['date'].max(), end_date),
        freq='D'
    )
    categories = sorted(df['category'].unique())
    
    # Initialize empty DataFrame with all combinations
    trends_df = pd.DataFrame([
        {'date': date, 'category': cat, 'count': 0}
        for date in date_range
        for cat in categories
    ])
    
    # Count events for each date-category combination
    actual_counts = df.groupby([df['date'].dt.date, 'category']).size().reset_index()
    actual_counts.columns = ['date', 'category', 'count']
    
    # Update counts in the full DataFrame
    for _, row in actual_counts.iterrows():
        mask = (trends_df['date'].dt.date == row['date']) & (trends_df['category'] == row['category'])
        trends_df.loc[mask, 'count'] = row['count']
    
    return trends_df

def generate_event_stats(events):
    """Generate statistical insights about events"""
    if not events:
        return {
            'total_events': 0,
            'unique_categories': 0,
            'most_common_category': "N/A",
            'avg_events_per_day': 0,
            'busiest_day': "N/A"
        }
    
    df = pd.DataFrame(events)
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure dates are timezone-aware
    if df['date'].dt.tz is None:
        df['date'] = df['date'].dt.tz_localize(timezone.utc)
    
    date_range = (df['date'].max() - df['date'].min()).days + 1
    avg_events = len(events) / max(1, date_range)
    
    stats_dict = {
        'total_events': len(events),
        'unique_categories': len(df['category'].unique()),
        'most_common_category': df['category'].mode().iloc[0] if not df.empty else "N/A",
        'avg_events_per_day': round(avg_events, 1),
        'busiest_day': df['date'].dt.date.mode().iloc[0] if not df.empty else "N/A"
    }
    
    return stats_dict

def calculate_timeline_height(categories):
    """Calculate timeline height based on number of categories"""
    base_height = 100  # Minimum height
    height_per_category = 50  # Height increment per category
    padding = 75  # Extra padding for axes and legend

    return base_height + (len(categories) * height_per_category) + padding

def create_detailed_timeline(events):
    """Create an enhanced timeline visualization with dynamic height"""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)

    if not events:
        fig = go.Figure()
        fig.update_layout(
            title="No events to display",
            height=200,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            xaxis=dict(
                title="Date",
                type='date',
                range=[start_date, end_date]
            ),
            yaxis=dict(
                title="",  # Removed label
                range=[-0.5, 0.5]
            )
        )
        return fig

    df = pd.DataFrame(events)
    df['date'] = pd.to_datetime(df['date'])

    # Ensure dates are timezone-aware
    if df['date'].dt.tz is None:
        df['date'] = df['date'].dt.tz_localize(timezone.utc)

    # Sort categories and create positions
    categories = sorted(df['category'].unique())
    y_positions = {cat: i for i, cat in enumerate(categories)}

    # Calculate dynamic height
    timeline_height = calculate_timeline_height(categories)

    fig = go.Figure()

    for category in categories:
        cat_events = df[df['category'] == category]
        fig.add_trace(go.Scatter(
            x=cat_events['date'],
            y=[y_positions[category]] * len(cat_events),
            mode='markers',
            name=category,
            text=cat_events['title'],
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Date: %{x}<br>" +
                "Category: " + category +
                "<extra></extra>"
            ),
            marker=dict(size=12)
        ))

    date_range = [
        min(df['date'].min(), start_date),
        max(df['date'].max(), end_date)
    ]

    fig.update_layout(
        showlegend=True,
        height=timeline_height,  # Dynamic height
        xaxis=dict(
            title="Date",
            type='date',
            range=date_range
        ),
        yaxis=dict(
            title="",  # Removed label
            ticktext=categories,
            tickvals=list(y_positions.values()),
            range=[-0.5, len(categories) - 0.5]
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    return fig

def generate_event_heatmap(events):
    """Generate a heatmap of event frequency by day and hour"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(24))
    
    if not events:
        empty_data = np.zeros((len(days), len(hours)))
        fig = go.Figure(data=go.Heatmap(
            z=empty_data,
            x=hours,
            y=days,
            colorscale='Viridis',
            zmin=0,
            zmax=1  # Set default maximum for empty data
        ))
    else:
        df = pd.DataFrame(events)
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure dates are timezone-aware
        if df['date'].dt.tz is None:
            df['date'] = df['date'].dt.tz_localize(timezone.utc)
        
        df['day'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        
        # Create base DataFrame with all day-hour combinations
        base_data = pd.DataFrame(
            [(day, hour) for day in days for hour in hours],
            columns=['day', 'hour']
        )
        
        # Count events
        counts = df.groupby(['day', 'hour']).size().reset_index(name='count')
        
        # Merge with base data to ensure all combinations exist
        full_data = base_data.merge(counts, on=['day', 'hour'], how='left').fillna(0)
        
        # Pivot to create heatmap matrix
        heatmap_data = full_data.pivot(index='day', columns='hour', values='count')
        heatmap_data = heatmap_data.reindex(index=days)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=hours,
            y=days,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate="Day: %{y}<br>Hour: %{x}:00<br>Events: %{z}<extra></extra>",
            zmin=0,
            zmax=max(1, heatmap_data.values.max())  # Ensure non-zero range
        ))
    
    fig.update_layout(
        title="Event Frequency Heatmap",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis=dict(
            tickmode='array',
            ticktext=[f"{h:02d}:00" for h in hours],
            tickvals=hours
        )
    )
    
    return fig