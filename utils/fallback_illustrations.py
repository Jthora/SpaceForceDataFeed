import hashlib
from typing import Dict, Tuple
import base64
import os

def get_category_pattern(category: str) -> Dict[str, str]:
    """Generate pattern parameters based on category"""
    # Use category to generate consistent colors and patterns
    category_hash = hashlib.md5(category.encode()).hexdigest()

    # Generate colors from hash
    primary_color = f"#{category_hash[:6]}"
    secondary_color = f"#{category_hash[6:12]}"

    patterns = {
        'Military Space': {
            'pattern': 'circuit',
            'color1': '#00f2ff',
            'color2': '#0066cc'
        },
        'Space Industry': {
            'pattern': 'constellation',
            'color1': '#00ffcc',
            'color2': '#0099ff'
        },
        'Space Science': {
            'pattern': 'atoms',
            'color1': '#66ffcc',
            'color2': '#3366ff'
        },
        'Official Updates': {
            'pattern': 'shield',
            'color1': '#00ccff',
            'color2': '#3333cc'
        },
        'Defense Updates': {
            'pattern': 'radar',
            'color1': '#33ccff',
            'color2': '#0000cc'
        },
        'Space Technology': {
            'pattern': 'chip',
            'color1': '#00ffff',
            'color2': '#0033cc'
        }
    }

    return patterns.get(category, {
        'pattern': 'default',
        'color1': primary_color,
        'color2': secondary_color
    })

def generate_fallback_svg(category: str, width: int = 120, height: int = 90) -> str:
    """Generate SVG fallback illustration based on category"""
    pattern_info = get_category_pattern(category)
    pattern = pattern_info['pattern']
    color1 = pattern_info['color1']
    color2 = pattern_info['color2']

    # Base SVG with cyberpunk-style background
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color1};stop-opacity:0.2"/>
            <stop offset="100%" style="stop-color:{color2};stop-opacity:0.1"/>
        </linearGradient>

        <!-- Glowing effect -->
        <filter id="glow">
            <feGaussianBlur stdDeviation="1" result="glow"/>
            <feMerge>
                <feMergeNode in="glow"/>
                <feMergeNode in="glow"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>

    <!-- Background -->
    <rect width="100%" height="100%" fill="url(#bg)"/>
    '''

    # Add pattern based on category
    if pattern == 'circuit':
        svg += f'''
        <path d="M10 10 H110 M10 45 H110 M10 80 H110" 
              stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        <circle cx="30" cy="10" r="2" fill="{color1}" filter="url(#glow)"/>
        <circle cx="80" cy="45" r="2" fill="{color1}" filter="url(#glow)"/>
        <circle cx="60" cy="80" r="2" fill="{color1}" filter="url(#glow)"/>
        '''
    elif pattern == 'constellation':
        svg += f'''
        <circle cx="30" cy="20" r="1" fill="{color1}" filter="url(#glow)"/>
        <circle cx="80" cy="40" r="1" fill="{color1}" filter="url(#glow)"/>
        <circle cx="50" cy="70" r="1" fill="{color1}" filter="url(#glow)"/>
        <path d="M30 20 L80 40 L50 70" 
              stroke="{color1}" stroke-width="0.3" fill="none" filter="url(#glow)"/>
        '''
    elif pattern == 'atoms':
        svg += f'''
        <circle cx="60" cy="45" r="15" 
                stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        <ellipse cx="60" cy="45" rx="25" ry="10" 
                 stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        '''
    elif pattern == 'shield':
        svg += f'''
        <path d="M60 10 L90 30 L80 70 L60 80 L40 70 L30 30 Z" 
              stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        '''
    elif pattern == 'radar':
        svg += f'''
        <circle cx="60" cy="45" r="30" 
                stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        <path d="M60 45 L90 45 A30 30 0 0 0 60 15" 
              stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        '''
    elif pattern == 'chip':
        svg += f'''
        <rect x="30" y="20" width="60" height="50" 
              stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        <line x1="30" y1="35" x2="90" y2="35" 
              stroke="{color1}" stroke-width="0.5" filter="url(#glow)"/>
        <line x1="30" y1="55" x2="90" y2="55" 
              stroke="{color1}" stroke-width="0.5" filter="url(#glow)"/>
        '''
    else:
        # Default pattern
        svg += f'''
        <path d="M10 10 L110 80 M110 10 L10 80" 
              stroke="{color1}" stroke-width="0.5" fill="none" filter="url(#glow)"/>
        '''

    svg += '</svg>'
    return svg

def get_default_image_url() -> str:
    """Get the default featured image as a data URL"""
    try:
        with open('assets/default_featured_image.png', 'rb') as f:
            image_data = f.read()
            return f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
    except Exception:
        return None

def get_fallback_image_url(category: str) -> str:
    """Generate data URL for fallback image"""
    try:
        # First try category-specific SVG
        svg = generate_fallback_svg(category)
        return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"
    except Exception:
        # If SVG generation fails, use default featured image
        default_image = get_default_image_url()
        if default_image:
            return default_image
        # If all fails, return None to let the UI handle it
        return None