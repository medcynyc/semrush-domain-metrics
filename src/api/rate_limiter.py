"""Rate limiting implementation for API requests."""

import time
from typing import Optional, Dict
import threading
from datetime import datetime
import queue
import logging
from src.config.logging import get_logger

logger = get_logger(__name__)

class RateLimiter:
    """Thread-safe rate limiter for API requests."""
    
    def __init__(
        self,
        calls_per_second: int = 10,
        calls_per_minute: int = 600,
        max_retries: int = 3
    ):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls allowed per second (adjusted to SEMrush API V3 limits)
            calls_per_minute: Maximum calls allowed per minute (adjusted to SEMrush API V3 limits)
            max_retries: Maximum number of retries when rate limit is hit
        """
        self.calls_per_second = calls_per_second
        self.calls_per_minute = calls_per_minute
        self.max_retries = max_retries
        
        # Tracking queues for different time windows
        self.second_queue = queue.Queue()
        self.minute_queue = queue.Queue()
        
        # Thread lock for synchronization
        self._lock = threading.Lock()

    def _clean_queue(self, q: queue.Queue, interval: float) -> int:
        """
        Clean expired timestamps from a queue.
        
        Args:
            q: Queue to clean
            interval: Time interval in seconds
            
        Returns:
            Number of valid items remaining in queue
        """
        current_time = time.time()
        valid_times = []
        
        # Empty the queue and keep valid timestamps
        while not q.empty():
            timestamp = q.get()
            if current_time - timestamp <= interval:
                valid_times.append(timestamp)
        
        # Put back valid timestamps
        for timestamp in valid_times:
            q.put(timestamp)
            
        return len(valid_times)

    def _wait_if_needed(self, current_count: int, limit: int, interval: float) -> None:
        """
        Wait if current count exceeds limit.
        
        Args:
            current_count: Current number of requests
            limit: Maximum allowed requests
            interval: Time interval in seconds
        """
        if current_count >= limit:
            sleep_time = max(0, interval - (time.time() - self.second_queue.queue[0]))
            if sleep_time > 0:
                logger.debug(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

    def wait(self) -> None:
        """
        Wait if necessary to comply with rate limits.
        
        Raises:
            RuntimeError: If rate limit cannot be satisfied after max retries
        """
        with self._lock:
            retries = 0
            while retries < self.max_retries:
                # Clean and check second-based queue
                second_count = self._clean_queue(self.second_queue, 1.0)
                if second_count >= self.calls_per_second:
                    self._wait_if_needed(second_count, self.calls_per_second, 1.0)
                
                # Clean and check minute-based queue
                minute_count = self._clean_queue(self.minute_queue, 60.0)
                if minute_count >= self.calls_per_minute:
                    self._wait_if_needed(minute_count, self.calls_per_minute, 60.0)
                
                # If both checks pass, record the request
                current_time = time.time()
                if second_count < self.calls_per_second and minute_count < self.calls_per_minute:
                    self.second_queue.put(current_time)
                    self.minute_queue.put(current_time)
                    return
                
                retries += 1
                time.sleep(1)  # Wait before retry
            
            raise RuntimeError("Failed to satisfy rate limit after maximum retries")

class RateLimitManager:
    """Manages multiple rate limiters for different API endpoints."""
    
    def __init__(self):
        """Initialize rate limit manager."""
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    def get_limiter(
        self,
        endpoint: str,
        calls_per_second: Optional[int] = None,
        calls_per_minute: Optional[int] = None
    ) -> RateLimiter:
        """
        Get or create a rate limiter for an endpoint.
        
        Args:
            endpoint: API endpoint identifier
            calls_per_second: Optional override for calls per second
            calls_per_minute: Optional override for calls per minute
            
        Returns:
            RateLimiter instance for the endpoint
        """
        with self._lock:
            if endpoint not in self._limiters:
                self._limiters[endpoint] = RateLimiter(
                    calls_per_second=calls_per_second or 10,
                    calls_per_minute=calls_per_minute or 600
                )
            return self._limiters[endpoint]

    def wait_for_endpoint(self, endpoint: str) -> None:
        """
        Wait for rate limit on specific endpoint.
        
        Args:
            endpoint: API endpoint identifier
        """
        limiter = self.get_limiter(endpoint)
        limiter.wait()

# Global rate limit manager instance
rate_limit_manager = RateLimitManager()
