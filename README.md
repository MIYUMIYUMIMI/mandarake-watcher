# Mandarake Watcher

A configurable Python application for monitoring new listings on Mandarake and sending email alerts when unseen items appear.

The watcher uses Playwright to load Mandarake search pages, parses product information, stores previously seen items in SQLite, and sends Gmail notifications only when new item codes are detected.

## Features

- Monitor multiple Mandarake search keywords
- Configure keywords without modifying Python code
- Automatically check listings at a configurable interval
- Browser-based scraping with Playwright
- Extract:
  - item code
  - title
  - price
  - shop
  - product URL
- Store previously seen items in SQLite
- Detect newly appearing listings
- Avoid duplicate notifications
- Send Gmail notifications for new items
- Preserve browser session data with a persistent browser profile
- Unit tests with pytest
- Automated testing with GitHub Actions

## How It Works

```text
config.yaml
    |
    v
Playwright browser
    |
    v
Mandarake search page
    |
    v
HTML parser
    |
    v
Current product listings
    |
    v
SQLite seen-item database
    |
    +---- already seen ----> ignore
    |
    +---- new item --------> Gmail notification
```

Each Mandarake product has an item code.

For example:

```text
1349446110
```

The watcher uses this item code as the identifier for determining whether a listing has already been seen.

On the first run for a new keyword, the current search results are stored as the initial baseline.

After that, only item codes that have not previously been stored are treated as new listings.

## Project Structure

```text
mandarake_watcher/
├── .github/
│   └── workflows/
│       └── tests.yaml
├── src/
│   └── mandarake_watcher/
│       ├── __init__.py
│       ├── main.py
│       ├── notifier.py
│       ├── scraper.py
│       └── storage.py
├── tests/
│   ├── test_scraper.py
│   └── test_storage.py
├── .env.example
├── .gitignore
├── config.example.yaml
├── pyproject.toml
└── README.md
```

## Components

### `scraper.py`

Handles Mandarake search-page access and product parsing.

The scraper:

1. Opens Mandarake using Playwright.
2. Reuses a persistent browser profile.
3. Loads the search page for a keyword.
4. Finds product cards in the page.
5. Extracts structured product information.

A parsed item contains:

```python
Item(
    item_code="1349446110",
    title="...",
    price="1,500円 (税込 1,650円)",
    shop="中野店",
    url="https://order.mandarake.co.jp/order/detailPage/item?itemCode=1349446110",
)
```

### `storage.py`

Uses SQLite to remember which products have already been seen.

Listings are stored using a combination of:

```text
keyword + item_code
```

This allows the same product to be tracked independently across different search keywords.

The database also stores:

```text
title
price
shop
url
first_seen
last_seen
```

### `notifier.py`

Sends an email when new items are detected.

Email credentials are read from environment variables rather than being stored directly in the source code.

### `main.py`

Runs the monitoring loop.

For each configured keyword it:

```text
search
  ↓
parse
  ↓
compare with SQLite
  ↓
detect new items
  ↓
send notification if necessary
  ↓
wait
  ↓
repeat
```

## Requirements

- Python 3.10+
- Microsoft Edge
- Gmail account for email notifications

The project has been developed and tested with Python 3.12 on Windows.

## Installation

Clone the repository:

```bash
git clone https://github.com/MIYUMIYUMIMI/mandarake-watcher.git
cd mandarake-watcher
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

## Configuration

The repository contains:

```text
config.example.yaml
```

Copy it to:

```text
config.yaml
```

On Windows PowerShell:

```powershell
Copy-Item config.example.yaml config.yaml
```

Example configuration:

```yaml
keywords:
  - pokemon
  - pikachu

check_interval_seconds: 300
```

You can monitor any Mandarake search terms by modifying the keyword list.

For example:

```yaml
keywords:
  - pokemon
  - 初音ミク
  - miku

check_interval_seconds: 300
```

`check_interval_seconds` controls how long the application waits between monitoring cycles.

For example:

```yaml
check_interval_seconds: 300
```

means:

```text
300 seconds = 5 minutes
```

The personal `config.yaml` file is excluded from Git.

## Gmail Configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure your Gmail SMTP settings:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=your_email@gmail.com
```

