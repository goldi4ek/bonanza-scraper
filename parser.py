import undetected_chromedriver as uc
import time
import random
import csv
import uuid
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config

# =============================================================================
# Browser management class (driver initialization and termination)
# =============================================================================
class DriverManager:
    def __init__(self):
        """Initializes the driver with required parameters."""
        options = uc.ChromeOptions()
        for option in config.BROWSER_OPTIONS:
            options.add_argument(option)
        options.add_argument(f"user-agent={config.USER_AGENT}")
        self.driver = uc.Chrome(options=options)

    def get_driver(self):
        """Returns the driver."""
        return self.driver

    def quit(self):
        """Closes the driver."""
        self.driver.quit()


# =============================================================================
# Class for extracting category links
# =============================================================================
class CategoryExtractor:
    def __init__(self, driver, base_url: str, limit: int = 3):
        """
        :param driver: Driver object
        :param base_url: Website base URL
        :param limit: Maximum number of categories to process
        """
        self.driver = driver
        self.base_url = base_url
        self.limit = limit

    def extract_categories(self) -> list:
        """Gets category links from the page and returns a limited list."""
        self.driver.get(f"{self.base_url}/booths/browse_categories")
        # Wait for the element with id "main_right" to load
        WebDriverWait(self.driver, config.PAGE_LOAD_WAIT).until(
            EC.presence_of_element_located((By.ID, "main_right"))
        )
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        containers = soup.findAll("div", class_="category_group_container")
        links = []
        if containers:
            for category in containers:
                container_mid = category.find("div", class_="category_group_container_mid")
                if container_mid:
                    link_tag = container_mid.find("a")
                    if link_tag and link_tag.get("href"):
                        link = link_tag.get("href")
                        if not link.startswith("http"):
                            link = self.base_url + link
                        links.append(link)
        else:
            print("Navigation container not found")
        print("Categories found:", len(links))
        return links[:self.limit]


