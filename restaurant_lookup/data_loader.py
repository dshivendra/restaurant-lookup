"""
Data loading module for restaurant lookup.

This module provides functionality to load restaurant data from various sources,
following the Single Responsibility Principle.
"""

import os
import pandas as pd
import requests
from io import StringIO
from typing import Any
from interfaces import DataLoaderInterface


class CSVDataLoader(DataLoaderInterface):
    """
    Implementation of data loading functionality for CSV files.
    
    This class is responsible for loading restaurant data from CSV files
    or URLs pointing to CSV files.
    """
    
    def load_data(self, source: str) -> pd.DataFrame:
        """
        Load restaurant data from a file path or URL.
        
        Args:
            source: File path or URL to load restaurant data from
            
        Returns:
            pandas.DataFrame: DataFrame containing restaurant data
        """
        if source.startswith(('http://', 'https://')):
            return self._download_csv(source)
        else:
            # Use os.path for platform-independent path handling
            source = os.path.abspath(os.path.expanduser(source))
            return pd.read_csv(source)
    
    def _download_csv(self, url: str) -> pd.DataFrame:
        """
        Download CSV data from a URL.
        
        Args:
            url: URL to download CSV from
            
        Returns:
            pandas.DataFrame: DataFrame containing the CSV data
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            return pd.read_csv(StringIO(response.text))
        except requests.exceptions.RequestException as e:
            print(f"Error downloading CSV from {url}: {e}")
            raise
