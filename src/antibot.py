import random
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Configuration for a proxy server."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to requests proxy format."""
        if self.username and self.password:
            proxy_url = f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            proxy_url = f"{self.protocol}://{self.host}:{self.port}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }


class UserAgentRotator:
    """Manages rotation of user agents to mimic different browsers."""
    
    # Comprehensive list of real user agents (updated 2024)
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Chrome on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Firefox on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        
        # Safari on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Firefox on Linux
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    def __init__(self, custom_agents: List[str] = None):
        """Initialize with optional custom user agents."""
        self.user_agents = custom_agents if custom_agents else self.USER_AGENTS.copy()
        self.current_index = 0
        self.last_used = None
    
    def get_random(self) -> str:
        """Get a random user agent."""
        agent = random.choice(self.user_agents)
        self.last_used = agent
        return agent
    
    def get_next(self) -> str:
        """Get next user agent in rotation."""
        agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        self.last_used = agent
        return agent
    
    def get_browser_headers(self, user_agent: str = None) -> Dict[str, str]:
        """Get complete browser headers matching the user agent."""
        if user_agent is None:
            user_agent = self.get_random()
        
        # Base headers
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
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
        
        # Add browser-specific headers
        if "Chrome" in user_agent:
            headers["Sec-Ch-Ua"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers["Sec-Ch-Ua-Mobile"] = "?0"
            headers["Sec-Ch-Ua-Platform"] = '"Windows"' if "Windows" in user_agent else '"macOS"'
        
        return headers


class ProxyRotator:
    """Manages rotation of proxy servers."""
    
    def __init__(self, proxies: List[ProxyConfig] = None):
        """Initialize with optional list of proxies."""
        self.proxies = proxies if proxies else []
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_stats = {}  # Track success/failure per proxy
    
    def add_proxy(self, proxy: ProxyConfig):
        """Add a proxy to the pool."""
        self.proxies.append(proxy)
        self.proxy_stats[f"{proxy.host}:{proxy.port}"] = {"success": 0, "failure": 0}
    
    def add_proxies_from_list(self, proxy_list: List[str]):
        """
        Add proxies from a list of strings.
        Format: "host:port" or "host:port:username:password"
        """
        for proxy_str in proxy_list:
            parts = proxy_str.strip().split(":")
            if len(parts) >= 2:
                proxy = ProxyConfig(
                    host=parts[0],
                    port=int(parts[1]),
                    username=parts[2] if len(parts) > 2 else None,
                    password=parts[3] if len(parts) > 3 else None
                )
                self.add_proxy(proxy)
    
    def get_random(self) -> Optional[Dict[str, str]]:
        """Get a random working proxy."""
        available = [p for p in self.proxies 
                    if f"{p.host}:{p.port}" not in self.failed_proxies]
        
        if not available:
            logger.warning("No available proxies!")
            return None
        
        proxy = random.choice(available)
        return proxy.to_dict()
    
    def get_next(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation."""
        if not self.proxies:
            return None
        
        # Skip failed proxies
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if f"{proxy.host}:{proxy.port}" not in self.failed_proxies:
                return proxy.to_dict()
            
            attempts += 1
        
        logger.warning("All proxies have failed!")
        return None
    
    def mark_failed(self, proxy_dict: Dict[str, str]):
        """Mark a proxy as failed."""
        # Extract host:port from proxy URL
        proxy_url = proxy_dict.get("http", "")
        if "@" in proxy_url:
            host_port = proxy_url.split("@")[1]
        else:
            host_port = proxy_url.replace("http://", "").replace("https://", "")
        
        self.failed_proxies.add(host_port)
        if host_port in self.proxy_stats:
            self.proxy_stats[host_port]["failure"] += 1
        
        logger.warning(f"Proxy marked as failed: {host_port}")
    
    def mark_success(self, proxy_dict: Dict[str, str]):
        """Mark a proxy request as successful."""
        proxy_url = proxy_dict.get("http", "")
        if "@" in proxy_url:
            host_port = proxy_url.split("@")[1]
        else:
            host_port = proxy_url.replace("http://", "").replace("https://", "")
        
        if host_port in self.proxy_stats:
            self.proxy_stats[host_port]["success"] += 1
    
    def reset_failed(self):
        """Reset failed proxies list."""
        self.failed_proxies.clear()
        logger.info("Reset failed proxies list")


class RequestThrottler:
    """Manages request rate limiting with smart delays."""
    
    def __init__(self, 
                 min_delay: float = 1.0,
                 max_delay: float = 3.0,
                 requests_per_minute: int = 20):
        """
        Initialize throttler.
        
        Args:
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            requests_per_minute: Target requests per minute
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.consecutive_errors = 0
    
    def wait(self):
        """Wait before making next request."""
        # Clean old request times (older than 1 minute)
        cutoff = datetime.now() - timedelta(minutes=1)
        self.request_times = [t for t in self.request_times if t > cutoff]
        
        # Check if we're over the rate limit
        if len(self.request_times) >= self.requests_per_minute:
            # Wait until oldest request is more than 1 minute old
            wait_time = 60 - (datetime.now() - self.request_times[0]).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        # Add randomized delay
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        # Increase delay if we've had errors
        error_multiplier = 1 + (self.consecutive_errors * 0.5)
        actual_delay = base_delay * error_multiplier
        
        logger.debug(f"Waiting {actual_delay:.2f}s before next request...")
        time.sleep(actual_delay)
        
        # Record this request time
        self.request_times.append(datetime.now())
    
    def record_success(self):
        """Record successful request."""
        self.consecutive_errors = 0
    
    def record_error(self):
        """Record failed request."""
        self.consecutive_errors += 1
        logger.warning(f"Consecutive errors: {self.consecutive_errors}")


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        Uses exponential backoff with jitter.
        """
        # Exponential backoff
        delay = self.base_delay * (self.exponential_base ** attempt)
        
        # Add jitter (±25%)
        jitter = delay * 0.25 * random.uniform(-1, 1)
        delay += jitter
        
        # Cap at max delay
        delay = min(delay, self.max_delay)
        
        return delay
    
    def should_retry(self, attempt: int, status_code: int = None) -> bool:
        """
        Determine if request should be retried.
        
        Args:
            attempt: Current attempt number (0-indexed)
            status_code: HTTP status code (if available)
        """
        if attempt >= self.max_retries:
            return False
        
        # Always retry on these status codes
        retryable_codes = {408, 429, 500, 502, 503, 504}
        
        if status_code and status_code in retryable_codes:
            return True
        
        # Don't retry client errors (except rate limit)
        if status_code and 400 <= status_code < 500 and status_code != 429:
            return False
        
        return True
    
    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
        
        Returns:
            Result of function or None if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return result
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.get_delay(attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed. Last error: {e}")
        
        raise last_exception


class CaptchaDetector:
    """Detects CAPTCHA challenges and bot detection pages."""
    
    # Common CAPTCHA indicators
    CAPTCHA_INDICATORS = [
        # Text patterns
        "captcha",
        "recaptcha",
        "hcaptcha",
        "challenge",
        "verify you are human",
        "verify you're human",
        "are you a robot",
        "bot detection",
        "access denied",
        "blocked",
        "unusual traffic",
        "automated access",
        "please verify",
        "security check",
        "cloudflare",
        "ddos protection",
        "incapsula",
        "distil networks",
        "imperva",
        "perimeterx",
        "datadome",
    ]
    
    # Common CAPTCHA URLs
    CAPTCHA_URLS = [
        "google.com/recaptcha",
        "hcaptcha.com",
        "challenges.cloudflare.com",
        "captcha",
        "challenge",
    ]
    
    @classmethod
    def is_captcha_page(cls, html: str, url: str = None) -> bool:
        """
        Detect if page contains CAPTCHA or bot detection.
        
        Args:
            html: Page HTML content
            url: Current URL (optional)
        
        Returns:
            True if CAPTCHA detected
        """
        html_lower = html.lower()
        
        # Check text indicators
        for indicator in cls.CAPTCHA_INDICATORS:
            if indicator in html_lower:
                logger.warning(f"CAPTCHA indicator found: '{indicator}'")
                return True
        
        # Check URL patterns
        if url:
            url_lower = url.lower()
            for pattern in cls.CAPTCHA_URLS:
                if pattern in url_lower:
                    logger.warning(f"CAPTCHA URL pattern found: '{pattern}'")
                    return True
        
        # Check for common CAPTCHA elements
        captcha_elements = [
            'id="captcha"',
            'class="captcha"',
            'id="recaptcha"',
            'class="g-recaptcha"',
            'class="h-captcha"',
            'data-sitekey=',
            'cf-turnstile',
        ]
        
        for element in captcha_elements:
            if element in html_lower:
                logger.warning(f"CAPTCHA element found: '{element}'")
                return True
        
        return False
    
    @classmethod
    def is_blocked(cls, status_code: int, html: str = None) -> bool:
        """
        Check if request was blocked.
        
        Args:
            status_code: HTTP status code
            html: Response HTML (optional)
        
        Returns:
            True if blocked
        """
        # Common block status codes
        blocked_codes = {403, 429, 503}
        
        if status_code in blocked_codes:
            logger.warning(f"Blocked status code: {status_code}")
            return True
        
        if html and cls.is_captcha_page(html):
            return True
        
        return False
    
    @classmethod
    def get_block_reason(cls, status_code: int, html: str = None) -> str:
        """Get human-readable block reason."""
        if status_code == 403:
            return "Access Forbidden - IP may be blocked"
        elif status_code == 429:
            return "Too Many Requests - Rate limited"
        elif status_code == 503:
            return "Service Unavailable - May be under protection"
        elif html and cls.is_captcha_page(html):
            return "CAPTCHA Challenge Detected"
        else:
            return "Unknown block reason"


class AntiBotScraper:
    """Complete scraper with all anti-bot features integrated."""
    
    def __init__(self,
                 use_proxies: bool = False,
                 proxy_list: List[str] = None,
                 min_delay: float = 1.0,
                 max_delay: float = 3.0,
                 max_retries: int = 3):
        """
        Initialize anti-bot scraper.
        
        Args:
            use_proxies: Whether to use proxy rotation
            proxy_list: List of proxy strings
            min_delay: Minimum delay between requests
            max_delay: Maximum delay between requests
            max_retries: Maximum retry attempts
        """
        self.ua_rotator = UserAgentRotator()
        self.proxy_rotator = ProxyRotator()
        self.throttler = RequestThrottler(min_delay, max_delay)
        self.retry_handler = RetryHandler(max_retries)
        self.use_proxies = use_proxies
        
        if proxy_list:
            self.proxy_rotator.add_proxies_from_list(proxy_list)
        
        # Statistics
        self.stats = {
            "requests": 0,
            "successful": 0,
            "failed": 0,
            "captchas": 0,
            "blocks": 0,
        }
    
    def get_request_config(self) -> Dict:
        """Get configuration for next request."""
        config = {
            "headers": self.ua_rotator.get_browser_headers(),
            "timeout": 30,
        }
        
        if self.use_proxies:
            proxy = self.proxy_rotator.get_next()
            if proxy:
                config["proxies"] = proxy
        
        return config
    
    def print_stats(self):
        """Print scraping statistics."""
        print("\n" + "=" * 40)
        print("Scraping Statistics")
        print("=" * 40)
        print(f"Total Requests:  {self.stats['requests']}")
        print(f"Successful:      {self.stats['successful']}")
        print(f"Failed:          {self.stats['failed']}")
        print(f"CAPTCHAs Hit:    {self.stats['captchas']}")
        print(f"Blocks Hit:      {self.stats['blocks']}")
        
        if self.stats['requests'] > 0:
            success_rate = (self.stats['successful'] / self.stats['requests']) * 100
            print(f"Success Rate:    {success_rate:.1f}%")
        print("=" * 40)