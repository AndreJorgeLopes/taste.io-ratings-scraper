# Configuration settings for the taste.io scraper.
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# User settings
USERNAME = os.getenv("TASTE_USERNAME")  # Your taste.io username

# API settings
BASE_URL = f"https://www.taste.io/api/users/{USERNAME}/ratings"
SAVED_URL = f"https://www.taste.io/api/users/{USERNAME}/saved"
CONTINUE_WATCHING_URL = "https://www.taste.io/api/browse/continue-watching"
TV_EPISODES_URL = "https://www.taste.io/api/tv/{slug}/episodes"
API_LIMIT = 96  # Maximum number of items per request

# Taste.io authentication
TASTE_TOKEN = os.getenv("TASTE_TOKEN")  # Your taste.io authentication token

# Simkl API settings
# Get your client_id by creating a new app at https://simkl.com/settings/developer/
# Note: The URI field can be just a dot (.)
SIMKL_CLIENT_ID = os.getenv("SIMKL_CLIENT_ID")  # Your Simkl client ID
SIMKL_SEARCH_URL = "https://api.simkl.com/search"
SIMKL_IMPORT_ENDPOINT = "https://api.simkl.com/sync/ratings"
SIMKL_ADD_TO_LIST_ENDPOINT = "https://api.simkl.com/sync/add-to-list"
SIMKL_HISTORY_ENDPOINT = "https://api.simkl.com/sync/history"
SIMKL_ACCESS_TOKEN = os.getenv("SIMKL_ACCESS_TOKEN")  # Your Simkl access token gotten by following the instructions at this link: https://simkl.docs.apiary.io/#reference/authentication-oauth-2.0/

# Simkl API Headers
SIMKL_API_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SIMKL_ACCESS_TOKEN}",
    "simkl-api-key": SIMKL_CLIENT_ID
}

# Anti-bot detection settings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

# Request settings
REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "DNT": "1",
    "Host": "www.taste.io",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

# Authenticated request headers (when TASTE_TOKEN is available)
def get_auth_headers():
    """Get authenticated headers for taste.io API requests."""
    if not TASTE_TOKEN:
        return REQUEST_HEADERS

    auth_headers = REQUEST_HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {TASTE_TOKEN}"
    return auth_headers

# Cookie settings
COOKIE_DEFAULTS = {
    "sg_user_id": "null",
    "ajs_group_id": "null",
    "ajs_anonymous_id": "ab91b9bf-a89e-4aa2-8ab2-bebaf5790d23",
    "_ga": "GA1.2.705052639.1521047187"
}

# Delay settings (in seconds)
MIN_DELAY = float(os.getenv("MIN_DELAY", 1.5))
MAX_DELAY = float(os.getenv("MAX_DELAY", 4.0))

# Browser settings
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 30))

# Output settings
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "SimklBackup.json")
JSON_INDENT = 2

# Cache settings
CACHE_FILE = os.getenv("CACHE_FILE", "ratings_cache.json")
CACHE_TIMEOUT_DAYS = int(os.getenv("CACHE_TIMEOUT_DAYS", 1))

# Feature toggles (all enabled by default)
SCRAPE_RATINGS = os.getenv("SCRAPE_RATINGS", "true").lower() == "true"
SCRAPE_SAVED = os.getenv("SCRAPE_SAVED", "true").lower() == "true"
SCRAPE_CONTINUE_WATCHING = os.getenv("SCRAPE_CONTINUE_WATCHING", "true").lower() == "true"
