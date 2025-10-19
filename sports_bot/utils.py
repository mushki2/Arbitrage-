import json
import os
from datetime import datetime, timedelta

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'cache.json')
CACHE_DURATION_HOURS = 24  # Cache data for 24 hours

def cache_data(key, data):
    """Saves data to the cache file with a timestamp."""
    try:
        with open(CACHE_FILE, 'r+') as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError:
                cache = {}

            cache[key] = {
                'timestamp': datetime.utcnow().isoformat(),
                'data': data
            }
            f.seek(0)
            json.dump(cache, f, indent=4)
    except FileNotFoundError:
        with open(CACHE_FILE, 'w') as f:
            cache = {
                key: {
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': data
                }
            }
            json.dump(cache, f, indent=4)

def load_cached_data(key):
    """Loads data from the cache if it's not expired."""
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
            if key in cache:
                timestamp_str = cache[key]['timestamp']
                timestamp = datetime.fromisoformat(timestamp_str)
                if datetime.utcnow() - timestamp < timedelta(hours=CACHE_DURATION_HOURS):
                    return cache[key]['data']
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return None
