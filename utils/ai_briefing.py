import os
from openai import OpenAI
from datetime import datetime, timedelta, timezone
import logging
import time
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with proper error handling
def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client with error handling"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return None
    return OpenAI(api_key=api_key)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def generate_briefing(events: List[Dict[str, Any]]) -> str:
    """Generate an AI briefing summary of recent events with robust error handling"""
    try:
        client = get_openai_client()
        if not client:
            return "AI Briefing unavailable: API configuration issue"

        # Ensure current time is timezone-aware
        current_time = datetime.now(timezone.utc)
        logger.info(f"Generating briefing at {current_time}")

        # Sort events by date and get the last 24 hours
        recent_events = [
            event for event in events
            if event['date'] >= current_time - timedelta(hours=24)
        ]

        if not recent_events:
            logger.info("No recent events found in the last 24 hours")
            return "No significant events in the last 24 hours."

        # Prepare events data for the prompt
        events_text = "\n".join([
            f"- {event['title']} ({event['category']}) - {event['description'][:200]}..."
            for event in recent_events
        ])

        logger.info(f"Processing {len(recent_events)} events for briefing")

        # Generate briefing using OpenAI with rate limiting
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Space Force intelligence analyst providing "
                            "concise, professional briefings. Focus on key developments, "
                            "emerging patterns, and strategic implications. Use clear, "
                            "military-style communication."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Generate a brief, strategic analysis of these Space Force "
                            f"related events from the last 24 hours:\n\n{events_text}"
                        )
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            briefing = response.choices[0].message.content
            logger.info("Successfully generated briefing")
            return briefing

        except Exception as api_error:
            error_msg = str(api_error)
            logger.error(f"OpenAI API error: {error_msg}")

            # Return a more user-friendly message based on the error type
            if "insufficient_quota" in error_msg:
                return ("Strategic briefing temporarily unavailable. "
                       "Please check back later.")
            elif "rate_limit" in error_msg:
                return ("Strategic briefing generation paused. "
                       "Please refresh in a few minutes.")
            else:
                return ("Strategic briefing system encountered an issue. "
                       "Using static analysis mode.")

    except Exception as e:
        logger.error(f"Error generating AI briefing: {str(e)}", exc_info=True)
        return ("Strategic briefing system encountered an error. "
                "Using manual event tracking.")