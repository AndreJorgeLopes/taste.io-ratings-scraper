import json
import os
import time
from datetime import datetime, timedelta

CACHE_FILE = "ratings_cache.json"
CACHE_TIMEOUT_DAYS = 1

def load_cache():
    """Load cached items if they exist and are not expired."""
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Check if cache is expired
        cache_timestamp = cache_data.get('timestamp', 0)
        current_time = time.time()
        if current_time - cache_timestamp > (CACHE_TIMEOUT_DAYS * 24 * 60 * 60):
            return None

        return cache_data.get('items', [])
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None

def save_cache(items):
    """Save items to cache with current timestamp."""
    try:
        cache_data = {
            'timestamp': time.time(),
            'items': items
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")