# Taste.io Ratings Scraper

A Python script that scrapes your ratings from taste.io and converts them into a Simkl-compatible format.

## Features

- Scrapes all movie and TV show ratings from your taste.io profile
- Converts ratings to Simkl format
- Supports both movies and TV shows
- Handles pagination automatically
- Exports data to both JSON and CSV formats
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

Edit `config.py` to customize the scraper settings:

- `USERNAME`: Your taste.io username
- `HEADLESS_MODE`: Run Chrome in headless mode (default: True)
- `MIN_DELAY`/`MAX_DELAY`: Random delay between requests to avoid rate limiting
- `PAGE_LOAD_TIMEOUT`: Maximum time to wait for page load
- `OUTPUT_FILE`: Name of the output file
- `JSON_INDENT`: Number of spaces for JSON indentation
- `CSV_ENABLED`: Enable CSV output alongside JSON
- `CSV_FIELDS`: Fields to include in CSV output
- `USER_AGENTS`: List of user agents to rotate through
- `REQUEST_HEADERS`: Custom headers for requests
- `COOKIE_DEFAULTS`: Default cookie values for authentication

## Usage

1. Configure your taste.io username in `config.py`
2. Run the script:
   ```bash
   python scraper.py
   ```

The script will create output files containing your ratings in the specified format(s).

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

### CSV Output

When CSV export is enabled, the script creates a CSV file with the following fields:
- title
- rating
- rated_at
- year

Both movies and TV shows are included in the same CSV file.

## License

MIT