import json
import sys
import os
import requests
from typing import Dict, List, Any
from collections import defaultdict

from config import (
    OUTPUT_FILE, SIMKL_CLIENT_ID,
    SIMKL_IMPORT_ENDPOINT, SIMKL_ACCESS_TOKEN,
    SIMKL_API_HEADERS, SIMKL_ADD_TO_LIST_ENDPOINT,
    SIMKL_HISTORY_ENDPOINT
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

def group_by_rating(backup: SimklBackup) -> Dict[float, Dict[str, List[Dict[str, Any]]]]:
    """Group movies and shows by their rating value, separating them into 'movies' and 'shows' categories."""
    rating_groups = defaultdict(lambda: {'movies': [], 'shows': []})

    # Process movies
    for movie in backup['movies']:
        rating = movie.get('rating')
        if rating is not None:
            # Round to nearest integer for API grouping
            rounded_rating = round(rating)
            rating_groups[rounded_rating]['movies'].append(movie)

    # Process shows
    for show in backup['shows']:
        rating = show.get('rating')
        if rating is not None:
            # Round to nearest integer for API grouping
            rounded_rating = round(rating)
            rating_groups[rounded_rating]['shows'].append(show)

    return rating_groups

def send_ratings_to_simkl(rating_groups: Dict[float, Dict[str, List[Dict[str, Any]]]]) -> None:
    """Send ratings to Simkl API, one request per rating value.
    Also sends each group to the add-to-list endpoint."""
    if not SIMKL_CLIENT_ID or not SIMKL_ACCESS_TOKEN:
        print("Error: SIMKL_CLIENT_ID or SIMKL_ACCESS_TOKEN not set. Please configure them in config.py")
        sys.exit(1)

    headers = SIMKL_API_HEADERS.copy()

    # Process each rating group
    for rating, formatted_items in rating_groups.items():
        if not formatted_items['movies'] and not formatted_items['shows']:
            continue

        total_items = len(formatted_items['movies']) + len(formatted_items['shows'])
        print(f"Sending {total_items} items with rating {rating}...")

        # 1. Send to ratings endpoint with rating parameter
        ratings_endpoint = f"{SIMKL_IMPORT_ENDPOINT}?rating={rating}"
        try:
            response = requests.post(
                ratings_endpoint,
                headers=headers,
                json=formatted_items
            )
            response.raise_for_status()
            print(f"Successfully sent {total_items} items with rating {rating} to ratings endpoint")
        except requests.exceptions.RequestException as e:
            print(f"Error sending items with rating {rating} to ratings endpoint: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")

        # 2. Send to add-to-list endpoint with proper format (movies and shows already separated)
        try:
            print(f"Adding {total_items} items to the completed list...")
            add_response = requests.post(
                SIMKL_ADD_TO_LIST_ENDPOINT,
                headers=headers,
                json=formatted_items
            )
            add_response.raise_for_status()
            print(f"Successfully added {total_items} items to the completed list")
            print(f"Movies: {len(formatted_items['movies'])}, Shows: {len(formatted_items['shows'])}")
        except requests.exceptions.RequestException as e:
            print(f"Error adding items to the completed list: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")

def extract_plantowatch_items(backup: SimklBackup) -> Dict[str, List[Dict[str, Any]]]:
    """Extract items with 'plantowatch' status from the backup.
    Returns a dictionary with 'movies' and 'shows' keys."""
    plantowatch_items = {
        'movies': [],
        'shows': []
    }

    # Process movies
    for movie in backup['movies']:
        if movie.get('to') == 'plantowatch':
            plantowatch_items['movies'].append(movie)

    # Process shows
    for show in backup['shows']:
        if show.get('to') == 'plantowatch':
            plantowatch_items['shows'].append(show)

    return plantowatch_items

def send_plantowatch_to_simkl(plantowatch_items: Dict[str, List[Dict[str, Any]]]) -> None:
    """Send plantowatch items to Simkl API using the add-to-list endpoint.
    Expects a dictionary with 'movies' and 'shows' keys."""
    if not SIMKL_CLIENT_ID or not SIMKL_ACCESS_TOKEN:
        print("Error: SIMKL_CLIENT_ID or SIMKL_ACCESS_TOKEN not set. Please configure them in config.py")
        sys.exit(1)

    total_items = len(plantowatch_items['movies']) + len(plantowatch_items['shows'])
    if total_items == 0:
        print("No plantowatch items to send.")
        return

    headers = SIMKL_API_HEADERS.copy()

    print(f"Sending {total_items} items to the plantowatch list...")
    try:
        response = requests.post(
            SIMKL_ADD_TO_LIST_ENDPOINT,
            headers=headers,
            json=plantowatch_items
        )
        response.raise_for_status()
        print(f"Successfully added {total_items} items to the plantowatch list")
        print(f"Movies: {len(plantowatch_items['movies'])}, Shows: {len(plantowatch_items['shows'])}")
    except requests.exceptions.RequestException as e:
        print(f"Error adding items to the plantowatch list: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")

def extract_watching_items(backup: SimklBackup) -> Dict[str, List[Dict[str, Any]]]:
    """Extract items with 'watching' status from the backup.
    Returns a dictionary with 'movies' and 'shows' keys."""
    watching_items = {
        'movies': [],
        'shows': []
    }

    # Process movies
    for movie in backup['movies']:
        if movie.get('to') == 'watching':
            watching_items['movies'].append(movie)

    # Process shows
    for show in backup['shows']:
        if show.get('to') == 'watching':
            watching_items['shows'].append(show)

    return watching_items

def send_watching_to_simkl(watching_items: Dict[str, List[Dict[str, Any]]]) -> None:
    """Send watching items to Simkl API using the add-to-list endpoint.
    Expects a dictionary with 'movies' and 'shows' keys."""
    if not SIMKL_CLIENT_ID or not SIMKL_ACCESS_TOKEN:
        print("Error: SIMKL_CLIENT_ID or SIMKL_ACCESS_TOKEN not set. Please configure them in config.py")
        sys.exit(1)

    total_items = len(watching_items['movies']) + len(watching_items['shows'])
    if total_items == 0:
        print("No watching items to send.")
        return

    headers = SIMKL_API_HEADERS.copy()

    print(f"Sending {total_items} items to the watching list...")
    try:
        response = requests.post(
            SIMKL_ADD_TO_LIST_ENDPOINT,
            headers=headers,
            json=watching_items
        )
        response.raise_for_status()
        print(f"Successfully added {total_items} items to the watching list")
        print(f"Movies: {len(watching_items['movies'])}, Shows: {len(watching_items['shows'])}")
    except requests.exceptions.RequestException as e:
        print(f"Error adding items to the watching list: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")

def send_watched_episodes_to_simkl() -> None:
    """Send watched episodes data to Simkl history endpoint in a single request."""
    if not SIMKL_CLIENT_ID or not SIMKL_ACCESS_TOKEN:
        print("Error: SIMKL_CLIENT_ID or SIMKL_ACCESS_TOKEN not set. Please configure them in config.py")
        sys.exit(1)

    # Check if watched episodes file exists
    if not os.path.exists("watched_episodes.json"):
        print("No watched episodes data found. Remember if the Scraper.py script didn't create the 'watched_episodes.json' file,\n you need to run the Scraper.py script first/again. \nBecause it didn't manage to get all the episodes, probably because of the rate limit of Simkl.")
        return

    # Load watched episodes data
    try:
        with open("watched_episodes.json", 'r', encoding='utf-8') as f:
            watched_episodes = json.load(f)
    except Exception as e:
        print(f"Error loading watched episodes data: {e}")
        return

    if not watched_episodes:
        print("No watched episodes data found.")
        return

    # Filter out shows with no seasons or episodes
    valid_shows = [show for show in watched_episodes if show.get("seasons")]

    if not valid_shows:
        print("No valid shows with episodes found in the 'watched_episodes.json' file.")
        return

    # Create the payload with all shows in a single request
    payload = {"shows": valid_shows}

    headers = SIMKL_API_HEADERS.copy()

    print(f"Sending watched episodes data for {len(valid_shows)} shows to Simkl in a single request...")

    try:
        response = requests.post(
            SIMKL_HISTORY_ENDPOINT,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        print(f"Successfully sent watched episodes for all {len(valid_shows)} shows")
    except requests.exceptions.RequestException as e:
        print(f"Error sending watched episodes: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")

def main():
    # Load the backup file
    backup_file = OUTPUT_FILE
    print(f"Loading backup from {backup_file}...")
    backup = load_backup(backup_file)

    # Extract plantowatch items
    plantowatch_items = extract_plantowatch_items(backup)
    print(f"Found {len(plantowatch_items['movies']) + len(plantowatch_items['shows'])} items with 'plantowatch' status")

    # Extract watching items
    watching_items = extract_watching_items(backup)
    print(f"Found {len(watching_items['movies']) + len(watching_items['shows'])} items with 'watching' status")

    # Filter out plantowatch and watching items from the backup for rating processing
    rated_backup = SimklBackup(
        movies=[movie for movie in backup['movies'] if movie.get('to') not in ['plantowatch', 'watching']],
        shows=[show for show in backup['shows'] if show.get('to') not in ['plantowatch', 'watching']]
    )

    # Check if ratings are sorted
    movies_sorted = is_sorted_by_rating(rated_backup['movies'])
    shows_sorted = is_sorted_by_rating(rated_backup['shows'])

    if not movies_sorted or not shows_sorted:
        print("Ratings are not sorted. Sorting now...")
        rated_backup = sort_by_rating(rated_backup)
        print("Ratings sorted successfully.")
    else:
        print("Ratings are already sorted.")

    # Group items by rating
    print("Grouping items by rating...")
    rating_groups = group_by_rating(rated_backup)

    # Print summary of ratings
    for rating, items in sorted(rating_groups.items(), reverse=True):
        print(f"Rating {rating}: {len(items)} items")

    # Send ratings to Simkl
    print("\nSending ratings to Simkl...")
    send_ratings_to_simkl(rating_groups)

    # Send plantowatch items to Simkl
    print("\nSending plantowatch items to Simkl...")
    print(f"Found {len(plantowatch_items['movies'])} movies and {len(plantowatch_items['shows'])} shows with 'plantowatch' status")
    send_plantowatch_to_simkl(plantowatch_items)

    # Send watching items to Simkl
    print("\nSending watching items to Simkl...")
    send_watching_to_simkl(watching_items)

    # Send watched episodes to Simkl
    print("\nSending watched episodes to Simkl...")
    send_watched_episodes_to_simkl()

    print("\nImport process completed.")

if __name__ == "__main__":
    main()