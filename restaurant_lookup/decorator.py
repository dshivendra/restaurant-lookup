"""
Decorator pattern implementation for enhancing spatial index functionality.

This module provides decorators that add functionality to spatial indexes
without modifying their core implementation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from interfaces import SpatialIndexInterface


class CachingSpatialIndex(SpatialIndexInterface):
    """
    Decorator that adds caching to a spatial index.
    
    This class follows the Decorator pattern to add caching functionality
    to any implementation of SpatialIndexInterface without modifying it.
    """
    
    def __init__(self, spatial_index: SpatialIndexInterface, cache_size: int = 1000):
        """
        Initialize the decorator with the spatial index to decorate.
        
        Args:
            spatial_index: The spatial index to decorate
            cache_size: Maximum number of results to cache (default: 1000)
        """
        self.spatial_index = spatial_index
        self.cache = {}
        self.cache_size = cache_size
        self.cache_hits = 0
        self.cache_misses = 0
    
    def build_index(self, restaurants_data: Any) -> None:
        """
        Build the spatial index from restaurant data.
        
        Args:
            restaurants_data: Data containing restaurant information
        """
        # Clear the cache when rebuilding the index
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Delegate to the decorated spatial index
        self.spatial_index.build_index(restaurants_data)
    
    def find_restaurants_in_radius(self, latitude: float, longitude: float, 
                                  current_time: Optional[datetime] = None) -> List[int]:
        """
        Find restaurants within their delivery radius of the given location
        and open at the specified time, with caching.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            current_time: Time to check if restaurants are open (default: current time)
            
        Returns:
            List of restaurant IDs that are available for delivery
        """
        # Create a cache key from the parameters
        # For current_time, we use the hour and minute to allow for some cache hits
        # even if the seconds are different
        if current_time is None:
            time_key = None
        else:
            time_key = f"{current_time.hour}:{current_time.minute}"
        
        cache_key = (round(latitude, 4), round(longitude, 4), time_key)
        
        # Check if the result is in the cache
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        # If not, delegate to the decorated spatial index
        self.cache_misses += 1
        result = self.spatial_index.find_restaurants_in_radius(latitude, longitude, current_time)
        
        # Store the result in the cache
        if len(self.cache) >= self.cache_size:
            # Simple cache eviction strategy: remove a random entry
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[cache_key] = result
        return result
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get statistics about the cache performance.
        
        Returns:
            Dictionary with cache hits, misses, and size
        """
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'size': len(self.cache),
            'max_size': self.cache_size
        }


class LoggingSpatialIndex(SpatialIndexInterface):
    """
    Decorator that adds logging to a spatial index.
    
    This class follows the Decorator pattern to add logging functionality
    to any implementation of SpatialIndexInterface without modifying it.
    """
    
    def __init__(self, spatial_index: SpatialIndexInterface, log_file: str = None):
        """
        Initialize the decorator with the spatial index to decorate.
        
        Args:
            spatial_index: The spatial index to decorate
            log_file: Path to log file (default: None, logs to console)
        """
        self.spatial_index = spatial_index
        self.log_file = log_file
        self.query_count = 0
    
    def _log(self, message: str) -> None:
        """
        Log a message.
        
        Args:
            message: Message to log
        """
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        else:
            print(message)
    
    def build_index(self, restaurants_data: Any) -> None:
        """
        Build the spatial index from restaurant data, with logging.
        
        Args:
            restaurants_data: Data containing restaurant information
        """
        self._log(f"Building spatial index with {len(restaurants_data)} restaurants")
        self.query_count = 0
        
        # Delegate to the decorated spatial index
        self.spatial_index.build_index(restaurants_data)
        
        self._log("Spatial index built successfully")
    
    def find_restaurants_in_radius(self, latitude: float, longitude: float, 
                                  current_time: Optional[datetime] = None) -> List[int]:
        """
        Find restaurants within their delivery radius of the given location
        and open at the specified time, with logging.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            current_time: Time to check if restaurants are open (default: current time)
            
        Returns:
            List of restaurant IDs that are available for delivery
        """
        self.query_count += 1
        self._log(f"Query #{self.query_count}: Finding restaurants near ({latitude}, {longitude}) at {current_time}")
        
        # Delegate to the decorated spatial index
        result = self.spatial_index.find_restaurants_in_radius(latitude, longitude, current_time)
        
        self._log(f"Query #{self.query_count}: Found {len(result)} restaurants")
        return result
