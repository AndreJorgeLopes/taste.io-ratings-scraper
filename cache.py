import json
import os
import time
from datetime import datetime, timedelta
from config import CACHE_FILE, CACHE_TIMEOUT_DAYS

# Global cache for episodes data
EPISODES_CACHE_FILE = "episodes_cache.json"
# Global cache for failed Simkl ID lookups
FAILED_LOOKUPS_FILE = "failed_lookups.json"

def get_cache_file(cache_key):
    """Get the cache file path based on the cache key."""
    if cache_key == 'default' or not cache_key:
        return CACHE_FILE
    elif cache_key.startswith('episodes_'):
        # All episode data is now stored in a single file
        return EPISODES_CACHE_FILE
    elif cache_key == 'failed_lookups':
        return FAILED_LOOKUPS_FILE
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

        # For episodes cache, we need to extract the specific show's episodes
        if cache_key.startswith('episodes_') and cache_file == EPISODES_CACHE_FILE:
            show_slug = cache_key.replace('episodes_', '')
            return cache_data.get('items', {}).get(show_slug, [])

        # Check if cache is expired (except for failed lookups which don't expire)
        if cache_key != 'failed_lookups':
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
        cache_file = get_cache_file(cache_key)

        # Special handling for episodes cache
        if cache_key.startswith('episodes_') and cache_file == EPISODES_CACHE_FILE:
            show_slug = cache_key.replace('episodes_', '')

            # Load existing episodes cache
            existing_data = {}
            if os.path.exists(EPISODES_CACHE_FILE):
                try:
                    with open(EPISODES_CACHE_FILE, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = {'timestamp': time.time(), 'items': {}}
            else:
                existing_data = {'timestamp': time.time(), 'items': {}}

            # Update with new data for this show
            existing_data['timestamp'] = time.time()
            existing_data['items'][show_slug] = items

            # Save updated cache
            with open(EPISODES_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
        else:
            # Standard cache saving
            cache_data = {
                'timestamp': time.time(),
                'items': items
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving {cache_key} cache: {e}")

def add_failed_lookup(title, year, category, error):
    """Add a failed Simkl ID lookup to the failed lookups cache."""
    try:
        # Load existing failed lookups
        failed_lookups = load_cache('failed_lookups') or []

        # Add new failed lookup
        failed_lookups.append({
            'title': title,
            'year': year,
            'category': category,
            'error': str(error),
            'timestamp': time.time()
        })

        # Save updated failed lookups
        save_cache(failed_lookups, 'failed_lookups')
    except Exception as e:
        print(f"Error adding failed lookup for {title}: {e}")

def get_failed_lookups():
    """Get all failed Simkl ID lookups."""
    return load_cache('failed_lookups') or []