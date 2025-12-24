import os
import random
import time
import logging
from datetime import datetime
from config.settings import USER_AGENTS, LOG_DIR

def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger instance."""
    
    # Create logs directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    log_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.log"
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_filename))
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_random_user_agent() -> str:
    """Return a random user agent string."""
    return random.choice(USER_AGENTS)


def random_delay(min_seconds: float = 1, max_seconds: float = 3) -> None:
    """Add random delay between requests to avoid detection."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def ensure_directory(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)