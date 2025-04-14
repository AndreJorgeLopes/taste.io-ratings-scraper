import json
import time
import random
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from cache import load_cache, save_cache

from config import (
    USERNAME, BASE_URL, SAVED_URL, CONTINUE_WATCHING_URL, TV_EPISODES_URL,
    API_LIMIT, USER_AGENTS, REQUEST_HEADERS, get_auth_headers,
    MIN_DELAY, MAX_DELAY, HEADLESS_MODE, PAGE_LOAD_TIMEOUT,
    OUTPUT_FILE, JSON_INDENT, COOKIE_DEFAULTS,
    SIMKL_CLIENT_ID, SIMKL_SEARCH_URL, TASTE_TOKEN
)
from schemas import SimklBackup, MediaEntry, TasteIOItem

# Configuration for Selenium Chrome Driver
chrome_options = Options()
if HEADLESS_MODE:
    chrome_options.add_argument("--headless")

# Add anti-bot detection measures
chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Add custom headers
for key, value in REQUEST_HEADERS.items():
    chrome_options.add_argument(f"--header={key}: {value}")

# Add default cookies
chrome_options.add_argument("--start-maximized")
for key, value in COOKIE_DEFAULTS.items():
    chrome_options.add_argument(f"--cookie={key}={value}")

# Initialize the WebDriver with automatic ChromeDriver management
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

def get_json_from_page(url):
    """Loads the given URL with Selenium and returns the parsed JSON from the page body."""
    driver.get(url)
    # Add random delay to mimic human behavior
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    # The page source is plain JSON text; extract the text from the <body> element
    body_text = driver.find_element("tag name", "body").text
    return json.loads(body_text)

def convert_ms_to_iso(ms: int | None) -> str | None:
    """Convert millisecond timestamp to ISO 8601 format."""
    if ms is None:
        return None
    dt = datetime.datetime.fromtimestamp(ms / 1000.0, datetime.UTC)
    return dt.isoformat()

def get_ids(title: str, year: int, category: str) -> int | None:
    """Fetch Simkl ID from their API using the title title."""
    if not SIMKL_CLIENT_ID:
        print("Warning: SIMKL_CLIENT_ID not set. Please configure it in config.py")
        return None

    try:
        params = {
            "q": f"{title} {year}",
            "page": 1,
            "limit": 1,
            "client_id": SIMKL_CLIENT_ID
        }

        params_without_year = {
            "q": title,
            "page": 1,
            "limit": 1,
            "client_id": SIMKL_CLIENT_ID
        }

        final_search_url = f"{SIMKL_SEARCH_URL}/{category}"

        response = requests.get(final_search_url, params=params)
        response.raise_for_status()
        item = response.json()[0] or requests.get(final_search_url, params=params_without_year).raise_for_status().json()[0]

        if item.get("ids", {}).get("simkl_id"):
            return {
                "simkl": item.get("ids", {}).get("simkl_id"),
                "tmdb": int(item.get("ids", {}).get("tmdb", 0))
            }

        print(f"Warning: No matching Simkl ID found for {response.json()}")
        return None

    except Exception as e:
        print(f"Error fetching Simkl ID for {title}: {e}")
        return None

def process_item(item: TasteIOItem) -> MediaEntry:
    """Process a single item from taste.io and convert it to Simkl format."""
    # Determine the rating value (convert from 4-star to 10-point scale)
    star_rating = item.get("highlightRating") or item.get("user", {}).get("rating")
    rating_value = star_rating * 2.5

    # Get the Simkl ID from their API
    if item.get("category") == "movies":
        category = "movie"
    elif 'anime' in item.get("genre") or 'Animation' in item.get("genre"):
        category = "anime"
    else:
        category = "tv"
    ids = get_ids(item.get("name", ""), item.get("year", ""), category)

    return MediaEntry(
        title=item.get("name", ""),
        rating=rating_value,
        year=item.get("year", ""),
        to='completed',
        ids=ids
    )

