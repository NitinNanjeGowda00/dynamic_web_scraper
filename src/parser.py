from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from src.utils import setup_logger

logger = setup_logger("parser")


class QuoteParser:
    """Parser for extracting quotes from HTML content."""
    
    def __init__(self, html_content: str):
        """Initialize parser with HTML content."""
        self.soup = BeautifulSoup(html_content, 'lxml')
    
    def extract_quotes(self) -> List[Dict[str, any]]:
        """Extract all quotes from the page."""
        quotes = []
        quote_elements = self.soup.find_all('div', class_='quote')
        
        for element in quote_elements:
            quote_data = self._parse_quote_element(element)
            if quote_data:
                quotes.append(quote_data)
        
        logger.info(f"Extracted {len(quotes)} quotes from page")
        return quotes
    
    def _parse_quote_element(self, element) -> Optional[Dict[str, any]]:
        """Parse a single quote element."""
        try:
            # Extract quote text
            text_element = element.find('span', class_='text')
            text = text_element.get_text(strip=True) if text_element else None
            
            # Remove quotation marks from beginning and end
            if text:
                text = text.strip('\u201c\u201d"')
            
            # Extract author
            author_element = element.find('small', class_='author')
            author = author_element.get_text(strip=True) if author_element else None
            
            # Extract tags
            tag_elements = element.find_all('a', class_='tag')
            tags = [tag.get_text(strip=True) for tag in tag_elements]
            
            return {
                'text': text,
                'author': author,
                'tags': tags
            }
        
        except Exception as e:
            logger.error(f"Error parsing quote element: {e}")
            return None
    
    def get_next_page_url(self) -> Optional[str]:
        """Get the URL for the next page if it exists."""
        next_button = self.soup.find('li', class_='next')
        
        if next_button:
            next_link = next_button.find('a')
            if next_link and next_link.get('href'):
                return next_link.get('href')
        
        return None