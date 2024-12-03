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
                "Rk": 1,  # Domain Rank
                "Or": 5000,  # Organic Traffic
                "Ot": 1000,  # Total Traffic
                "Oc": 2500.50,  # Traffic Cost
                "Ad": 45,  # Domain Authority
                "Ac": 200,  # Referring Domains
                "At": 180,  # Total Backlinks
                "FK1": "Knowledge Panel",  # Featured Snippet Type
                "FP1": 500,  # Featured Snippet Count
            }
            self.url = "https://api.semrush.com/analytics/v3/domain_ranks"
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