def fetch_items_from_api(url, cache_key):
    """Fetch all items from the given API URL with pagination."""
    # Try to load cached items
    cached_items = load_cache(cache_key)
    if cached_items:
        print(f"Using cached {cache_key} items...")
        return cached_items

    print(f"Cache not found or expired for {cache_key}, fetching from API...")
    all_items = []

    # Retrieve the first page to get total items
    first_page_url = f"{url}?limit={API_LIMIT}&offset=0"
    if cache_key == 'saved':
        first_page_url += "&maxReleaseDate=1744443802477&sort=trending"

    print("Requesting URL:", first_page_url)
    data = get_json_from_page(first_page_url)

    total_items = data.get("total", 0)
    print(f"Total {cache_key} items found:", total_items)

    # Process first page items and save to cache immediately
    all_items.extend(data.get("items", []))
    save_cache(all_items, cache_key)

    # Fetch remaining pages
    offset = API_LIMIT
    while offset < total_items:
        page_url = f"{url}?limit={API_LIMIT}&offset={offset}"
        if cache_key == 'saved':
            page_url += "&maxReleaseDate=1744443802477&sort=trending"

        print("Requesting URL:", page_url)
        page_data = get_json_from_page(page_url)
        new_items = page_data.get("items", [])
        all_items.extend(new_items)
        # Update cache after each page
        save_cache(all_items, cache_key)
        offset += API_LIMIT

    print(f"Total {cache_key} items collected:", len(all_items))
    return all_items

def process_saved_item(item: TasteIOItem) -> MediaEntry:
    """Process a single saved item from taste.io and convert it to Simkl format with 'plantowatch' status."""
    # Get the Simkl ID from their API
    if item.get("category") == "movies":
        category = "movie"
    elif 'anime' in item.get("genre", "") or 'Animation' in item.get("genre", ""):
        category = "anime"
    else:
        category = "tv"
    ids = get_ids(item.get("name", ""), item.get("year", ""), category)

    # Skip items where we couldn't find a Simkl ID
    if not ids:
        return None

    return MediaEntry(
        title=item.get("name", ""),
        rating=None,  # No rating for saved items
        year=item.get("year", ""),
        to='plantowatch',  # Set status to plantowatch
        ids=ids
    )

def fetch_continue_watching_items():
    """Fetch items from the continue-watching API endpoint."""
    if not TASTE_TOKEN:
        print("Warning: TASTE_TOKEN not set. Cannot fetch continue-watching items.")
        return []

    # Try to load cached items
    cached_items = load_cache('watching')
    if cached_items:
        print("Using cached continue-watching items...")
        return cached_items

    print("Cache not found or expired for continue-watching, fetching from API...")
    all_items = []

    # Retrieve the first page
    first_page_url = f"{CONTINUE_WATCHING_URL}?limit={API_LIMIT}&offset=0"
    print("Requesting URL:", first_page_url)

    # Use authenticated headers
    headers = get_auth_headers()
    response = requests.get(first_page_url, headers=headers)
    response.raise_for_status()
    data = response.json()

    total_items = data.get("total", 0)
    print(f"Total continue-watching items found: {total_items}")

    # Process first page items and save to cache immediately
    all_items.extend(data.get("items", []))
    save_cache(all_items, 'watching')

    # Fetch remaining pages
    offset = API_LIMIT
    while offset < total_items:
        page_url = f"{CONTINUE_WATCHING_URL}?limit={API_LIMIT}&offset={offset}"
        print("Requesting URL:", page_url)
        page_response = requests.get(page_url, headers=headers)
        page_response.raise_for_status()
        page_data = page_response.json()
        new_items = page_data.get("items", [])
        all_items.extend(new_items)
        # Update cache after each page
        save_cache(all_items, 'watching')
        offset += API_LIMIT

    print(f"Total continue-watching items collected: {len(all_items)}")
    return all_items

def fetch_watched_episodes(slug):
    """Fetch watched episodes for a TV show."""
    if not TASTE_TOKEN:
        print("Warning: TASTE_TOKEN not set. Cannot fetch episode data.")
        return []

    # Try to load cached items
    cache_key = f"episodes_{slug}"
    cached_items = load_cache(cache_key)
    if cached_items:
        print(f"Using cached episode data for {slug}...")
        return cached_items

    print(f"Fetching episode data for {slug}...")

    # Use authenticated headers
    headers = get_auth_headers()
    url = TV_EPISODES_URL.format(slug=slug)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extract watched episodes (where user.tracked is true)
        watched_episodes = []
        for item in data.get("items", []):
            # Skip episodes in season 0 (specials) as they're buggy
            if item.get("season") == 0:
                continue

            if item.get("user", {}).get("tracked", False):
                watched_episodes.append({
                    "season": item.get("season"),
                    "episode": item.get("episode")
                })

        # Save to cache
        save_cache(watched_episodes, cache_key)
        return watched_episodes

    except Exception as e:
        print(f"Error fetching episode data for {slug}: {e}")
        return []

