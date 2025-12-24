import requests

# Force reimport by importing directly
import importlib
import src.parser
importlib.reload(src.parser)

from src.parser import QuoteParser

# Fetch page
response = requests.get("https://quotes.toscrape.com")
html = response.text

print(f"HTML Length: {len(html)}")

# Test the QuoteParser class
parser = QuoteParser(html)
quotes = parser.extract_quotes()

print(f"\nQuoteParser found: {len(quotes)} quotes")

if quotes:
    print("\nFirst 3 quotes:")
    for i, q in enumerate(quotes[:3]):
        print(f"\n{i+1}. {q['author']}: {q['text'][:50]}...")
else:
    print("\nDEBUG: Testing soup directly inside class...")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all('div', class_='quote')
    print(f"Direct soup found: {len(divs)} quote divs")