import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import (
    init_database,
    insert_quotes_batch,
    start_session,
    update_session,
    print_statistics,
    get_statistics
)

# Configuration
MAX_PAGES = 10  # Scrape more pages this time
BASE_URL = "https://quotes.toscrape.com"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


def fetch_page(url):
    """Fetch a web page."""
    time.sleep(random.uniform(1.0, 2.0))
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  Error: {e}")
        return None


def parse_quotes(html):
    """Extract quotes from HTML."""
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
            quotes.append({'text': text, 'author': author, 'tags': tags})
    
    return quotes


def get_next_page(html):
    """Get next page URL."""
    soup = BeautifulSoup(html, 'lxml')
    next_btn = soup.find('li', class_='next')
    if next_btn:
        link = next_btn.find('a')
        if link and link.get('href'):
            return link.get('href')
    return None


def main():
    print("=" * 60)
    print("Database-Enabled Web Scraper")
    print("=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    
    # Start session tracking
    session_id = start_session()
    print(f"Started scraping session #{session_id}")
    
    total_added = 0
    total_skipped = 0
    pages_scraped = 0
    current_url = BASE_URL
    
    print("\n" + "-" * 60)
    
    try:
        while current_url and pages_scraped < MAX_PAGES:
            pages_scraped += 1
            print(f"\nPage {pages_scraped}: {current_url}")
            
            # Fetch page
            html = fetch_page(current_url)
            if html is None:
                print("  Failed to fetch page")
                break
            
            # Parse quotes
            quotes = parse_quotes(html)
            print(f"  Found {len(quotes)} quotes on page")
            
            # Insert into database
            result = insert_quotes_batch(quotes, source_url=current_url)
            total_added += result['added']
            total_skipped += result['skipped']
            
            print(f"  Added: {result['added']}, Skipped (duplicates): {result['skipped']}")
            
            # Get next page
            next_page = get_next_page(html)
            if next_page:
                current_url = f"{BASE_URL}{next_page}"
            else:
                print("\n  No more pages available")
                break
        
        # Update session
        update_session(session_id, pages_scraped, total_added, total_skipped, 'completed')
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        update_session(session_id, pages_scraped, total_added, total_skipped, 'interrupted')
    
    except Exception as e:
        print(f"\n\nError: {e}")
        update_session(session_id, pages_scraped, total_added, total_skipped, 'failed')
    
    # Print summary
    print("\n" + "=" * 60)
    print("SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Pages Scraped:    {pages_scraped}")
    print(f"Quotes Added:     {total_added}")
    print(f"Duplicates:       {total_skipped}")
    print(f"Database:         data/quotes.db")
    
    # Print database statistics
    print_statistics()
    
    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()