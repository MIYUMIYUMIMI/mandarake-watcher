# Mandarake Watcher

A configurable Python watcher for monitoring new Mandarake listings and sending email alerts when unseen items appear.

## Features

- Monitor multiple search keywords
- Browser-based scraping with Playwright
- Parse item title, price, shop, URL, and item code
- Store seen items in SQLite
- Detect newly listed items
- Send Gmail notifications
- Configurable polling interval
- Automated tests with pytest
- GitHub Actions CI

## Project Structure

```text
mandarake_watcher/
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
├── .github/
│   └── workflows/
│       └── tests.yml
├── .env.example
├── config.example.yaml
├── .gitignore
├── pyproject.toml
└── README.md