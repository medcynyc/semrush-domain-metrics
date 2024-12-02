"""SEMrush API V3 client implementation for domain metrics."""

import os
from typing import Optional, Dict, Any, List, Union
import httpx
from datetime import datetime
from .rate_limiter import rate_limit_manager
from src.exceptions.errors import APIError
from src.config.logging import get_logger
from src.config.settings import settings

logger = get_logger(__name__)

class SEMrushAPIV3Client:
    """Client for interacting with SEMrush Analytics API V3."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = 'https://api.semrush.com',
        database: str = 'us'
    ):
        """Initialize SEMrush API V3 client."""
        self.api_key = api_key or settings.SEMRUSH_API_KEY
        if not self.api_key:
            raise APIError("SEMRUSH_API_KEY not provided or found in environment")
        
        self.base_url = base_url
        self.database = database
        self.client = httpx.Client(timeout=30.0)
        
        # Domain-specific endpoint rate limits
        self.endpoint_limits = {
            'analytics': {'per_second': 1, 'per_minute': 45},
            'backlinks': {'per_second': 1, 'per_minute': 45}
        }

    def get_domain_overview(self, domain: str) -> Dict[str, Any]:
        """
        Get domain overview analytics.
        
        Args:
            domain: Domain to analyze
        
        Returns:
            Domain overview data including traffic and keywords
        """
        endpoint = '/analytics/v1/domain_ranks'
        params = {
            'key': self.api_key,
            'target': domain,
            'database': self.database,
            'display_date': 'yesterday',
            'display_limit': 100,
            'display_sort': 'tr_count_desc',
            'export_columns': (
                'Ot,Oc,Or,Ob,Op,Od'  # SEMrush column codes
            )
        }
        
        return self._make_request(endpoint, params)

    def get_domain_metrics(self, domain: str) -> Dict[str, Any]:
        """
        Get detailed domain metrics.
        
        Args:
            domain: Domain to analyze
        
        Returns:
            Detailed domain metrics including authority and backlinks
        """
        endpoint = '/analytics/v1/domain_organic'
        params = {
            'key': self.api_key,
            'target': domain,
            'database': self.database,
            'display_date': 'yesterday',
            'export_columns': (
                'Rk,Kt,Po,Cp,Ur,Tr'  # SEMrush column codes
            )
        }
        
        return self._make_request(endpoint, params)

    def get_backlinks_overview(self, domain: str) -> Dict[str, Any]:
        """
        Get domain backlinks overview.
        
        Args:
            domain: Domain to analyze
        
        Returns:
            Backlinks overview data
        """
        endpoint = '/backlinks/v1/domain_backlinks'
        params = {
            'key': self.api_key,
            'target': domain,
            'database': self.database,
            'export_columns': (
                'source_url,anchor,external,nofollow'  # SEMrush column codes
            )
        }
        
        return self._make_request(endpoint, params)

    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Make API request with rate limiting.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            method: HTTP method
        
        Returns:
            API response data
        
        Raises:
            APIError: If the request fails
        """
        # Apply rate limiting
        endpoint_key = endpoint.split('/')[1]  # Get 'analytics' or 'backlinks'
        rate_limiter = self._get_rate_limiter(endpoint_key)
        rate_limiter.wait()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.client.request(method, url, params=params)
            
            # Log full request details in debug mode
            logger.debug(f"Request URL: {response.url}")
            logger.debug(f"Request params: {params}")
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response text: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_text = str(e)
            try:
                error_json = e.response.json()
                if isinstance(error_json, dict):
                    error_text = error_json.get('error', {}).get('message', str(e))
            except Exception:
                pass
            
            raise APIError(
                f"API request failed: {error_text}",
                status_code=e.response.status_code,
                response_text=e.response.text
            )
        except Exception as e:
            raise APIError(f"Request failed: {str(e)}")

    def _get_rate_limiter(self, endpoint: str):
        """Get rate limiter for specific endpoint."""
        limits = self.endpoint_limits.get(endpoint, {})
        return rate_limit_manager.get_limiter(
            endpoint,
            calls_per_second=limits.get('per_second', 1),
            calls_per_minute=limits.get('per_minute', 45)
        )

    def __del__(self):
        """Cleanup client session."""
        self.client.close()
