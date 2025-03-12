"""
Interfaces for the restaurant lookup system.

This module defines interfaces for the restaurant lookup system
following the Interface Segregation Principle from SOLID.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, time


class SpatialIndexInterface(ABC):
    """Interface for spatial indexing implementations."""
    
    @abstractmethod
    def build_index(self, restaurants_data: Any) -> None:
        """
        Build the spatial index from restaurant data.
        
        Args:
            restaurants_data: Data containing restaurant information
        """
        pass
    
    @abstractmethod
    def find_restaurants_in_radius(self, latitude: float, longitude: float, 
                                  current_time: Optional[datetime] = None) -> List[int]:
        """
        Find restaurants within their delivery radius of the given location
        and open at the specified time.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            current_time: Time to check if restaurants are open (default: current time)
            
        Returns:
            List of restaurant IDs that are available for delivery
        """
        pass


class TimeCheckerInterface(ABC):
    """Interface for time checking implementations."""
    
    @abstractmethod
    def is_open(self, open_hour: str, close_hour: str, 
               current_time: Optional[time] = None) -> bool:
        """
        Check if a location is open at the specified time.
        
        Args:
            open_hour: Opening hour in ISO format (HH:MM:SS)
            close_hour: Closing hour in ISO format (HH:MM:SS)
            current_time: Time to check (default: current time)
            
        Returns:
            True if open, False otherwise
        """
        pass


class DistanceCalculatorInterface(ABC):
    """Interface for distance calculation implementations."""
    
    @abstractmethod
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two geographic points.
        
        Args:
            lat1, lon1: Coordinates of the first point
            lat2, lon2: Coordinates of the second point
            
        Returns:
            Distance in kilometers
        """
        pass


class DataLoaderInterface(ABC):
    """Interface for data loading implementations."""
    
    @abstractmethod
    def load_data(self, source: str) -> Any:
        """
        Load data from a source.
        
        Args:
            source: Source to load data from (file path or URL)
            
        Returns:
            Loaded data
        """
        pass


class ResultWriterInterface(ABC):
    """Interface for result writing implementations."""
    
    @abstractmethod
    def write_results(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Write results to the specified output path.
        
        Args:
            results: Results to write
            output_path: Path to write results to
        """
        pass
