# Financial News Scraper

A web scraping tool that collects financial news from multiple sources and stores it in a database.

## Overview

This project automatically scrapes financial news from various sources, processes the information, and stores it in PostgreSQL for easy access and analysis.

## Features

- Multi-source news scraping (Moneycontrol, Yahoo Finance)
- Intelligent article summarization
- PostgreSQL database storage
- Modular scraper architecture for easy expansion
- Error handling and graceful fallbacks
- Environment-based configuration

## Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- pip package manager

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies from `requirements.txt`

## Configuration

Set up your PostgreSQL database and create a `.env` file with your database credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newsdb
DB_USER=postgres
DB_PASS=your_password
```

## Usage

Run the scraper from the `Web_scrapers` directory:

```bash
python main.py
```

This will:
- Initialize the database
- Run all configured scrapers
- Save collected news to the database
- Display a summary of results

## Project Structure

```
Web_scrapers/
├── main.py                 # Entry point
├── database.py             # Database operations
├── scraper_registry.py     # Scraper management
├── scraper_runner.py       # Execution logic
└── scrapers/               # Individual scraper implementations
    ├── moneycontrol_scraper.py
    └── yahoo_scraper.py
```

## Available Scrapers

- **Moneycontrol** - Scrapes business and market news
- **Yahoo Finance** - Scrapes financial news with summarization

## Adding New Scrapers

To add a new scraper:
1. Create a new scraper file in the `scrapers/` directory
2. Register it in `scraper_registry.py`
3. The system will automatically include it in the scraping pipeline

## Database

News articles are stored with the following information:
- Headline
- URL
- Summary
- Source
- Scrape timestamp

## Dependencies

Main dependencies include:
- BeautifulSoup4 (web scraping)
- Requests (HTTP)
- psycopg2 (PostgreSQL)
- Transformers (text summarization)
- python-dotenv (configuration)

See `requirements.txt` for complete list.

## Notes

- Scrapers include user-agent headers to prevent blocking
- Request timeouts are set to 15 seconds
- Articles are batch-inserted into the database
- The system handles errors gracefully and continues with other sources
