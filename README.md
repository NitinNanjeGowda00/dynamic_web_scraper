# 🕷️ Dynamic Web Scraper

A professional Python web scraping toolkit demonstrating multiple scraping techniques, anti-bot measures, and database storage. Built as a portfolio project showcasing production-ready web automation skills.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Scrapers Overview](#-scrapers-overview)
- [Anti-Bot Techniques](#-anti-bot-techniques)
- [Database Schema](#-database-schema)
- [Skills Demonstrated](#-skills-demonstrated)
- [Sample Output](#-sample-output)
- [License](#-license)

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Static Scraping** | Fast scraping with Requests + BeautifulSoup |
| **Dynamic Scraping** | JavaScript rendering with Selenium WebDriver |
| **Anti-Bot Protection** | User-agent rotation, delays, retry logic |
| **Database Storage** | SQLite with normalized schema |
| **Duplicate Prevention** | Automatic detection of existing records |
| **Session Tracking** | Statistics for each scraping session |
| **Multi-Format Export** | CSV, JSON, and database output |

## 📁 Project Structure
```
dynamic_web_scraper/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
│
├── src/
│   ├── __init__.py
│   ├── scraper.py           # Base scraper class
│   ├── parser.py            # HTML parsing utilities
│   ├── exporter.py          # CSV/JSON export
│   ├── database.py          # SQLite operations
│   ├── antibot.py           # Anti-detection module
│   └── utils.py             # Helper functions
│
├── data/
│   ├── quotes.db            # SQLite database
│   ├── quotes.csv           # CSV export
│   └── quotes.json          # JSON export
│
├── logs/                    # Log files
│
├── run_scraper.py           # Basic Requests scraper
├── selenium_scraper.py      # Selenium for JS content
├── final_antibot_scraper.py # Anti-bot protected scraper
├── db_scraper.py            # Database-enabled scraper
├── db_query.py              # Database query tool
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Google Chrome browser (for Selenium)
- Git

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/nitingowdaroan-alt/dynamic_web_scraper.git
   cd dynamic_web_scraper
```

2. **Create virtual environment**
```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

## 📖 Usage

### Basic Scraper (Requests + BeautifulSoup)
```bash
python run_scraper.py
```
Fast scraping for static HTML pages. Exports to CSV and JSON.

### Selenium Scraper (Dynamic Content)
```bash
python selenium_scraper.py
```
Handles JavaScript-rendered content using headless Chrome.

### Anti-Bot Scraper
```bash
python final_antibot_scraper.py
```
Includes user-agent rotation, smart delays, and retry logic.

### Database Scraper
```bash
python db_scraper.py
```
Stores data in SQLite with duplicate prevention and session tracking.

### Query Database
```bash
python db_query.py
```
Interactive tool to search and explore scraped data.

## 🔧 Scrapers Overview

### 1. Basic Scraper (`run_scraper.py`)

| Feature | Implementation |
|---------|---------------|
| HTTP Client | `requests` library |
| Parser | BeautifulSoup with lxml |
| Output | CSV, JSON |
| Speed | ~5 pages/second |
```python
# Example usage
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
quotes = soup.find_all('div', class_='quote')
```

### 2. Selenium Scraper (`selenium_scraper.py`)

| Feature | Implementation |
|---------|---------------|
| Browser | Chrome (headless) |
| Wait Strategy | Explicit waits with WebDriverWait |
| JS Handling | Full JavaScript execution |
| Anti-Detection | Disabled automation flags |
```python
# Example usage
driver = webdriver.Chrome(options=options)
driver.get(url)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "quote"))
)
```

### 3. Anti-Bot Scraper (`final_antibot_scraper.py`)

| Feature | Implementation |
|---------|---------------|
| User-Agent | Random rotation from 5+ browsers |
| Delays | Random 1.5-3.5 seconds |
| Retry | Exponential backoff (3 attempts) |
| Detection | Block/CAPTCHA detection |

### 4. Database Scraper (`db_scraper.py`)

| Feature | Implementation |
|---------|---------------|
| Database | SQLite3 |
| Schema | Normalized (authors, quotes, tags) |
| Duplicates | Prevented via UNIQUE constraints |
| Tracking | Session statistics |

## 🛡️ Anti-Bot Techniques

This project implements several techniques to avoid detection:

### User-Agent Rotation
```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0",
    # ... more agents
]
headers = {'User-Agent': random.choice(USER_AGENTS)}
```

### Smart Request Delays
```python
def smart_delay(min_sec=1.5, max_sec=3.5):
    time.sleep(random.uniform(min_sec, max_sec))
```

### Exponential Backoff Retry
```python
for attempt in range(max_retries):
    try:
        response = requests.get(url, headers=headers)
        break
    except Exception:
        wait = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(wait)
```

### Block Detection
```python
def is_blocked(status_code, html):
    if status_code in {403, 429, 503}:
        return True
    indicators = ['captcha', 'blocked', 'access denied']
    return any(ind in html.lower() for ind in indicators)
```

## 🗄️ Database Schema
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   authors   │     │   quotes    │     │    tags     │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │────<│ id (PK)     │>────│ id (PK)     │
│ name        │     │ text        │     │ name        │
│ created_at  │     │ author_id   │     └─────────────┘
└─────────────┘     │ scraped_at  │            │
                    └─────────────┘            │
                           │                   │
                           └───────┬───────────┘
                                   │
                           ┌───────────────┐
                           │  quote_tags   │
                           ├───────────────┤
                           │ quote_id (FK) │
                           │ tag_id (FK)   │
                           └───────────────┘
```

### Sample Queries
```sql
-- Get all quotes by an author
SELECT q.text, a.name 
FROM quotes q 
JOIN authors a ON q.author_id = a.id 
WHERE a.name LIKE '%Einstein%';

-- Get quotes by tag
SELECT q.text, a.name
FROM quotes q
JOIN authors a ON q.author_id = a.id
JOIN quote_tags qt ON q.id = qt.quote_id
JOIN tags t ON qt.tag_id = t.id
WHERE t.name = 'love';

-- Top authors by quote count
SELECT a.name, COUNT(q.id) as count
FROM authors a
JOIN quotes q ON a.id = q.author_id
GROUP BY a.id
ORDER BY count DESC
LIMIT 5;
```

## 🎯 Skills Demonstrated

### Web Scraping
- HTTP requests with custom headers
- HTML parsing with BeautifulSoup
- CSS selectors and DOM traversal
- Pagination handling
- JavaScript rendering with Selenium

### Anti-Bot Techniques
- User-agent rotation
- Request throttling
- Exponential backoff
- CAPTCHA/block detection
- Browser fingerprint masking

### Database Management
- SQLite database design
- Normalized schema with foreign keys
- Many-to-many relationships
- CRUD operations
- SQL queries with JOINs

### Python Best Practices
- Virtual environments
- Requirements management
- Modular code organization
- Error handling
- Logging

### Automation & DevOps
- Headless browser automation
- Chrome WebDriver configuration
- Cross-platform compatibility

## 📊 Sample Output

### Scraping Statistics
```
============================================================
SCRAPING SUMMARY
============================================================
Pages Scraped:    10
Quotes Added:     100
Duplicates:       0
Database:         data/quotes.db

==================================================
DATABASE STATISTICS
==================================================
Total Quotes:    100
Total Authors:   50
Total Tags:      137

Top 5 Authors:
  - Albert Einstein: 10 quotes
  - J.K. Rowling: 9 quotes
  - Marilyn Monroe: 7 quotes
  - Mark Twain: 6 quotes
  - Dr. Seuss: 6 quotes

Top 10 Tags:
  - love: 14 uses
  - life: 13 uses
  - inspirational: 13 uses
  - humor: 12 uses
  - books: 11 uses
```

### Sample JSON Output
```json
[
  {
    "text": "The world as we have created it is a process of our thinking.",
    "author": "Albert Einstein",
    "tags": ["change", "deep-thoughts", "thinking", "world"]
  },
  {
    "text": "It is our choices, Harry, that show what we truly are.",
    "author": "J.K. Rowling",
    "tags": ["abilities", "choices"]
  }
]
```

## 🔮 Future Enhancements

- [ ] Proxy rotation support
- [ ] Async scraping with aiohttp
- [ ] Redis caching
- [ ] Docker containerization
- [ ] REST API for scraped data
- [ ] Scheduled scraping with APScheduler
- [ ] Cloud deployment (AWS/GCP)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Nitin N**

- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

⭐ If you found this project helpful, please give it a star!