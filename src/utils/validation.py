"""Validation utilities for SEMrush data."""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import ipaddress
from urllib.parse import urlparse

from logging_setup import get_logger

logger = get_logger(__name__)

class ValidationHelper:
    """Provides validation methods for various data types."""
    
    def __init__(self):
        """Initialize validation helper."""
        # Compile regex patterns
        self.patterns = {
            'domain': re.compile(
                r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
            ),
            'email': re.compile(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            ),
            'url': re.compile(
                r'^https?:\/\/'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$',
                re.IGNORECASE
            )
        }
        
        # Define validation ranges
        self.ranges = {
            'position': (1, 100),
            'search_volume': (0, 1000000000),
            'traffic': (0, 1000000000),
            'percentage': (0, 100),
            'year': (2000, datetime.now().year + 1)
        }

    def validate_domain(self, domain: str) -> bool:
        """
        Validate domain name format.
        
        Args:
            domain: Domain name to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not domain:
                return False
            return bool(self.patterns['domain'].match(domain.lower()))
        except Exception as e:
            logger.error(f"Domain validation error for '{domain}': {str(e)}")
            return False

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not url:
                return False
            return bool(self.patterns['url'].match(url))
        except Exception as e:
            logger.error(f"URL validation error for '{url}': {str(e)}")
            return False

    def validate_numeric_range(
        self,
        value: Union[int, float],
        range_key: str
    ) -> bool:
        """
        Validate numeric value within defined range.
        
        Args:
            value: Value to validate
            range_key: Key for range definition
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if range_key not in self.ranges:
                logger.warning(f"Unknown range key: {range_key}")
                return True
                
            min_val, max_val = self.ranges[range_key]
            return min_val <= value <= max_val
            
        except TypeError as e:
            logger.error(f"Numeric range validation error for '{value}': {str(e)}")
            return False

    def validate_date_format(
        self,
        date_str: str,
        format_str: str = '%Y-%m-%d'
    ) -> bool:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            format_str: Expected date format
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False

    def validate_keyword_data(
        self,
        data: Dict[str, Any],
        required_fields: Optional[List[str]] = None
    ) -> List[str]:
        """
        Validate keyword data structure from SEMrush API V3.
        
        Args:
            data: Keyword data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if required_fields is None:
            required_fields = ['Keyword', 'Position', 'SearchVolume', 'CPC', 'Competition', 'NumberOfResults', 'Trends', 'URL', 'Traffic', 'TrafficCost']
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate specific fields
        if 'Position' in data and data['Position'] is not None:
            if not self.validate_numeric_range(data['Position'], 'position'):
                errors.append(f"Invalid position value: {data['Position']}")
        
        if 'SearchVolume' in data and data['SearchVolume'] is not None:
            if not self.validate_numeric_range(data['SearchVolume'], 'search_volume'):
                errors.append(f"Invalid search volume: {data['SearchVolume']}")
        
        if 'CPC' in data and data['CPC'] is not None:
            if not isinstance(data['CPC'], (int, float)) or data['CPC'] < 0:
                errors.append(f"Invalid CPC value: {data['CPC']}")
        
        if 'Competition' in data and data['Competition'] is not None:
            if not self.validate_numeric_range(data['Competition'], 'percentage'):
                errors.append(f"Invalid competition value: {data['Competition']}")
        
        if 'NumberOfResults' in data and data['NumberOfResults'] is not None:
            if not isinstance(data['NumberOfResults'], int) or data['NumberOfResults'] < 0:
                errors.append(f"Invalid number of results: {data['NumberOfResults']}")
        
        # 'Trends' would typically be a list of 12 numbers, but this isn't enforced here as formats can vary
        if 'URL' in data and data['URL']:
            if not self.validate_url(data['URL']):
                errors.append(f"Invalid URL: {data['URL']}")
        
        # Traffic and TrafficCost should be non-negative numbers
        for field in ['Traffic', 'TrafficCost']:
            if field in data and data[field] is not None:
                if not self.validate_numeric_range(data[field], 'traffic'):
                    errors.append(f"Invalid {field} value: {data[field]}")
        
        return errors

    def validate_metrics_data(
        self,
        data: Dict[str, Any],
        required_fields: Optional[List[str]] = None
    ) -> List[str]:
        """
        Validate metrics data structure from SEMrush API V3.
        
        Args:
            data: Metrics data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if required_fields is None:
            required_fields = ['Date']
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate date field
        if 'Date' in data and data['Date']:
            if isinstance(data['Date'], str):
                if not self.validate_date_format(data['Date'], '%Y%m%d'):  # SEMrush uses YYYYMMDD format
                    errors.append(f"Invalid date format: {data['Date']}")
            elif not isinstance(data['Date'], (datetime, date)):
                errors.append("Date must be string or datetime object")
        
        # Validate traffic fields
        traffic_fields = ['OrganicTraffic', 'PaidTraffic', 'TotalTraffic']
        for field in traffic_fields:
            if field in data and data[field] is not None:
                if not self.validate_numeric_range(data[field], 'traffic'):
                    errors.append(f"Invalid {field} value: {data[field]}")
        
        # Validate percentage fields (Visibility is a percentage in SEMrush)
        percentage_fields = ['Visibility']
        for field in percentage_fields:
            if field in data and data[field] is not None:
                if not self.validate_numeric_range(data[field], 'percentage'):
                    errors.append(f"Invalid {field} value: {data[field]}")
        
        return errors

    def validate_competitor_data(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate competitor data structure.
        
        This method remains largely the same as the fields for competitors haven't changed significantly in V3.
        
        Args:
            data: Competitor data dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields
        required_fields = ['CompetitorDomain', 'Date']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate domain
        if 'CompetitorDomain' in data and data['CompetitorDomain']:
            if not self.validate_domain(data['CompetitorDomain']):
                errors.append(f"Invalid competitor domain: {data['CompetitorDomain']}")
        
        # Validate metrics
        metric_fields = {
            'commonKeywords': 'traffic',
            'marketShare': 'percentage',
            'visibility': 'percentage'
        }
        
        for field, range_key in metric_fields.items():
            if field in data and data[field] is not None:
                if not self.validate_numeric_range(data[field], range_key):
                    errors.append(f"Invalid {field} value: {data[field]}")
        
        return errors

# Global validation helper instance
validation_helper = ValidationHelper()
