# Taste.io Ratings Scraper

A Python library that scrapes your ratings from taste.io and converts them into a Simkl-compatible format.

# Note:

To get your taste.io authentication token, follow these steps:

1. Log in to your taste.io account.
2. Open the Developer Tools in your browser (usually by pressing F12).
3. Navigate to the "Network" tab.
4. Reload the taste.io page.
5. In the "Network" tab, look for a request with the endpoint "/me".
6. Click on the request to view its details.
7. Copy the Authorization token (without the `Bearer` part) from the headers tab
8. Paste it into the `TASTE_TOKEN` variable value.

![Chrome Example](/images/taste-chrome-example.png)

## Configuration

Create a `.env` file based on `.env.example` and configure the following settings:

- `TASTE_USERNAME`: Your taste.io username
- `TASTE_TOKEN`: Your taste.io authentication token (required for continue-watching and episode tracking)
- `SIMKL_CLIENT_ID`: Your Simkl API client ID (get it from https://simkl.com/settings/developer/)
- `SIMKL_ACCESS_TOKEN`: Your Simkl access token (Get it by following the instructions at this link:
  https://simkl.docs.apiary.io/#reference/authentication-oauth-2.0/)
- `HEADLESS_MODE`: Run Chrome in headless mode (default: true)
- `MIN_DELAY`/`MAX_DELAY`: Random delay between requests (default: 1.5/4.0)
- `PAGE_LOAD_TIMEOUT`: Maximum time to wait for page load (default: 30)
- `OUTPUT_FILE`: Name of the output file (default: SimklBackup.json)

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
- Converts taste.io's 4-star rating system to Simkl's 10-point scale
- Fetches Simkl IDs for each title

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

Create a `.env` file based on `.env.example`

## Usage

1. Configure your environment variables in `.env`
2. Run the scraper script:
   ```bash
   python scraper.py
   ```
3. Try to import the json into the importer on their website manually or run the auto importer script:
   ```bash
   python importer.py
   ```

The scraper script will create a JSON file containing your ratings in the Simkl backup format. Subsequent runs will use
cached API responses when available.

The import script will import the ratings from the JSON file into your Simkl account by chunking them into ratings after
sorting them.

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