For Gmail, use a Google App Password rather than your normal Google account password.

Your real `.env` file is excluded from Git and should never be committed.

## Running the Watcher

Start the watcher with:

```powershell
python -m mandarake_watcher.main
```

Example output:

```text
Mandarake Watcher started.
Keywords: pokemon, pikachu
Check interval: 300 seconds
Press Ctrl+C to stop.
```

During a normal check:

```text
======================================================================
[2026-10-02 10:30:00] Checking: pokemon
======================================================================

Opening Mandarake home page...
Opening: https://order.mandarake.co.jp/order/listPage/list?keyword=pokemon

Found 48 current items.
No new items found for 'pokemon'.
```

When a new listing appears:

```text
NEW ITEMS for 'pokemon': 1

[NEW] Example Pokemon Item
Shop: 中野店
Price: 1,500円 (税込 1,650円)
https://order.mandarake.co.jp/order/detailPage/item?itemCode=1234567890
```

An email notification is then sent automatically.

To stop the watcher:

```text
Ctrl+C
```

## First Run Behaviour

When a keyword is monitored for the first time, the watcher creates an initial baseline.

For example:

```text
Initial baseline created for 'pokemon' with 48 items.
No new items found.
```

Those existing products are recorded without generating notifications.

If a later search contains a previously unseen item code:

```text
existing item -> ignored

new item code -> stored
              -> marked as NEW
              -> email sent
```

This prevents the watcher from sending an email for every existing search result when a new keyword is first added.

## Testing

The project includes unit tests for the parser and SQLite storage logic.

Run all tests with:

```powershell
python -m pytest
```

Current tests cover:

- parsing a Mandarake product card
- extracting item codes
- extracting titles
- extracting shops
- normalising prices
- generating product URLs
- ignoring malformed product cards
- creating an initial SQLite baseline
- detecting newly appearing item codes
- preventing duplicate notifications

Example:

```text
6 passed
```

The tests use local sample HTML and temporary SQLite databases.

They do not need to access Mandarake or send real emails.

## Continuous Integration

GitHub Actions automatically runs the test suite when code is pushed to the `main` branch or when a pull request targets `main`.

Workflow:

```text
push / pull request
        |
        v
GitHub Actions
        |
        v
Python 3.12
        |
        v
install project
        |
        v
pytest
```

The workflow configuration is located at:

```text
.github/workflows/tests.yaml
```

## Local Files

Some files are intentionally excluded from version control.

These include:

```text
.env
config.yaml
*.db
.mandarake_profile/
.venv/
__pycache__/
.pytest_cache/
*.egg-info/
mandarake_debug.html
```

### `.env`

Contains private email credentials.

### `config.yaml`

Contains the user's personal monitoring keywords.

### SQLite database

Stores the user's local monitoring history.

### `.mandarake_profile/`

Stores the persistent browser profile used by Playwright.

These files should remain local and should not be committed to GitHub.

## Security

Secrets are loaded through environment variables.

The repository contains:

```text
.env.example
```

as a configuration template, while the real:

```text
.env
```

is ignored by Git.

Never commit:

```text
Gmail passwords
Google App Passwords
session data
personal browser profiles
```

## Technologies

- Python
- Playwright
- BeautifulSoup
- SQLite
- SMTP
- Gmail
- PyYAML
- python-dotenv
- pytest
- GitHub Actions

## Future Improvements

Possible extensions include:

- richer HTML email notifications
- product images in notifications
- configurable shop filters
- price filters
- include/exclude keyword rules
- structured logging
- retry handling
- monitoring statistics
- command-line configuration
- support for additional second-hand marketplaces
- Docker deployment
- scheduled cloud deployment

## Motivation

Mandarake provides a large and frequently changing catalogue of collectible products.

This project was created as a configurable personal monitoring tool that can repeatedly check search results, remember previously observed listings, and surface newly appearing products automatically.

It also demonstrates practical software engineering concepts including:

- browser automation
- HTML parsing
- persistent state
- database operations
- configuration management
- environment-variable based secret management
- email integration
- automated testing
- continuous integration