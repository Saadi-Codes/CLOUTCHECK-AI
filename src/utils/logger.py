"""
Logging configuration for CloutCheck AI pipeline.
Provides structured logging with file rotation and progress tracking.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

from src.config import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional specific log file name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set level
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"cloutcheck_{timestamp}.log"
    
    log_path = LOGS_DIR / log_file
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


class ProgressLogger:
    """
    Simple progress logger for tracking long-running operations.
    """
    
    def __init__(self, logger: logging.Logger, total: int, description: str = "Processing"):
        self.logger = logger
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
        
    def update(self, n: int = 1):
        """Update progress by n items"""
        self.current += n
        
        # Log every 10% or at completion
        progress = (self.current / self.total) * 100
        if progress % 10 < (n / self.total) * 100 or self.current == self.total:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = self.current / elapsed if elapsed > 0 else 0
            
            if self.current < self.total:
                eta = (self.total - self.current) / rate if rate > 0 else 0
                self.logger.info(
                    f"{self.description}: {self.current}/{self.total} "
                    f"({progress:.1f}%) - ETA: {eta:.0f}s"
                )
            else:
                self.logger.info(
                    f"{self.description}: Complete! "
                    f"({self.total} items in {elapsed:.1f}s, {rate:.1f} items/s)"
                )


# Default logger for the pipeline
default_logger = setup_logger("cloutcheck")


def log_section(logger: logging.Logger, title: str, char: str = "="):
    """Log a section header for better readability"""
    separator = char * 70
    logger.info("")
    logger.info(separator)
    logger.info(f"  {title.upper()}")
    logger.info(separator)


def log_results(logger: logging.Logger, results: dict):
    """Log dictionary results in a formatted way"""
    logger.info("Results:")
    for key, value in results.items():
        if isinstance(value, float):
            logger.info(f"  {key}: {value:.4f}")
        else:
            logger.info(f"  {key}: {value}")
