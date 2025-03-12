"""
Result writing module for restaurant lookup.

This module provides functionality to write restaurant lookup results to files,
following the Single Responsibility Principle.
"""

import csv
import os
from typing import List, Dict, Any
from interfaces import ResultWriterInterface


class CSVResultWriter(ResultWriterInterface):
    """
    Implementation of result writing functionality for CSV files.
    
    This class is responsible for writing restaurant lookup results to CSV files.
    """
    
    def write_results(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Write results to the specified output path.
        
        Args:
            results: List of dictionaries with 'location' and 'restaurants' keys
            output_path: Path to write results to
        """
        # Use os.path for platform-independent path handling
        output_path = os.path.abspath(os.path.expanduser(output_path))
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_path, 'w', newline='') as output_file:
            output_writer = csv.writer(output_file)
            
            for result in results:
                user_location = result['location']
                available_restaurants = result['restaurants']
                
                if available_restaurants:
                    restaurant_ids = ';'.join(map(str, available_restaurants))
                    output_writer.writerow([user_location, restaurant_ids])
                else:
                    output_writer.writerow([user_location, ""])
