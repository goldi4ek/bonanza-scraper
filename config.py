"""
Configuration settings for the Bonanza parser
"""

# URL configuration
BASE_URL = "https://www.bonanza.com"

# Parser limits
CATEGORIES_LIMIT = 3
PRODUCTS_LIMIT = 5

# Output file settings
OUTPUT_FILE = "out.csv"

# Browser options
BROWSER_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled"
]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"

# Wait times (seconds)
PAGE_LOAD_WAIT = 20
PRODUCT_SLEEP_MIN = 2
PRODUCT_SLEEP_MAX = 3

# CSV field names
CSV_FIELDS = [
    "Name", 
    "Description", 
    "Price", 
    "Product Image", 
    "Product Link", 
    "Unique Key", 
    "Bonanza Item Code", 
    "Characteristics"
]

# Original Ukrainian field names for backward compatibility
CSV_FIELDS_UA = [
    "Назва", 
    "Опис", 
    "Ціна", 
    "Фото товару", 
    "Посилання на товар", 
    "Унікальний ключ", 
    "Код товару з Bonanza", 
    "Характеристики"
]