def process_watching_item(item: TasteIOItem) -> MediaEntry:
    """Process a single item from continue-watching and convert it to Simkl format."""
    # Get the Simkl ID from their API
    if item.get("category") == "movies":
        category = "movie"
    elif 'anime' in item.get("genre", "") or 'Animation' in item.get("genre", ""):
        category = "anime"
    else:
        category = "tv"
    ids = get_ids(item.get("name", ""), item.get("year", ""), category)

    # Skip items where we couldn't find a Simkl ID
    if not ids:
        return None

    return MediaEntry(
        title=item.get("name", ""),
        rating=None,  # No rating for watching items
        year=item.get("year", ""),
        to='watching',  # Set status to watching
        ids=ids
    )

def main():
    # Initialize the backup structure
    backup = SimklBackup(movies=[], shows=[])
    # Dictionary to store watched episodes data for the importer
    watched_episodes = {}

    try:
        # Fetch rated items
        ratings_items = fetch_items_from_api(BASE_URL, 'ratings')

        # Process rated items
        ratings_cache = set()  # Keep track of rated items to filter out duplicates
        for item in ratings_items:
            entry = process_item(item)
            # Add to ratings cache for filtering saved items later
            if entry and entry.get("ids") and entry.get("ids").get("simkl"):
                ratings_cache.add(entry.get("ids").get("simkl"))

            if item.get("category") == "tv":
                backup["shows"].append(entry)
            else:  # Default to movies for unknown categories
                backup["movies"].append(entry)

        # Fetch saved items
        saved_items = fetch_items_from_api(SAVED_URL, 'saved')

        # Process saved items (filter out duplicates)
        for item in saved_items:
            # Skip items that are already rated
            item_key = f"{item.get('name')}_{item.get('year')}"
            if item_key in ratings_cache:
                continue

            # Process the saved item
            entry = process_saved_item(item)
            if entry:
                if item.get("category") == "movies":
                    backup["movies"].append(entry)
                else:
                    backup["shows"].append(entry)

        # Fetch continue-watching items if TASTE_TOKEN is available
        if TASTE_TOKEN:
            watching_items = fetch_continue_watching_items()

            # Process continue-watching items (filter out duplicates)
            for item in watching_items:
                # Skip items that are already rated or saved
                item_key = f"{item.get('name')}_{item.get('year')}"
                if item_key in ratings_cache:
                    continue

                # Process the watching item
                entry = process_watching_item(item)
                if entry:
                    if item.get("category") == "movies":
                        backup["movies"].append(entry)
                    else:
                        # For TV shows, fetch watched episodes
                        slug = item.get("slug")
                        if slug:
                            show_episodes = fetch_watched_episodes(slug)
                            if show_episodes:
                                # Group episodes by season
                                seasons = {}
                                for ep in show_episodes:
                                    season_num = ep["season"]
                                    if season_num not in seasons:
                                        seasons[season_num] = []
                                    seasons[season_num].append({"number": ep["episode"]})

                                # Store watched episodes for this show
                                watched_episodes[item_key] = {
                                    "title": item.get("name", ""),
                                    "year": item.get("year", ""),
                                    "ids": entry.get("ids", {}),
                                    "seasons": [
                                        {"number": season, "episodes": episodes}
                                        for season, episodes in seasons.items()
                                    ]
                                }

                        backup["shows"].append(entry)

        # Save the backup to a file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(backup, f, ensure_ascii=False, indent=JSON_INDENT)

        # Save watched episodes to a separate file for the importer
        if watched_episodes:
            with open("watched_episodes.json", 'w', encoding='utf-8') as f:
                json.dump(list(watched_episodes.values()), f, ensure_ascii=False, indent=JSON_INDENT)

        print(f"Backup saved to {OUTPUT_FILE}")
        print(f"Total movies: {len(backup['movies'])}")
        print(f"Total shows: {len(backup['shows'])}")
        if watched_episodes:
            print(f"Watched episodes data saved to watched_episodes.json")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    main()