"""Data transformation utilities for SEMrush data."""

from typing import Dict, Any, List, Union, Optional
from datetime import datetime
import re
from decimal import Decimal, InvalidOperation

from logging_setup import get_logger

logger = get_logger(__name__)

class DataTransformer:
    """Handles data transformation and normalization."""
    
    def __init__(self):
        """Initialize data transformer."""
        # Common patterns for data cleaning
        self.patterns = {
            'url': re.compile(r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'),
            'domain': re.compile(r'^([\da-z\.-]+)\.([a-z\.]{2,6})$'),
            'number': re.compile(r'^-?\d*\.?\d+$')
        }
        
        # Unit multipliers for converting string representations
        self.unit_multipliers = {
            'k': 1000,
            'm': 1000000,
            'b': 1000000000
        }

    def clean_domain(self, domain: str) -> str:
        """
        Clean and normalize domain name.
        
        Args:
            domain: Domain name to clean
            
        Returns:
            Cleaned domain name
            
        Example:
            >>> clean_domain('https://example.com/')
            'example.com'
        """
        try:
            # Remove protocol and www if present
            domain = re.sub(r'https?://', '', domain.lower())
            domain = re.sub(r'^www\.', '', domain)
            
            # Remove trailing slashes and paths
            domain = domain.split('/')[0]
            
            return domain.strip()
        except Exception as e:
            logger.warning(f"Failed to clean domain '{domain}': {str(e)}")
            return domain

    def parse_traffic_value(self, value: str) -> Optional[int]:
        """
        Parse traffic value with unit indicators (K, M, B).
        
        Args:
            value: Traffic value string
            
        Returns:
            Parsed integer value
            
        Example:
            >>> parse_traffic_value('1.5K')
            1500
        """
        try:
            if not value or value.lower() == 'n/a':
                return None
                
            # Remove any commas and spaces
            value = value.replace(',', '').replace(' ', '').lower()
            
            # Extract number and unit
            match = re.match(r'^([\d.]+)([kmb])?$', value.lower())
            if not match:
                return int(float(value))
                
            number, unit = match.groups()
            number = float(number)
            
            if unit:
                number *= self.unit_multipliers.get(unit, 1)
                
            return int(number)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse traffic value '{value}': {str(e)}")
            return None

    def parse_percentage(self, value: str) -> Optional[float]:
        """
        Parse percentage value.
        
        Args:
            value: Percentage string
            
        Returns:
            Parsed float value
            
        Example:
            >>> parse_percentage('15.5%')
            15.5
        """
        try:
            if not value or value.lower() == 'n/a':
                return None
                
            # Remove % sign and any spaces
            value = value.replace('%', '').strip()
            return float(value)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse percentage '{value}': {str(e)}")
            return None

    def parse_currency_amount(self, value: str) -> Optional[Decimal]:
        """
        Parse currency amount.
        
        Args:
            value: Currency amount string
            
        Returns:
            Parsed decimal value
            
        Example:
            >>> parse_currency_amount('$1,234.56')
            Decimal('1234.56')
        """
        try:
            if not value or value.lower() == 'n/a':
                return None
                
            # Remove currency symbols and commas
            value = re.sub(r'[$€£,]', '', value)
            return Decimal(value)
            
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Failed to parse currency amount '{value}': {str(e)}")
            return None

    def normalize_keyword_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize keyword data structure.
        
        Args:
            data: Raw keyword data dictionary
            
        Returns:
            Normalized data dictionary
        """
        normalized = {}
        
        try:
            # Normalize known fields
            if 'keyword' in data:
                normalized['keyword'] = data['keyword'].lower()
            
            if 'search_volume' in data:
                normalized['search_volume'] = self.parse_traffic_value(str(data['search_volume']))
            
            if 'position' in data:
                normalized['position'] = int(data['position']) if data['position'] else None
                
            if 'cpc' in data:
                normalized['cpc'] = self.parse_currency_amount(str(data['cpc']))
                
            if 'competition' in data:
                normalized['competition'] = self.parse_percentage(str(data['competition']))
            
            # Copy other fields as-is
            for key, value in data.items():
                if key not in normalized:
                    normalized[key] = value
                    
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to normalize keyword data: {str(e)}")
            return data

    def normalize_metrics_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize metrics data structure.
        
        Args:
            data: Raw metrics data dictionary
            
        Returns:
            Normalized data dictionary
        """
        normalized = {}
        
        try:
            # Normalize traffic metrics
            traffic_fields = ['organic_traffic', 'paid_traffic', 'total_traffic']
            for field in traffic_fields:
                if field in data:
                    normalized[field] = self.parse_traffic_value(str(data[field]))
            
            # Normalize cost metrics
            cost_fields = ['traffic_cost', 'organic_traffic_cost', 'paid_traffic_cost']
            for field in cost_fields:
                if field in data:
                    normalized[field] = self.parse_currency_amount(str(data[field]))
            
            # Normalize percentage metrics
            percentage_fields = ['market_share', 'visibility_score', 'engagement_rate']
            for field in percentage_fields:
                if field in data:
                    normalized[field] = self.parse_percentage(str(data[field]))
            
            # Copy other fields as-is
            for key, value in data.items():
                if key not in normalized:
                    normalized[key] = value
                    
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to normalize metrics data: {str(e)}")
            return data

    def format_api_parameters(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Format parameters for API requests.
        
        Args:
            params: Raw parameter dictionary
            
        Returns:
            Formatted parameter dictionary
        """
        formatted = {}
        
        try:
            for key, value in params.items():
                # Convert lists to comma-separated strings
                if isinstance(value, (list, tuple)):
                    formatted[key] = ','.join(str(v) for v in value)
                # Convert dates to required format
                elif isinstance(value, datetime):
                    formatted[key] = value.strftime('%Y-%m-%d')
                # Convert booleans to 1/0
                elif isinstance(value, bool):
                    formatted[key] = '1' if value else '0'
                else:
                    formatted[key] = str(value)
                    
            return formatted
            
        except Exception as e:
            logger.error(f"Failed to format API parameters: {str(e)}")
            return params

# Global transformer instance
data_transformer = DataTransformer()
