# Taste.io Ratings Scraper

A Python script that scrapes your ratings from taste.io and converts them into a Simkl-compatible format.

## Features

- Scrapes all movie and TV show ratings from your taste.io profile
- Converts ratings to Simkl format
- Supports both movies and TV shows
- Handles pagination automatically
- Exports data to a JSON file

## Requirements

- Python 3.6+
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)

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

## Usage

1. Make sure ChromeDriver is installed and in your system PATH
2. Replace 'ciganoo' in the script with your taste.io username
3. Run the script:
   ```bash
   python scraper.py
   ```

The script will create a `SimklBackup.json` file containing your ratings in Simkl format.

## Output Format

The output file follows the Simkl backup format:

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