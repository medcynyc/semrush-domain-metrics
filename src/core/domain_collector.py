"""Domain metrics collector implementation."""

from typing import Dict, Any, List, Optional
from datetime import datetime

from src.collectors.base import BaseCollector
from src.utils.validation import validation_helper
from src.exceptions.errors import APIError, DatabaseError

class DomainMetricsCollector(BaseCollector):
    """Collects and stores domain-level metrics from SEMrush."""
    
    def __init__(self, *args, **kwargs):
        """Initialize domain metrics collector."""
        super().__init__(*args, **kwargs)
        
        # Required columns for domain metrics table
        self.required_columns = [
            'date',
            'domain_id',
            'organic_traffic',
            'paid_traffic',
            'organic_keywords',
            'paid_keywords',
            'organic_traffic_cost',
            'paid_traffic_cost',
            'backlink_count',
            'referring_domains',
            'domain_authority'
        ]

    def validate_metrics(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate domain metrics data.
        
        Args:
            data: Metrics data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        for field in ['organic_traffic', 'organic_keywords', 'backlink_count']:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric ranges
        if 'organic_traffic' in data and data['organic_traffic'] is not None:
            if not validation_helper.validate_numeric_range(data['organic_traffic'], 'traffic'):
                errors.append(f"Invalid organic traffic value: {data['organic_traffic']}")
        
        if 'paid_traffic' in data and data['paid_traffic'] is not None:
            if not validation_helper.validate_numeric_range(data['paid_traffic'], 'traffic'):
                errors.append(f"Invalid paid traffic value: {data['paid_traffic']}")
        
        return errors

    def collect(self) -> bool:
        """
        Collect domain metrics data.
        
        Returns:
            True if collection successful, False otherwise
        """
        try:
            # Validate table schema
            if not self.validate_table_schema('semrush_domain_metrics', self.required_columns):
                return False
            
            # Get domain ID
            domain_id = self._get_or_create_domain_id()
            if not domain_id:
                return False

            # Collect metrics
            all_metrics = {}
            
            # Get organic/paid metrics
            try:
                metrics = self._retry_operation(
                    self.api_client.get_domain_metrics,
                    self.domain
                )
                all_metrics.update(metrics)
            except APIError as e:
                self.logger.error(f"Failed to get domain metrics: {str(e)}")
                return False
            
            # Get backlink metrics
            try:
                backlink_data = self._retry_operation(
                    self.api_client.get_backlinks,
                    self.domain
                )
                all_metrics.update(backlink_data)
            except APIError as e:
                self.logger.warning(f"Failed to get backlink metrics: {str(e)}")
                # Continue without backlink data
            
            # Add metadata
            all_metrics.update({
                'date': self.collection_date,
                'domain_id': domain_id
            })
            
            # Process and store metrics
            success = self._process_batch(
                [all_metrics],
                'semrush_domain_metrics',
                self.validate_metrics
            ) > 0
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to collect domain metrics: {str(e)}")
            return False

    def _get_or_create_domain_id(self) -> Optional[int]:
        """
        Get existing domain ID or create new domain entry.
        
        Returns:
            Domain ID if successful, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Try to get existing domain ID
                    cur.execute(
                        "SELECT id FROM domains WHERE domain = %s",
                        (self.domain,)
                    )
                    result = cur.fetchone()
                    
                    if result:
                        return result[0]
                    
                    # Create new domain entry
                    cur.execute(
                        "INSERT INTO domains (domain) VALUES (%s) RETURNING id",
                        (self.domain,)
                    )
                    conn.commit()
                    return cur.fetchone()[0]
                    
        except Exception as e:
            self.logger.error(f"Failed to get/create domain ID: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    collector = DomainMetricsCollector()
    success = collector.collect()
    print(f"Collection {'successful' if success else 'failed'}")
