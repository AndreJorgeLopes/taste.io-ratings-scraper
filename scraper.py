import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Configuration for Selenium Chrome Driver (headless mode in this example)
chrome_options = Options()
chrome_options.add_argument("--headless")  # run in headless mode if you do not need a visible browser

# Initialize the WebDriver (make sure chromedriver is installed and in your PATH)
driver = webdriver.Chrome(options=chrome_options)

# The base URL for the ratings API (using the taste.io API endpoint)
base_url = "https://www.taste.io/api/users/ciganoo/ratings"

def get_json_from_page(url):
    """Loads the given URL with Selenium and returns the parsed JSON from the page body."""
    driver.get(url)
    # wait a moment for the data to load; adjust sleep time if necessary
    time.sleep(1)
    # The page source is plain JSON text; extract the text from the <body> element
    body_text = driver.find_element("tag name", "body").text
    return json.loads(body_text)

# Retrieve the first page (offset=0) to get the total number of items.
first_page_url = f"{base_url}?offset=0"
print("Requesting URL:", first_page_url)
data = get_json_from_page(first_page_url)

# The total number of items is given in the "total" field.
total_items = data.get("total", 0)
print("Total items found:", total_items)

# Initialize a list to hold all rating items
all_items = data.get("items", [])

# Assuming each page has 24 items, calculate the required number of pages/offsets.
offset = 24
while offset < total_items:
    page_url = f"{base_url}?offset={offset}"
    print("Requesting URL:", page_url)
    page_data = get_json_from_page(page_url)
    items = page_data.get("items", [])
    all_items.extend(items)
    offset += 24

print("Total items collected:", len(all_items))

# Create the backup structure to be written in the Simkl format.
backup = {
    "movies": [],
    "shows": []
}

# Helper function to convert millisecond timestamp to ISO 8601 format.
def convert_ms_to_iso(ms):
    # Convert milliseconds to seconds
    dt = datetime.datetime.utcfromtimestamp(ms / 1000.0)
    return dt.isoformat() + "Z"

# Process each item and add it to either the movies or shows list.
for item in all_items:
    # Determine the rating value.
    # We assume the "starRating" (out of 5) needs to be multiplied by 2 to convert to a 10-point scale.
    star_rating = item.get("starRating")
    if star_rating is not None:
        rating_value = star_rating * 2
    else:
        # Fallback: try using the "user" rating if available.
        user_rating = item.get("user", {}).get("rating")
        rating_value = user_rating * 2 if user_rating is not None else None

    # Convert the "lastReaction" timestamp if available (assumed to be in milliseconds).
    rated_at = None
    if "lastReaction" in item:
        rated_at = convert_ms_to_iso(item["lastReaction"])

    # Generate a placeholder Simkl id using a hash of the "slug" value.
    slug = item.get("slug", "")
    simkl_id = abs(hash(slug)) % 1000000  # produces a pseudo-unique integer value

    # Create an entry in Simkl format.
    entry = {
        "title": item.get("name", ""),
        "rating": rating_value,
        "rated_at": rated_at,
        "year": item.get("year", ""),
        "ids": {
            "simkl": simkl_id
        }
    }

    # Put the entry into the correct category list based on the item category.
    if item.get("category") == "tv":
        backup["shows"].append(entry)
    elif item.get("category") == "movie":
        backup["movies"].append(entry)
    else:
        # If the category is unrecognized, you could choose to log or place it in one category.
        backup["movies"].append(entry)

# Write the backup data to the file "SimklBackup.json"
with open("SimklBackup.json", "w", encoding="utf-8") as f:
    json.dump(backup, f, ensure_ascii=False, indent=2)

print("Backup file 'SimklBackup.json' has been created.")

# Close the Selenium WebDriver
driver.quit()