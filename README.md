# Bonanza Product Scraper

A web scraper that extracts product information from the Bonanza marketplace.

## Overview

This tool navigates through product categories on Bonanza.com, extracts product details, and saves the data to a CSV file. The script uses Selenium with undetected-chromedriver to avoid detection by anti-bot measures.

## Features

- Category navigation and extraction
- Product detail extraction (name, price, description, images, etc.)
- Configurable scraping parameters (categories limit, products per category)
- CSV export with customizable field names
- Anti-detection measures

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/goldi4ek/bonanza-scraper.git
   cd bonanza-scraper
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Make sure you have Chrome browser installed on your system.

## Usage

1. Configure scraping parameters in `config.py` if needed.

2. Run the scraper:
   ```
   python parser.py
   ```

3. Results will be saved to `out.csv` (or the filename specified in `config.py`).

## Configuration

Edit `config.py` to modify these settings:

- `BASE_URL`: The base URL of the website
- `CATEGORIES_LIMIT`: Maximum number of categories to scrape
- `PRODUCTS_LIMIT`: Maximum number of products to scrape per category
- `OUTPUT_FILE`: Name of the output CSV file
- `BROWSER_OPTIONS`: Chrome browser options
- `PAGE_LOAD_WAIT`: Maximum wait time for page elements to load
- `PRODUCT_SLEEP_MIN/MAX`: Random delay range between requests

## Project Structure

- `parser.py`: Main script containing the scraping logic
- `config.py`: Configuration settings
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation