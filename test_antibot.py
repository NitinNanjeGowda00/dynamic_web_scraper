"""Test anti-bot components individually."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.antibot import (
    UserAgentRotator,
    RequestThrottler,
    RetryHandler,
    CaptchaDetector
)


def test_user_agent_rotator():
    """Test user agent rotation."""
    print("\n" + "=" * 50)
    print("Testing User Agent Rotator")
    print("=" * 50)
    
    rotator = UserAgentRotator()
    
    print("\n5 Random User Agents:")
    for i in range(5):
        ua = rotator.get_random()
        print(f"  {i+1}. {ua[:60]}...")
    
    print("\nComplete Headers for Chrome:")
    headers = rotator.get_browser_headers()
    for key, value in headers.items():
        print(f"  {key}: {value[:50]}..." if len(str(value)) > 50 else f"  {key}: {value}")


def test_throttler():
    """Test request throttler."""
    print("\n" + "=" * 50)
    print("Testing Request Throttler")
    print("=" * 50)
    
    throttler = RequestThrottler(min_delay=0.5, max_delay=1.0, requests_per_minute=60)
    
    print("\nMaking 3 throttled requests...")
    for i in range(3):
        print(f"  Request {i+1}...", end=" ")
        throttler.wait()
        print("Done!")


def test_retry_handler():
    """Test retry handler."""
    print("\n" + "=" * 50)
    print("Testing Retry Handler")
    print("=" * 50)
    
    handler = RetryHandler(max_retries=3, base_delay=0.5)
    
    print("\nDelay progression:")
    for attempt in range(4):
        delay = handler.get_delay(attempt)
        print(f"  Attempt {attempt}: {delay:.2f}s delay")
    
    print("\nShould retry (status codes):")
    test_codes = [200, 403, 429, 500, 503]
    for code in test_codes:
        should = handler.should_retry(0, code)
        print(f"  Status {code}: {'Yes' if should else 'No'}")


def test_captcha_detector():
    """Test CAPTCHA detection."""
    print("\n" + "=" * 50)
    print("Testing CAPTCHA Detector")
    print("=" * 50)
    
    # Test HTML samples
    normal_html = "<html><body><h1>Welcome</h1><p>Content here</p></body></html>"
    captcha_html = "<html><body><div class='g-recaptcha' data-sitekey='xxx'></div></body></html>"
    blocked_html = "<html><body><h1>Access Denied</h1><p>Unusual traffic detected</p></body></html>"
    
    print("\nDetection Results:")
    print(f"  Normal page: {CaptchaDetector.is_captcha_page(normal_html)}")
    print(f"  reCAPTCHA page: {CaptchaDetector.is_captcha_page(captcha_html)}")
    print(f"  Blocked page: {CaptchaDetector.is_captcha_page(blocked_html)}")
    
    print("\nBlock Detection:")
    print(f"  Status 200: {CaptchaDetector.is_blocked(200)}")
    print(f"  Status 403: {CaptchaDetector.is_blocked(403)}")
    print(f"  Status 429: {CaptchaDetector.is_blocked(429)}")
    
    print("\nBlock Reasons:")
    print(f"  403: {CaptchaDetector.get_block_reason(403)}")
    print(f"  429: {CaptchaDetector.get_block_reason(429)}")


def main():
    print("=" * 60)
    print("Anti-Bot Component Tests")
    print("=" * 60)
    
    test_user_agent_rotator()
    test_throttler()
    test_retry_handler()
    test_captcha_detector()
    
    print("\n" + "=" * 60)
    print("All Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()