import requests
from bs4 import BeautifulSoup

# Fetch page
response = requests.get("https://quotes.toscrape.com")
html = response.text

# Parse directly (same logic as parser.py)
soup = BeautifulSoup(html, 'lxml')
quote_elements = soup.find_all('div', class_='quote')

print(f"Found {len(quote_elements)} quote elements")

for i, element in enumerate(quote_elements[:3]):
    text_el = element.find('span', class_='text')
    author_el = element.find('small', class_='author')
    
    text = text_el.get_text(strip=True) if text_el else "NOT FOUND"
    author = author_el.get_text(strip=True) if author_el else "NOT FOUND"
    
    print(f"\nQuote {i+1}:")
    print(f"  Text: {text[:50]}...")
    print(f"  Author: {author}")