import requests
from typing import Optional
from src.utils import setup_logger, get_random_user_agent, random_delay
from config.settings import REQUEST_TIMEOUT, RETRY_ATTEMPTS, BASE_URL

logger = setup_logger("scraper")


class WebScraper:
    """Web scraper for fetching web pages."""
    
    def __init__(self):
        """Initialize the scraper with a session."""
        self.session = requests.Session()
        self.base_url = BASE_URL
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Configure session with default headers."""
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        logger.info("Session configured with headers")
    
    def rotate_user_agent(self) -> None:
        """Rotate to a new random user agent."""
        new_ua = get_random_user_agent()
        self.session.headers['User-Agent'] = new_ua
        logger.debug(f"Rotated user agent to: {new_ua[:50]}...")
    
    def fetch_page(self, url: str, retry_count: int = 0) -> Optional[str]:
        """
        Fetch a web page and return its HTML content.
        
        Args:
            url: The URL to fetch
            retry_count: Current retry attempt number
            
        Returns:
            HTML content as string or None if failed
        """
        # Build full URL if relative path provided
        if url.startswith('/'):
            url = f"{self.base_url}{url}"
        
        try:
            logger.info(f"Fetching: {url}")
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched {url} (Status: {response.status_code})")
            return response.text
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error for {url}: {e}")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection Error for {url}: {e}")
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout Error for {url}: {e}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error for {url}: {e}")
        
        # Retry logic
        if retry_count < RETRY_ATTEMPTS:
            logger.info(f"Retrying... (Attempt {retry_count + 1}/{RETRY_ATTEMPTS})")
            random_delay(2, 4)
            self.rotate_user_agent()
            return self.fetch_page(url, retry_count + 1)
        
        logger.error(f"Failed to fetch {url} after {RETRY_ATTEMPTS} attempts")
        return None
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
        logger.info("Session closed")