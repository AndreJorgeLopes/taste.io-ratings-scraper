# Taste.io Ratings Scraper

A Python script that scrapes your ratings from taste.io and converts them into a Simkl-compatible format.

# Note:

This script only works for shown you watched in full, because the Simkl api doesn't support episode/season ratings and I
couldn't manage to find a way to get the episode/season ratings to work on the json/csv imports. As a small side note,
you can get that info from your taste.io account on the endpoint `https://www.taste.io/api/tv/{tvShow.slug}/episodes`
with the field `items[i].user.tracked`

## Features

- Scrapes all movie and TV show ratings from your taste.io profile
- Converts ratings to Simkl format
- Supports both movies and TV shows
- Handles pagination automatically
- Exports data to JSON format
- Caches API responses for faster subsequent runs
- Advanced anti-bot detection measures
  - Random user agent selection
  - Cookie management
  - Request headers customization
  - Automated ChromeDriver management
- Configurable settings

## Requirements

- Python 3.6+
- Chrome/Chromium browser
- Selenium 4.10.0 or higher (required for experimental options)
- ChromeDriver (automatically managed)

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file based on `.env.example` and configure the following settings:

- `TASTE_USERNAME`: Your taste.io username
- `SIMKL_CLIENT_ID`: Your Simkl API client ID (get it from https://simkl.com/settings/developer/)
- `HEADLESS_MODE`: Run Chrome in headless mode (default: true)
- `MIN_DELAY`/`MAX_DELAY`: Random delay between requests (default: 1.5/4.0)
- `PAGE_LOAD_TIMEOUT`: Maximum time to wait for page load (default: 30)
- `OUTPUT_FILE`: Name of the output file (default: SimklBackup.json)

## Usage

1. Configure your environment variables in `.env`
2. Run the script:
   ```bash
   python scraper.py
   ```

The script will create a JSON file containing your ratings in the Simkl backup format. Subsequent runs will use cached
API responses when available.

## Output Formats

### JSON Output

The JSON output file follows the Simkl backup format:

```json
{
  "movies": [
    {
      "title": "Movie Title",
      "rating": 8,
      "rated_at": "2023-01-01T12:00:00Z",
      "year": 2023,
      "ids": {
        "simkl": 123456
      }
    }
  ],
  "shows": [...]
}
```

## License

MIT
