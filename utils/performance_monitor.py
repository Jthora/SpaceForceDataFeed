import streamlit as st
import psutil
import logging
import gc
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_memory_usage() -> Dict[str, float]:
    """Monitor memory usage of the application"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # RSS in MB
            'vms': memory_info.vms / 1024 / 1024   # VMS in MB
        }
    except Exception as e:
        logger.error(f"Error getting memory usage: {str(e)}")
        return {'rss': 0, 'vms': 0}

def cleanup_session_state():
    """Clean up old or unused session state variables"""
    try:
        current_time = datetime.now()

        # List of keys that should never be cleaned
        protected_keys = {'settings_initialized', 'dashboard_sections', 'last_refresh'}

        # Clean up old cached data
        keys_to_remove = []
        for key in st.session_state:
            if key not in protected_keys:
                # If the key has a timestamp and is old, mark for removal
                if isinstance(st.session_state[key], dict) and '_timestamp' in st.session_state[key]:
                    if current_time - st.session_state[key]['_timestamp'] > timedelta(minutes=30):
                        keys_to_remove.append(key)

        # Remove marked keys
        for key in keys_to_remove:
            del st.session_state[key]

        # Force garbage collection
        gc.collect()

        logger.info(f"Cleaned up {len(keys_to_remove)} old session state entries")
    except Exception as e:
        logger.error(f"Error cleaning up session state: {str(e)}")

def monitor_performance() -> Dict[str, float]:
    """Monitor and optimize application performance"""
    try:
        # Initialize performance monitoring in session state
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = {
                'last_cleanup': datetime.now(),
                'memory_usage': []
            }

        current_time = datetime.now()

        # Check if cleanup is needed (every 5 minutes)
        if current_time - st.session_state.performance_metrics['last_cleanup'] > timedelta(minutes=5):
            cleanup_session_state()
            st.session_state.performance_metrics['last_cleanup'] = current_time

        # Monitor memory usage
        memory_usage = get_memory_usage()
        st.session_state.performance_metrics['memory_usage'].append({
            'timestamp': current_time,
            'usage': memory_usage
        })

        # Keep only last hour of metrics
        st.session_state.performance_metrics['memory_usage'] = [
            m for m in st.session_state.performance_metrics['memory_usage']
            if current_time - m['timestamp'] <= timedelta(hours=1)
        ]

        # Log if memory usage is high
        if memory_usage['rss'] > 500:  # Alert if RSS memory usage exceeds 500MB
            logger.warning(f"High memory usage detected: {memory_usage['rss']:.2f} MB RSS")
            cleanup_session_state()

        return memory_usage

    except Exception as e:
        logger.error(f"Error in performance monitoring: {str(e)}")
        return {'rss': 0, 'vms': 0}

def optimize_cache():
    """Optimize Streamlit cache usage"""
    try:
        # Clear old caches if memory usage is high
        memory_usage = get_memory_usage()
        if memory_usage['rss'] > 500:  # MB
            st.cache_data.clear()
            st.cache_resource.clear()
            logger.info("Cleared Streamlit caches due to high memory usage")

        # Ensure essential caches are preserved
        if 'dashboard_sections' in st.session_state:
            st.session_state.dashboard_sections = st.session_state.dashboard_sections

    except Exception as e:
        logger.error(f"Error optimizing cache: {str(e)}")