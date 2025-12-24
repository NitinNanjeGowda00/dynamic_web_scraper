import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import time
import random

# Configuration
BASE_URL = "https://quotes.toscrape.com"
OUTPUT_DIR = "data"
MAX_PAGES = 5

def fetch_page(url):
    """Fetch a web page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

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

def main():
    print("=" * 50)
    print("Dynamic Web Scraper Started")
    print("=" * 50)
    
    all_quotes = []
    current_url = BASE_URL
    page_number = 1
    
    while current_url and page_number <= MAX_PAGES:
        print(f"\nProcessing page {page_number}...")
        print(f"Fetching: {current_url}")
        
        html = fetch_page(current_url)
        print(f"Fetched successfully (Length: {len(html)})")
        
        quotes = parse_quotes(html)
        print(f"Extracted {len(quotes)} quotes")
        
        all_quotes.extend(quotes)
        
        next_page = get_next_page(html)
        if next_page:
            current_url = f"{BASE_URL}{next_page}"
            page_number += 1
            time.sleep(random.uniform(1, 2))
        else:
            print("No more pages")
            break
    
    print(f"\n{'=' * 50}")
    print(f"Total quotes collected: {len(all_quotes)}")
    
    if all_quotes:
        csv_path = save_to_csv(all_quotes, "quotes.csv")
        json_path = save_to_json(all_quotes, "quotes.json")
        print(f"Saved to: {csv_path}")
        print(f"Saved to: {json_path}")
        
        print(f"\nSample quotes:")
        for q in all_quotes[:3]:
            print(f"  - {q['author']}: {q['text'][:50]}...")
    
    print("=" * 50)
    print("Scraping Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()