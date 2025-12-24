# Force reload modules to clear cache
import importlib
import src.parser
import src.scraper
importlib.reload(src.parser)
importlib.reload(src.scraper)

from src.scraper import WebScraper
from src.parser import QuoteParser
from src.exporter import DataExporter
from src.utils import setup_logger, ensure_directory, random_delay
from config.settings import OUTPUT_DIR, LOG_DIR, BASE_URL

def main():
    # Initialize
    ensure_directory(OUTPUT_DIR)
    ensure_directory(LOG_DIR)
    logger = setup_logger("main")
    
    logger.info("=" * 50)
    logger.info("Dynamic Web Scraper Started")
    logger.info("=" * 50)
    
    # Initialize components
    scraper = WebScraper()
    exporter = DataExporter()
    all_quotes = []
    
    # Start scraping
    current_url = BASE_URL
    page_number = 1
    max_pages = 5  # Limit pages for testing
    
    try:
        while current_url and page_number <= max_pages:
            logger.info(f"Processing page {page_number}...")
            
            # Fetch page
            html_content = scraper.fetch_page(current_url)
            
            if html_content is None:
                logger.error("Failed to fetch page. Stopping.")
                break
            
            # Parse content
            parser = QuoteParser(html_content)
            quotes = parser.extract_quotes()
            all_quotes.extend(quotes)
            
            # Get next page URL
            next_page = parser.get_next_page_url()
            
            if next_page:
                current_url = f"{BASE_URL}{next_page}"
                page_number += 1
                random_delay(1, 3)  # Be polite to the server
            else:
                logger.info("No more pages to scrape")
                break
        
        # Export data
        logger.info(f"Total quotes collected: {len(all_quotes)}")
        
        if all_quotes:
            csv_path = exporter.to_csv(all_quotes)
            json_path = exporter.to_json(all_quotes)
            logger.info(f"Data exported to CSV: {csv_path}")
            logger.info(f"Data exported to JSON: {json_path}")
    
    finally:
        scraper.close()
    
    logger.info("=" * 50)
    logger.info("Scraping Complete")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()