# =============================================================================
# Class for product processing: getting links from category and product data
# =============================================================================
class ProductExtractor:
    def __init__(self, driver, base_url: str, products_limit: int = 5):
        """
        :param driver: Driver object
        :param base_url: Website base URL
        :param products_limit: Maximum number of products to process in a category
        """
        self.driver = driver
        self.base_url = base_url
        self.products_limit = products_limit

    def extract_product_links(self, category_url: str) -> list:
        """Gets product links from the category page."""
        self.driver.get(category_url)
        try:
            WebDriverWait(self.driver, config.PAGE_LOAD_WAIT).until(
                EC.presence_of_element_located((By.ID, "search_pages_container"))
            )
        except Exception as e:
            print("Waiting error for category:", category_url, e)
            return []
        time.sleep(random.uniform(config.PRODUCT_SLEEP_MIN, config.PRODUCT_SLEEP_MAX))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find("div", class_="search_results_items_container")
        links = []
        if container:
            items = container.find_all("div", class_="search_result_item")[:self.products_limit]
            print(f"Found items in category (limited to {self.products_limit}): {len(items)}")
            for item in items:
                a_tag = item.find("a")
                if a_tag and a_tag.get("href"):
                    link = a_tag.get("href")
                    if not link.startswith("http"):
                        link = self.base_url + link
                    links.append(link)
        else:
            print("Search results container not found in category:", category_url)
        return links

    def extract_product_details(self, product_url: str) -> dict:
        """Gets product data from the link."""
        self.driver.get(product_url)
        try:
            WebDriverWait(self.driver, config.PAGE_LOAD_WAIT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            print("Waiting error for product:", product_url, e)
            return {}
        time.sleep(random.uniform(config.PRODUCT_SLEEP_MIN, config.PRODUCT_SLEEP_MAX))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 1. Getting the main image link
        image_href = None
        main_image_container = soup.find("div", class_="main_image_container")
        if main_image_container:
            a_img = main_image_container.find("a", class_="fancybox_trigger")
            if a_img:
                image_href = a_img.get("href")

        # 2. Getting basic information (price and text from span)
        basic_info_div = soup.find("div", class_="item_listing_basic_info")
        span_text = None
        price_text = None
        if basic_info_div:
            span_tag = basic_info_div.find("span")
            if span_tag:
                span_text = span_tag.get_text(strip=True)
            price_div = basic_info_div.find("div", class_="item_price")
            if price_div:
                price_text = price_div.get_text(strip=True)

        # 3. Getting product description
        description_text = None
        description_div = soup.find("div", class_="item_description_inner")
        if description_div:
            full_text = description_div.get_text(" ", strip=True)
            if "Item Description" in full_text and "About Us" in full_text:
                start_index = full_text.find("Item Description") + len("Item Description")
                end_index = full_text.find("About Us")
                description_text = full_text[start_index:end_index].strip()
            else:
                description_text = full_text

        # 4. Getting product characteristics (4th and 5th rows of the table)
        traits = {}
        traits_div = soup.find("div", class_="item_listing_item_traits")
        if traits_div:
            table = traits_div.find("table")
            if table:
                tbody = table.find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                    if len(rows) >= 5:
                        for row in rows[3:5]:
                            label_tag = row.find("th", class_="extended_info_label")
                            value_tag = row.find("td", class_="extended_info_value")
                            if label_tag and value_tag:
                                key = label_tag.get_text(strip=True).rstrip(":")
                                val = value_tag.get_text(strip=True)
                                traits[key] = val
                    else:
                        print("Not enough rows in the characteristics table")

        # 5. Getting product code from Bonanza (item number)
        listing_number = None
        listing_details_div = soup.find("div", class_="listing_details_section")
        if listing_details_div:
            table = listing_details_div.find("table")
            if table:
                tbody = table.find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                    if rows:
                        last_row = rows[-1]
                        tds = last_row.find_all("td")
                        if tds:
                            listing_number = tds[-1].get_text(strip=True)

        # 6. Generating unique key
        unique_key = str(uuid.uuid4())

        # Use either English or Ukrainian field names based on config
        field_names = config.CSV_FIELDS_UA  # Using Ukrainian for backward compatibility
        
        return {
            field_names[0]: span_text if span_text else "",
            field_names[1]: description_text if description_text else "",
            field_names[2]: price_text if price_text else "",
            field_names[3]: image_href if image_href else "",
            field_names[4]: product_url,
            field_names[5]: unique_key,
            field_names[6]: listing_number if listing_number else "",
            field_names[7]: "; ".join([f"{k}: {v}" for k, v in traits.items()])
        }


# =============================================================================
# Class for writing data to a CSV file
# =============================================================================
class CSVWriter:
    def __init__(self, filename: str, fieldnames: list):
        """
        :param filename: CSV filename for saving results
        :param fieldnames: Column names list
        """
        self.filename = filename
        self.fieldnames = fieldnames

    def write(self, rows: list):
        """Writes a list of dictionaries to a CSV file."""
        with open(self.filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"\nResults saved to file {self.filename}")


# =============================================================================
# Main Bonanza parser class that combines all components
# =============================================================================
class BonanzaParser:
    def __init__(self, base_url: str = config.BASE_URL, 
                 categories_limit: int = config.CATEGORIES_LIMIT, 
                 products_limit: int = config.PRODUCTS_LIMIT, 
                 output_file: str = config.OUTPUT_FILE):
        self.base_url = base_url
        self.categories_limit = categories_limit
        self.products_limit = products_limit
        self.output_file = output_file
        self.driver_manager = DriverManager()
        self.driver = self.driver_manager.get_driver()
        self.category_extractor = CategoryExtractor(self.driver, self.base_url, self.categories_limit)
        self.product_extractor = ProductExtractor(self.driver, self.base_url, self.products_limit)
        self.csv_writer = CSVWriter(self.output_file, config.CSV_FIELDS_UA)

    def run(self):
        """Launches the parsing process: collecting categories, products and processing them, saving results to CSV."""
        results = []
        categories = self.category_extractor.extract_categories()
        for cat_idx, cat_link in enumerate(categories, start=1):
            print(f"\n[Category {cat_idx}] Going to category: {cat_link}")
            product_links = self.product_extractor.extract_product_links(cat_link)
            for prod_idx, prod_link in enumerate(product_links, start=1):
                print(f"  [Category {cat_idx} - Product {prod_idx}] Processing product: {prod_link}")
                details = self.product_extractor.extract_product_details(prod_link)
                if details:
                    results.append(details)
        self.driver_manager.quit()
        self.csv_writer.write(results)


def main():
    parser = BonanzaParser()
    parser.run()


if __name__ == "__main__":
    main()