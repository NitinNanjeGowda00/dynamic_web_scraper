import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com"

response = requests.get(url)
print(f"Status Code: {response.status_code}")
print(f"Content Length: {len(response.text)}")

soup = BeautifulSoup(response.text, 'lxml')

# Check what we're getting
print("\n--- Checking HTML Structure ---")

# Find all divs with class 'quote'
quotes = soup.find_all('div', class_='quote')
print(f"Found {len(quotes)} quote divs")

# If no quotes found, let's see what divs exist
if len(quotes) == 0:
    print("\nAll div classes found on page:")
    all_divs = soup.find_all('div')
    classes = set()
    for div in all_divs:
        if div.get('class'):
            classes.add(tuple(div.get('class')))
    for c in list(classes)[:20]:
        print(f"  - {c}")

# If quotes found, print first one
if len(quotes) > 0:
    print("\n--- First Quote Structure ---")
    print(quotes[0].prettify()[:500])