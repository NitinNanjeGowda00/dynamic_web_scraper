import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import time
import random
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = "data"
MAX_PAGES = 5
BASE_URL = "https://quotes.toscrape.com"


# ============== ANTI-BOT FEATURES ==============

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

class Stats:
    requests = 0
    successful = 0
    failed = 0
    captchas = 0
    blocks = 0

def get_headers():
    """Get randomized browser headers."""
    ua = random.choice(USER_AGENTS)
    return {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def smart_delay(min_sec=1.5, max_sec=3.5):
    """Random delay between requests."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def is_blocked(status_code, html):
    """Check if request was blocked."""
    if status_code in {403, 429, 503}:
        return True
    
    block_indicators = ['captcha', 'blocked', 'access denied', 'unusual traffic']
    html_lower = html.lower()
    
    for indicator in block_indicators:
        if indicator in html_lower:
            return True
    return False

def fetch_with_retry(url, max_retries=3):
    """Fetch URL with retry and anti-bot protections."""
    Stats.requests += 1
    
    for attempt in range(max_retries):
        try:
            headers = get_headers()
            print(f"  User-Agent: {headers['User-Agent'][:50]}...")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if is_blocked(response.status_code, response.text):
                Stats.blocks += 1
                print(f"  Blocked! Status: {response.status_code}")
                if attempt < max_retries - 1:
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    print(f"  Retrying in {wait:.1f}s...")
                    time.sleep(wait)
                    continue
                return None
            
            response.raise_for_status()
            Stats.successful += 1
            return response.text
            
        except Exception as e:
            Stats.failed += 1
            print(f"  Error: {e}")
            if attempt < max_retries - 1:
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"  Retrying in {wait:.1f}s...")
                time.sleep(wait)
    
    return None


# ============== SCRAPING FUNCTIONS (from working run_scraper.py) ==============

def fetch_page(url):
    """Fetch a web page with anti-bot protection."""
    smart_delay()
    return fetch_with_retry(url)

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
    """Get next page URL if exists."""
    soup = BeautifulSoup(html, 'lxml')
    next_btn = soup.find('li', class_='next')
    if next_btn:
        link = next_btn.find('a')
        if link and link.get('href'):
            return link.get('href')
    return None

def save_to_csv(data, filename):
    """Save data to CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'author', 'tags'])
        writer.writeheader()
        for item in data:
            row = item.copy()
            row['tags'] = ', '.join(row['tags'])
            writer.writerow(row)
    
    return filepath

def save_to_json(data, filename):
    """Save data to JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath


def print_stats():
    """Print scraping statistics."""
    print("\n" + "=" * 40)
    print("Scraping Statistics")
    print("=" * 40)
    print(f"Total Requests:  {Stats.requests}")
    print(f"Successful:      {Stats.successful}")
    print(f"Failed:          {Stats.failed}")
    print(f"CAPTCHAs Hit:    {Stats.captchas}")
    print(f"Blocks Hit:      {Stats.blocks}")
    if Stats.requests > 0:
        rate = (Stats.successful / Stats.requests) * 100
        print(f"Success Rate:    {rate:.1f}%")
    print("=" * 40)


def main():
    print("=" * 60)
    print("Advanced Web Scraper with Anti-Bot Protection")
    print("=" * 60)
    
    print("\nAnti-Bot Features Enabled:")
    print("  ✓ User-Agent Rotation")
    print("  ✓ Browser Headers Spoofing")
    print("  ✓ Smart Request Delays")
    print("  ✓ Exponential Backoff Retry")
    print("  ✓ Block Detection")
    print()
    
    all_quotes = []
    current_url = BASE_URL
    page_number = 1
    
    while current_url and page_number <= MAX_PAGES:
        print(f"\nProcessing page {page_number}...")
        print(f"Fetching: {current_url}")
        
        html = fetch_page(current_url)
        
        if html is None:
            print("Failed to fetch page. Stopping.")
            break
        
        print(f"Fetched successfully (Length: {len(html)})")
        
        quotes = parse_quotes(html)
        print(f"Extracted {len(quotes)} quotes")
        
        all_quotes.extend(quotes)
        
        next_page = get_next_page(html)
        if next_page:
            current_url = f"{BASE_URL}{next_page}"
            page_number += 1
        else:
            print("No more pages")
            break
    
    print(f"\n{'=' * 60}")
    print(f"Total quotes collected: {len(all_quotes)}")
    
    if all_quotes:
        csv_path = save_to_csv(all_quotes, "quotes_antibot.csv")
        json_path = save_to_json(all_quotes, "quotes_antibot.json")
        print(f"Saved to: {csv_path}")
        print(f"Saved to: {json_path}")
        
        print(f"\nSample quotes:")
        for q in all_quotes[:3]:
            print(f"  - {q['author']}: {q['text'][:50]}...")
    
    print_stats()
    
    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()