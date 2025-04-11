\"""Configuration settings for the taste.io scraper."""

# User settings
USERNAME = "ciganoo"  # Your taste.io username

# API settings
BASE_URL = f"https://www.taste.io/api/users/{USERNAME}/ratings"

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

# Cookie settings
COOKIE_DEFAULTS = {
    "sg_user_id": "null",
    "ajs_group_id": "null",
    "ajs_anonymous_id": "ab91b9bf-a89e-4aa2-8ab2-bebaf5790d23",
    "_ga": "GA1.2.705052639.1521047187"
}

# Delay settings (in seconds)
MIN_DELAY = 1.5
MAX_DELAY = 4.0

# Browser settings
HEADLESS_MODE = True
PAGE_LOAD_TIMEOUT = 30

# Output settings
OUTPUT_FILE = "SimklBackup.json"
JSON_INDENT = 2
CSV_ENABLED = True  # Enable CSV output alongside JSON
CSV_FIELDS = ["title", "rating", "rated_at", "year"]  # Fields to include in CSV output