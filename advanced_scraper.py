import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import time
import random
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = "data"
MAX_PAGES = 5
BASE_URL = "https://quotes.toscrape.com"


# ============== ANTI-BOT CLASSES (INLINE) ==============

class UserAgentRotator:
    """Manages rotation of user agents."""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    def __init__(self):
        self.current_index = 0
    
    def get_random(self) -> str:
        return random.choice(self.USER_AGENTS)
    
    def get_headers(self) -> Dict[str, str]:
        ua = self.get_random()
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        if "Chrome" in ua:
            headers["Sec-Ch-Ua"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers["Sec-Ch-Ua-Mobile"] = "?0"
            headers["Sec-Ch-Ua-Platform"] = '"Windows"'
        return headers


class RequestThrottler:
    """Smart request rate limiting."""
    
    def __init__(self, min_delay=1.0, max_delay=3.0, requests_per_minute=20):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.consecutive_errors = 0
    
    def wait(self):
        # Clean old times
        cutoff = datetime.now() - timedelta(minutes=1)
        self.request_times = [t for t in self.request_times if t > cutoff]
        
        # Rate limit check
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (datetime.now() - self.request_times[0]).total_seconds()
            if wait_time > 0:
                print(f"  Rate limit reached. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        # Random delay with error multiplier
        base_delay = random.uniform(self.min_delay, self.max_delay)
        error_multiplier = 1 + (self.consecutive_errors * 0.5)
        actual_delay = base_delay * error_multiplier
        
        time.sleep(actual_delay)
        self.request_times.append(datetime.now())
    
    def record_success(self):
        self.consecutive_errors = 0
    
    def record_error(self):
        self.consecutive_errors += 1


class RetryHandler:
    """Exponential backoff retry logic."""
    
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** attempt)
        jitter = delay * 0.25 * random.uniform(-1, 1)
        return min(delay + jitter, 60.0)
    
    def execute(self, func, *args, **kwargs):
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self.get_delay(attempt)
                    print(f"  Attempt {attempt+1} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        raise last_error


class CaptchaDetector:
    """Detect CAPTCHA and blocks."""
    
    INDICATORS = ["captcha", "recaptcha", "hcaptcha", "verify you are human",
                  "access denied", "blocked", "unusual traffic", "cloudflare"]
    
    @classmethod
    def is_blocked(cls, status_code: int, html: str = None) -> bool:
        if status_code in {403, 429, 503}:
            return True
        if html:
            html_lower = html.lower()
            for indicator in cls.INDICATORS:
                if indicator in html_lower:
                    return True
        return False
    
    @classmethod
    def get_reason(cls, status_code: int) -> str:
        reasons = {403: "Access Forbidden", 429: "Rate Limited", 503: "Service Unavailable"}
        return reasons.get(status_code, "Unknown")


# ============== SCRAPER FUNCTIONS ==============

def fetch_page(url: str, ua_rotator: UserAgentRotator, throttler: RequestThrottler, 
               retry_handler: RetryHandler, stats: dict) -> Optional[str]:
    """Fetch URL with anti-bot protections."""
    
    def do_request():
        headers = ua_rotator.get_headers()
        print(f"  User-Agent: {headers['User-Agent'][:50]}...")
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        if CaptchaDetector.is_blocked(response.status_code, response.text):
            stats['blocks'] += 1
            raise Exception(f"Blocked: {CaptchaDetector.get_reason(response.status_code)}")
        
        return response.text
    
    throttler.wait()
    stats['requests'] += 1
    
    try:
        html = retry_handler.execute(do_request)
        stats['successful'] += 1
        throttler.record_success()
        return html
    except Exception as e:
        stats['failed'] += 1
        throttler.record_error()
        print(f"  Error: {e}")
        return None


def parse_quotes(html: str) -> List[Dict]:
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


def get_next_page(html: str) -> Optional[str]:
    """Get next page URL."""
    soup = BeautifulSoup(html, 'lxml')
    next_btn = soup.find('li', class_='next')
    if next_btn:
        link = next_btn.find('a')
        if link and link.get('href'):
            return link.get('href')
    return None


def save_data(data: List[Dict], filename: str):
    """Save to CSV and JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    csv_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'author', 'tags'])
        writer.writeheader()
        for item in data:
            row = item.copy()
            row['tags'] = ', '.join(row['tags'])
            writer.writerow(row)
    
    json_path = os.path.join(OUTPUT_DIR, f"{filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return csv_path, json_path


def print_stats(stats: dict):
    """Print statistics."""
    print("\n" + "=" * 40)
    print("Scraping Statistics")
    print("=" * 40)
    print(f"Total Requests:  {stats['requests']}")
    print(f"Successful:      {stats['successful']}")
    print(f"Failed:          {stats['failed']}")
    print(f"CAPTCHAs Hit:    {stats['captchas']}")
    print(f"Blocks Hit:      {stats['blocks']}")
    if stats['requests'] > 0:
        rate = (stats['successful'] / stats['requests']) * 100
        print(f"Success Rate:    {rate:.1f}%")
    print("=" * 40)


def main():
    print("=" * 60)
    print("Advanced Web Scraper with Anti-Bot Protection")
    print("=" * 60)
    
    # Initialize components
    ua_rotator = UserAgentRotator()
    throttler = RequestThrottler(min_delay=1.5, max_delay=3.0)
    retry_handler = RetryHandler(max_retries=3)
    stats = {'requests': 0, 'successful': 0, 'failed': 0, 'captchas': 0, 'blocks': 0}
    
    print("\nAnti-Bot Features Enabled:")
    print("  ✓ User-Agent Rotation")
    print("  ✓ Browser Headers Spoofing")
    print("  ✓ Request Throttling")
    print("  ✓ Exponential Backoff Retry")
    print("  ✓ CAPTCHA Detection")
    
    all_quotes = []
    current_url = BASE_URL
    page_number = 1
    
    while current_url and page_number <= MAX_PAGES:
        print(f"\n{'='*50}")
        print(f"Page {page_number}: {current_url}")
        print(f"{'='*50}")
        
        html = fetch_page(current_url, ua_rotator, throttler, retry_handler, stats)
        
        if html is None:
            print("Failed to fetch. Stopping.")
            break
        
        if CaptchaDetector.is_blocked(200, html):
            print("CAPTCHA detected! Stopping.")
            stats['captchas'] += 1
            break
        
        quotes = parse_quotes(html)
        print(f"  Extracted: {len(quotes)} quotes")
        all_quotes.extend(quotes)
        
        next_page = get_next_page(html)
        if next_page:
            current_url = f"{BASE_URL}{next_page}"
            page_number += 1
        else:
            print("\nNo more pages.")
            break
    
    print(f"\n{'='*60}")
    print(f"Total quotes collected: {len(all_quotes)}")
    
    if all_quotes:
        csv_path, json_path = save_data(all_quotes, "quotes_antibot")
        print(f"Saved to: {csv_path}")
        print(f"Saved to: {json_path}")
        
        print("\nSample quotes:")
        for q in all_quotes[:3]:
            print(f"  - {q['author']}: {q['text'][:50]}...")
    
    print_stats(stats)
    print("\n" + "=" * 60)
    print("Scraping Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()