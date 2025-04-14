import json
import os
import time
from datetime import datetime, timedelta
from config import CACHE_FILE, CACHE_TIMEOUT_DAYS

def get_cache_file(cache_key):
    """Get the cache file path based on the cache key."""
    if cache_key == 'default' or not cache_key:
        return CACHE_FILE
    else:
        # Add the cache key to the filename before the extension
        base, ext = os.path.splitext(CACHE_FILE)
        return f"{base}_{cache_key}{ext}"

def load_cache(cache_key='ratings'):
    """Load cached items if they exist and are not expired."""
    cache_file = get_cache_file(cache_key)
    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Check if cache is expired
        cache_timestamp = cache_data.get('timestamp', 0)
        current_time = time.time()
        if current_time - cache_timestamp > (CACHE_TIMEOUT_DAYS * 24 * 60 * 60):
            return None

        return cache_data.get('items', [])
    except Exception as e:
        print(f"Error loading {cache_key} cache: {e}")
        return None

def save_cache(items, cache_key='ratings'):
    """Save items to cache with current timestamp."""
    try:
        cache_data = {
            'timestamp': time.time(),
            'items': items
        }
        cache_file = get_cache_file(cache_key)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving {cache_key} cache: {e}")