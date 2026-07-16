"""
BigQuery client for connecting to GCP and executing queries.
"""
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from typing import Optional, List, Dict, Any
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default project ID
DEFAULT_PROJECT = "som-nero-phi-jonc101"


class BigQueryClient:
    """Handles BigQuery connections and query execution."""
    
    def __init__(self, project: Optional[str] = None):
        """
        Initialize BigQuery client.
        
        Args:
            project: GCP project ID. If None, uses default project.
        """
        # Use provided project, or fall back to default
        project = project or os.environ.get("GOOGLE_CLOUD_PROJECT") or DEFAULT_PROJECT
        self.client = bigquery.Client(project=project)
        self.project = self.client.project
        logger.info(f"Connected to BigQuery project: {self.project}")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            pandas DataFrame with query results
        """
        logger.info(f"Executing query...")
        query_job = self.client.query(query)
        df = query_job.to_dataframe()
        logger.info(f"Retrieved {len(df)} rows")
        return df
    
    def execute_parameterized_query(
        self, 
        query: str, 
        params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Execute a parameterized query with named parameters.
        
        Args:
            query: SQL query with @param_name placeholders
            params: Dictionary of parameter names and values
            
        Returns:
            pandas DataFrame with query results
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(name, self._get_bq_type(value), value)
                for name, value in params.items()
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        return query_job.to_dataframe()
    
    def _get_bq_type(self, value: Any) -> str:
        """Infer BigQuery parameter type from Python type."""
        if isinstance(value, str):
            return "STRING"
        elif isinstance(value, int):
            return "INT64"
        elif isinstance(value, float):
            return "FLOAT64"
        elif isinstance(value, bool):
            return "BOOL"
        else:
            return "STRING"
    
    def table_exists(self, table_ref: str) -> bool:
        """Check if a table exists in BigQuery."""
        try:
            self.client.get_table(table_ref)
            return True
        except NotFound:
            return False
    
    def get_table_schema(self, table_ref: str) -> List[Dict]:
        """Get schema information for a table."""
        table = self.client.get_table(table_ref)
        return [
            {"name": field.name, "type": field.field_type, "mode": field.mode}
            for field in table.schema
        ]
    
    def preview_table(self, table_ref: str, limit: int = 5) -> pd.DataFrame:
        """Preview first N rows of a table."""
        query = f"SELECT * FROM `{table_ref}` LIMIT {limit}"
        return self.execute_query(query)
