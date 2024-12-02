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
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json_data = json_data or {
                "result": "success",
                "organic_traffic": 5000,
                "paid_traffic": 1000,
                "organic_keywords": 500,
                "paid_keywords": 100,
                "traffic_cost": 2500.50,
                "organic_traffic_cost": 2000.00,
                "domain_authority": 45,
                "backlink_count": 1000,
                "referring_domains": 200,
                "backlinks": 5000,
                "referring_ips": 180,
                "referring_subnets": 150
            }
            self.url = "https://api.semrush.com/test"
            self.text = str(self._json_data)
        
        def json(self):
            return self._json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"{self.status_code} Error",
                    request=None,
                    response=self
                )
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
        return mock_response()
    
    monkeypatch.setattr(httpx.Client, "request", mock_request)
