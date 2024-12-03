"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock
import httpx
from src.api.semrush_client import SEMrushAPIV3Client

@pytest.fixture
def api_key():
    """Get API key for tests."""
    return "test_api_key"

@pytest.fixture
def mock_env_without_api_key(monkeypatch):
    """Remove API key from environment for testing."""
    monkeypatch.delenv('SEMRUSH_API_KEY', raising=False)

@pytest.fixture
def test_domain():
    """Test domain to use in tests."""
    return "christinamagdolna.com"

@pytest.fixture
def mock_response():
    """Mock API response."""
    class MockResponse:
        def __init__(self, status_code=200, json_data=None, endpoint=None):
            self.status_code = status_code
            self._request = Mock()  # Add mock request
            
            # Define endpoint-specific responses
            endpoint_responses = {
                'domain_ranks': {
                    "result": "success",
                    "data": {
                        "Rk": 1,  # Domain Rank
                        "Or": 5000,  # Organic Traffic
                        "Ot": 1000,  # Total Traffic
                        "Oc": 2500.50,  # Traffic Cost
                        "Ad": 45,  # Domain Authority
                        "At": 180,  # Total Backlinks
                        "Ac": 200,  # Referring Domains
                        "FK1": "Knowledge Panel",
                        "FP1": 500
                    }
                },
                'domain_organic': {
                    "result": "success",
                    "data": {
                        "Ph": 80,  # Position History
                        "Po": 15,  # Position
                        "Nq": 1200,  # Number of Queries
                        "Cp": 2.5,  # CPC
                        "Ur": "https://example.com",  # URL
                        "Tr": 500  # Traffic
                    }
                },
                'backlinks_overview': {
                    "result": "success",
                    "data": {
                        "ascore": 85,
                        "total": 1000,
                        "domains_num": 200,
                        "urls_num": 800,
                        "ips_num": 180,
                        "ipclassc_num": 150,
                        "follows_num": 700,
                        "nofollows_num": 300
                    }
                }
            }
            
            # Get the appropriate response data
            if endpoint and endpoint in endpoint_responses:
                self._json_data = endpoint_responses[endpoint]
            else:
                self._json_data = json_data or endpoint_responses['domain_ranks']
            
            self.url = f"https://api.semrush.com/analytics/v3/{endpoint if endpoint else 'domain_ranks'}"
            self.text = str(self._json_data)
            self.headers = {}
            self.reason_phrase = "OK" if status_code == 200 else "Bad Request"
        
        def json(self):
            return self._json_data
        
        @property
        def has_redirect_location(self):
            return 'location' in self.headers
        
        @property
        def is_success(self):
            return 200 <= self.status_code < 300
        
        def raise_for_status(self):
            if self.status_code >= 400:
                message = (f"Client error '{self.status_code} {self.reason_phrase}' "
                         f"for url '{self.url}'\nFor more information check: "
                         f"https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{self.status_code}")
                raise httpx.HTTPStatusError(
                    message,
                    request=self._request,
                    response=self
                )
            return self
    return MockResponse

@pytest.fixture
def semrush_client(api_key):
    """Create SEMrush client instance."""
    client = SEMrushAPIV3Client(api_key=api_key)
    yield client
    client.client.close()  # Cleanup after tests

@pytest.fixture
def mock_client(monkeypatch, mock_response):
    """Mock httpx client."""
    def mock_request(*args, **kwargs):
        # Extract endpoint from URL
        url = args[1] if len(args) > 1 else kwargs.get('url', '')
        endpoint = None
        
        if '/analytics/v3/domain_ranks' in url:
            endpoint = 'domain_ranks'
        elif '/analytics/v3/domain_organic' in url:
            endpoint = 'domain_organic'
        elif '/analytics/v3/backlinks_overview' in url:
            endpoint = 'backlinks_overview'
            
        return mock_response(endpoint=endpoint)
    
    monkeypatch.setattr(httpx.Client, "request", mock_request)
