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
    USERNAME, BASE_URL, USER_AGENTS, REQUEST_HEADERS,
    MIN_DELAY, MAX_DELAY, HEADLESS_MODE, PAGE_LOAD_TIMEOUT,
    OUTPUT_FILE, JSON_INDENT, COOKIE_DEFAULTS,
    SIMKL_CLIENT_ID, SIMKL_SEARCH_URL
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

def get_simkl_id(slug: str, category: str) -> int | None:
    """Fetch Simkl ID from their API using the title slug."""
    if not SIMKL_CLIENT_ID:
        print("Warning: SIMKL_CLIENT_ID not set. Please configure it in config.py")
        return None

    try:
        params = {
            "title": slug,
            "client_id": SIMKL_CLIENT_ID
        }
        response = requests.get(SIMKL_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Find the matching item with the correct type
        for item in data:
            if item.get("type") == category and item.get("ids", {}).get("simkl"):
                return item["ids"]["simkl"]

        print(f"Warning: No matching Simkl ID found for {slug}")
        return None

    except Exception as e:
        print(f"Error fetching Simkl ID for {slug}: {e}")
        return None

def process_item(item: TasteIOItem) -> MediaEntry:
    """Process a single item from taste.io and convert it to Simkl format."""
    # Determine the rating value (convert from 5-star to 10-point scale)
    star_rating = item.get("highlightRating")
    if star_rating is not None:
        rating_value = star_rating * 2
    else:
        user_rating = item.get("user", {}).get("rating")
        rating_value = user_rating * 2 if user_rating is not None else None

    # Convert timestamp if available
    rated_at = convert_ms_to_iso(item["lastReaction"]) if "lastReaction" in item else None

    # Get the Simkl ID from their API
    category = "tv" if item.get("category") == "tv" else "movie"
    simkl_id = get_simkl_id(item.get("slug", ""), category)

    return MediaEntry(
        title=item.get("name", ""),
        rating=rating_value,
        rated_at=rated_at,
        year=item.get("year", ""),
        ids={"simkl": simkl_id or 0}  # Fallback to 0 if no ID found
    )

def main():
    # Initialize the backup structure
    backup = SimklBackup(movies=[], shows=[])

    try:
        # Try to load cached items
        cached_items = load_cache()
        if cached_items:
            print("Using cached items...")
            all_items = cached_items
        else:
            print("Cache not found or expired, fetching from API...")
            all_items = []
            # Retrieve the first page to get total items
            first_page_url = f"{BASE_URL}?offset=0"
            print("Requesting URL:", first_page_url)
            data = get_json_from_page(first_page_url)

            total_items = data.get("total", 0)
            print("Total items found:", total_items)

            # Process first page items and save to cache immediately
            all_items.extend(data.get("items", []))
            save_cache(all_items)

            # Fetch remaining pages
            offset = 24
            while offset < total_items:
                page_url = f"{BASE_URL}?offset={offset}"
                print("Requesting URL:", page_url)
                page_data = get_json_from_page(page_url)
                new_items = page_data.get("items", [])
                all_items.extend(new_items)
                # Update cache after each page
                save_cache(all_items)
                offset += 24

        print("Total items collected:", len(all_items))

        # Process all items
        for item in all_items:
            entry = process_item(item)
            if item.get("category") == "tv":
                backup["shows"].append(entry)
            else:  # Default to movies for unknown categories
                backup["movies"].append(entry)

        # Save the final file in JSON format
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=JSON_INDENT)
        print(f"Backup file '{OUTPUT_FILE}' has been created.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()