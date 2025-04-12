import json
import sys
import requests
from typing import Dict, List, Any
from collections import defaultdict

from config import (
    OUTPUT_FILE, SIMKL_CLIENT_ID,
    SIMKL_IMPORT_ENDPOINT, SIMKL_ACCESS_TOKEN,
    SIMKL_API_HEADERS, SIMKL_ADD_TO_LIST_ENDPOINT
)
from schemas import SimklBackup, MediaEntry

def load_backup(file_path: str) -> SimklBackup:
    """Load the backup file created by the scraper."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading backup file: {e}")
        sys.exit(1)

def is_sorted_by_rating(items: List[MediaEntry]) -> bool:
    """Check if the items are sorted by rating in descending order."""
    if not items:
        return True

    for i in range(1, len(items)):
        # Handle None ratings (they should be at the end)
        prev_rating = items[i-1].get('rating') or 0
        curr_rating = items[i].get('rating') or 0

        if prev_rating < curr_rating:
            return False
    return True

def sort_by_rating(backup: SimklBackup) -> SimklBackup:
    """Sort movies and shows by rating in descending order."""
    sorted_backup = SimklBackup(
        movies=sorted(backup['movies'], key=lambda x: x.get('rating') or 0, reverse=True),
        shows=sorted(backup['shows'], key=lambda x: x.get('rating') or 0, reverse=True)
    )
    return sorted_backup

def group_by_rating(backup: SimklBackup) -> Dict[float, List[Dict[str, Any]]]:
    """Group movies and shows by their rating value."""
    rating_groups = defaultdict(list)

    # Process movies
    for movie in backup['movies']:
        rating = movie.get('rating')
        if rating is not None:
            # Round to nearest integer for API grouping
            rounded_rating = round(rating)
            rating_groups[rounded_rating].append({
                'title': movie['title'],
                'ids': movie['ids'],
                'type': 'movie'
            })

    # Process shows
    for show in backup['shows']:
        rating = show.get('rating')
        if rating is not None:
            # Round to nearest integer for API grouping
            rounded_rating = round(rating)
            rating_groups[rounded_rating].append({
                'title': show['title'],
                'ids': show['ids'],
                'type': 'show'
            })

    return rating_groups

def send_ratings_to_simkl(rating_groups: Dict[float, List[Dict[str, Any]]]) -> None:
    """Send ratings to Simkl API, one request per rating value.
    Also sends each group to the add-to-list endpoint."""
    if not SIMKL_CLIENT_ID or not SIMKL_ACCESS_TOKEN:
        print("Error: SIMKL_CLIENT_ID or SIMKL_ACCESS_TOKEN not set. Please configure them in config.py")
        sys.exit(1)

    headers = SIMKL_API_HEADERS.copy()

    # Process each rating group
    for rating, items in rating_groups.items():
        if not items:
            continue

        print(f"Sending {len(items)} items with rating {rating}...")

        # 1. Send to ratings endpoint with rating parameter
        ratings_endpoint = f"{SIMKL_IMPORT_ENDPOINT}?rating={rating}"
        try:
            response = requests.post(
                ratings_endpoint,
                headers=headers,
                json=items
            )
            response.raise_for_status()
            print(f"Successfully sent {len(items)} items with rating {rating} to ratings endpoint")
            print(f"Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending items with rating {rating} to ratings endpoint: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")

        # 2. Send to add-to-list endpoint without query parameters
        try:
            print(f"Adding {len(items)} items to the completed list...")
            add_response = requests.post(
                SIMKL_ADD_TO_LIST_ENDPOINT,
                headers=headers,
                json=items
            )
            add_response.raise_for_status()
            print(f"Successfully added {len(items)} items to the completed list")
            print(f"Response: {add_response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error adding items to the completed list: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")

def main():
    # Load the backup file
    backup_file = OUTPUT_FILE
    print(f"Loading backup from {backup_file}...")
    backup = load_backup(backup_file)

    # Check if ratings are sorted
    movies_sorted = is_sorted_by_rating(backup['movies'])
    shows_sorted = is_sorted_by_rating(backup['shows'])

    if not movies_sorted or not shows_sorted:
        print("Ratings are not sorted. Sorting now...")
        backup = sort_by_rating(backup)
        print("Ratings sorted successfully.")
    else:
        print("Ratings are already sorted.")

    # Group items by rating
    print("Grouping items by rating...")
    rating_groups = group_by_rating(backup)

    # Print summary of ratings
    for rating, items in sorted(rating_groups.items(), reverse=True):
        print(f"Rating {rating}: {len(items)} items")

    # Send ratings to Simkl
    print("\nSending ratings to Simkl...")
    send_ratings_to_simkl(rating_groups)

    print("\nImport process completed.")

if __name__ == "__main__":
    main()