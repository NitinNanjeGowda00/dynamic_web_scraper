from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import random
import csv
import json
import os

# Configuration
OUTPUT_DIR = "data"
HEADLESS = True  # Set to False to see browser in action
MAX_PAGES = 5


class SeleniumScraper:
    """Web scraper using Selenium for dynamic content."""
    
    def __init__(self, headless=True):
        """Initialize the Selenium WebDriver."""
        self.options = Options()
        
        if headless:
            self.options.add_argument("--headless=new")
        
        # Common options to avoid detection
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        
        # Disable automation flags
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver - let Selenium manage the driver automatically
        print("Initializing Chrome WebDriver...")
        try:
            # Try without specifying service (Selenium 4.6+ auto-manages drivers)
            self.driver = webdriver.Chrome(options=self.options)
        except Exception as e:
            print(f"Auto driver failed: {e}")
            print("Trying with webdriver-manager...")
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options
            )
        
        self.driver.implicitly_wait(10)
        print("WebDriver initialized successfully!")
    
    def get_page(self, url):
        """Navigate to a URL and return page source."""
        print(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(random.uniform(1, 2))
        return self.driver.page_source
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {value}")
            return None
    
    def click_element(self, by, value):
        """Click an element."""
        try:
            element = self.wait_for_element(by, value)
            if element:
                element.click()
                return True
        except Exception as e:
            print(f"Error clicking element: {e}")
        return False
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    
    def scroll_infinite(self, max_scrolls=5):
        """Handle infinite scroll pages."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(max_scrolls):
            print(f"Scrolling... ({i+1}/{max_scrolls})")
            self.scroll_to_bottom()
            time.sleep(2)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached end of page")
                break
            last_height = new_height
    
    def get_page_source(self):
        """Get current page source."""
        return self.driver.page_source
    
    def close(self):
        """Close the browser."""
        print("Closing browser...")
        self.driver.quit()


def parse_quotes(html):
    """Extract quotes from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, 'lxml')
    quotes = []
    
    for element in soup.find_all('div', class_='quote'):
        text_el = element.find('span', class_='text')
        author_el = element.find('small', class_='author')
        tag_els = element.find_all('a', class_='tag')
        
        text = text_el.get_text(strip=True).strip('\u201c\u201d"') if text_el else None
        author = author_el.get_text(strip=True) if author_el else None
        tags = [t.get_text(strip=True) for t in tag_els]
        
        if text and author:
            quotes.append({
                'text': text,
                'author': author,
                'tags': tags
            })
    
    return quotes


def get_next_page_url(html):
    """Check if next page exists."""
    soup = BeautifulSoup(html, 'lxml')
    next_btn = soup.find('li', class_='next')
    if next_btn:
        link = next_btn.find('a')
        if link and link.get('href'):
            return link.get('href')
    return None


def save_data(data, base_filename):
    """Save data to CSV and JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save CSV
    csv_path = os.path.join(OUTPUT_DIR, f"{base_filename}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'author', 'tags'])
        writer.writeheader()
        for item in data:
            row = item.copy()
            row['tags'] = ', '.join(row['tags'])
            writer.writerow(row)
    
    # Save JSON
    json_path = os.path.join(OUTPUT_DIR, f"{base_filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return csv_path, json_path


def main():
    print("=" * 60)
    print("Selenium Web Scraper - Dynamic Content Handler")
    print("=" * 60)
    
    # Initialize scraper
    scraper = SeleniumScraper(headless=HEADLESS)
    all_quotes = []
    
    try:
        # Start URL - JavaScript rendered version
        base_url = "https://quotes.toscrape.com/js/"
        current_url = base_url
        page_number = 1
        
        while current_url and page_number <= MAX_PAGES:
            print(f"\n{'='*40}")
            print(f"Processing Page {page_number}")
            print(f"{'='*40}")
            
            # Get page
            html = scraper.get_page(current_url)
            
            # Wait for quotes to load (JavaScript rendering)
            scraper.wait_for_element(By.CLASS_NAME, "quote", timeout=10)
            
            # Get updated page source after JS execution
            html = scraper.get_page_source()
            
            # Parse quotes
            quotes = parse_quotes(html)
            print(f"Extracted {len(quotes)} quotes")
            all_quotes.extend(quotes)
            
            # Check for next page
            next_page = get_next_page_url(html)
            if next_page:
                current_url = f"https://quotes.toscrape.com{next_page}"
                page_number += 1
                time.sleep(random.uniform(1, 2))
            else:
                print("No more pages found")
                break
        
        # Save results
        print(f"\n{'='*60}")
        print(f"Total quotes collected: {len(all_quotes)}")
        
        if all_quotes:
            csv_path, json_path = save_data(all_quotes, "quotes_selenium")
            print(f"Saved to: {csv_path}")
            print(f"Saved to: {json_path}")
            
            print(f"\nSample quotes:")
            for q in all_quotes[:3]:
                print(f"  - {q['author']}: {q['text'][:50]}...")
    
    finally:
        scraper.close()
    
    print("=" * 60)
    print("Scraping Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()