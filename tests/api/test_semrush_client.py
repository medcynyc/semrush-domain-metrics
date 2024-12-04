"""Tests for SEMrush API V3 client - Domain Metrics specific."""

import os
import pytest
import httpx
from unittest.mock import patch, Mock
from src.exceptions.errors import APIError
from src.api.semrush_client import SEMrushAPIV3Client

def test_client_initialization(api_key, mock_env_without_api_key):
    """Test client initialization with API key."""
    # Test valid initialization
    client = SEMrushAPIV3Client(api_key=api_key)
    assert client.api_key == api_key
    assert client.database == "us"
    
    # Test initialization without API key
    with pytest.raises(APIError):
        client = SEMrushAPIV3Client(api_key=None)
        client.get_domain_overview("example.com")  # This will trigger the error

def test_domain_overview(semrush_client, test_domain, mock_client):
    """Test domain overview endpoint."""
    response = semrush_client.get_domain_overview(test_domain)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get("result") == "success"
    
    # Verify expected data fields are present
    expected_fields = [
        "organic_traffic",
        "paid_traffic",
        "organic_keywords",
        "paid_keywords"
    ]
    for field in expected_fields:
        assert field in response, f"Missing field: {field}"

def test_domain_metrics(semrush_client, test_domain, mock_client):
    """Test domain metrics endpoint."""
    response = semrush_client.get_domain_metrics(test_domain)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get("result") == "success"
    
    # Verify metrics-specific fields
    expected_fields = [
        "domain_authority",
        "backlink_count",
        "referring_domains"
    ]
    for field in expected_fields:
        assert field in response, f"Missing field: {field}"

def test_backlinks_overview(semrush_client, test_domain, mock_client):
    """Test backlinks overview endpoint."""
    response = semrush_client.get_backlinks_overview(test_domain)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get("result") == "success"
    
    # Verify backlink-specific fields
    expected_fields = [
        "backlinks",
        "referring_domains",
        "referring_ips",
        "referring_subnets"
    ]
    for field in expected_fields:
        assert field in response, f"Missing field: {field}"

def test_keywords_overview(semrush_client, test_domain, mock_client):
    """Test keywords overview endpoint."""
    response = semrush_client.get_keywords_overview(test_domain)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get("result") == "success"

def test_domain_comparison(semrush_client, test_domain, mock_client):
    """Test domain comparison endpoint."""
    competitor_domain = "example.com"
    response = semrush_client.get_domain_comparison(test_domain, competitor_domain)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get("result") == "success"

def test_related_phrases(semrush_client, mock_client):
    """Test related phrases endpoint."""
    test_phrase = "jewelry"
    response = semrush_client.get_related_phrases(test_phrase)
    assert response is not None
    assert isinstance(response, dict)
    assert response.get("result") == "success"

def test_error_handling(mock_client, monkeypatch):
    """Test error handling with invalid domain."""
    def mock_error_request(*args, **kwargs):
        mock_resp = Mock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_resp.url = "https://api.semrush.com/analytics/v3/test"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=None,
            response=mock_resp
        )
        return mock_resp

    monkeypatch.setattr(httpx.Client, "request", mock_error_request)
    
    client = SEMrushAPIV3Client(api_key="invalid_key")
    with pytest.raises(APIError):
        client.get_domain_overview("example.com")

def test_rate_limiting(semrush_client, test_domain, monkeypatch):
    """Test rate limiting functionality."""
    request_count = 0
    
    def mock_rate_limit_request(*args, **kwargs):
        nonlocal request_count
        request_count += 1
        mock_resp = Mock()
        mock_resp.url = "https://api.semrush.com/analytics/v3/test"
        
        if request_count > 2:  # Rate limit after 2 requests
            mock_resp.status_code = 429
            mock_resp.text = "Rate limit exceeded"
            mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "429 Too Many Requests",
                request=None,
                response=mock_resp
            )
        else:
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"result": "success"}
            mock_resp.raise_for_status.return_value = None
        return mock_resp

    monkeypatch.setattr(httpx.Client, "request", mock_rate_limit_request)
    
    # First two requests should succeed
    for _ in range(2):
        response = semrush_client.get_domain_overview(test_domain)
        assert response is not None
        assert response.get("result") == "success"
    
    # Third request should hit rate limit
    with pytest.raises(APIError) as exc:
        semrush_client.get_domain_overview(test_domain)
    assert "429" in str(exc.value)

def test_invalid_domain_format(semrush_client):
    """Test with invalid domain format."""
    with pytest.raises(APIError):
        semrush_client.get_domain_overview("not-a-valid-domain")

