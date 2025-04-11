import json
import time
import random
import datetime
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    USERNAME, BASE_URL, USER_AGENTS, REQUEST_HEADERS,
    MIN_DELAY, MAX_DELAY, HEADLESS_MODE, PAGE_LOAD_TIMEOUT,
    OUTPUT_FILE, JSON_INDENT, CSV_ENABLED, CSV_FIELDS,
    COOKIE_DEFAULTS
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

def convert_ms_to_iso(ms: int) -> str:
    """Convert millisecond timestamp to ISO 8601 format."""
    dt = datetime.datetime.utcfromtimestamp(ms / 1000.0)
    return dt.isoformat() + "Z"

def process_item(item: TasteIOItem) -> MediaEntry:
    """Process a single item from taste.io and convert it to Simkl format."""
    # Determine the rating value (convert from 5-star to 10-point scale)
    star_rating = item.get("starRating")
    if star_rating is not None:
        rating_value = star_rating * 2
    else:
        user_rating = item.get("user", {}).get("rating")
        rating_value = user_rating * 2 if user_rating is not None else None

    # Convert timestamp if available
    rated_at = convert_ms_to_iso(item["lastReaction"]) if "lastReaction" in item else None

    # Generate a placeholder Simkl id
    simkl_id = abs(hash(item.get("slug", ""))) % 1000000

    return MediaEntry(
        title=item.get("name", ""),
        rating=rating_value,
        rated_at=rated_at,
        year=item.get("year", ""),
        ids={"simkl": simkl_id}
    )

def save_as_csv(backup: SimklBackup, filename: str):
    """Save the backup data as CSV file."""
    csv_filename = filename.replace(".json", ".csv")
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        
        # Write movies
        for movie in backup["movies"]:
            writer.writerow({
                field: getattr(movie, field) for field in CSV_FIELDS
            })
        
        # Write shows
        for show in backup["shows"]:
            writer.writerow({
                field: getattr(show, field) for field in CSV_FIELDS
            })

def main():
    # Initialize the backup structure
    backup = SimklBackup(movies=[], shows=[])

    try:
        # Retrieve the first page to get total items
        first_page_url = f"{BASE_URL}?offset=0"
        print("Requesting URL:", first_page_url)
        data = get_json_from_page(first_page_url)

        total_items = data.get("total", 0)
        print("Total items found:", total_items)

        # Process first page items
        all_items = data.get("items", [])

        # Fetch remaining pages
        offset = 24
        while offset < total_items:
            page_url = f"{BASE_URL}?offset={offset}"
            print("Requesting URL:", page_url)
            page_data = get_json_from_page(page_url)
            all_items.extend(page_data.get("items", []))
            offset += 24

        print("Total items collected:", len(all_items))

        # Process all items
        for item in all_items:
            entry = process_item(item)
            if item.get("category") == "tv":
                backup["shows"].append(entry)
            else:  # Default to movies for unknown categories
                backup["movies"].append(entry)

        # Save the backup file in JSON format
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=JSON_INDENT)
        print(f"Backup file '{OUTPUT_FILE}' has been created.")

        # Save as CSV if enabled
        if CSV_ENABLED:
            save_as_csv(backup, OUTPUT_FILE)
            print(f"CSV backup file has been created.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()