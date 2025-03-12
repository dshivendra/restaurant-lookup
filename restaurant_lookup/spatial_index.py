"""
Spatial indexing module for efficient restaurant lookup.

This module provides functionality to create and query a spatial index
for restaurants, allowing efficient radius-based searches.
"""

import pandas as pd
from rtree import index
from datetime import datetime
from typing import List, Dict, Any, Optional

from interfaces import SpatialIndexInterface
from time_checker import TimeChecker
from distance_calculator import DistanceCalculator


class SpatialIndex(SpatialIndexInterface):
    """
    A spatial index for efficient restaurant lookup based on location.
    
    Uses R-tree for spatial indexing to achieve better than O(N*M) complexity
    when searching for restaurants within a specific radius.
    """
    
    def __init__(self, time_checker: TimeChecker, distance_calculator: DistanceCalculator):
        """
        Initialize the spatial index with dependencies.
        
        Args:
            time_checker: TimeChecker instance for checking restaurant opening hours
            distance_calculator: DistanceCalculator instance for calculating distances
        """
        # Create R-tree index with custom properties
        p = index.Property()
        p.dimension = 2  # 2D index (latitude, longitude)
        p.buffering_capacity = 10  # Tune for better performance
        self.idx = index.Index(properties=p)
        self.restaurants = {}
        self.time_checker = time_checker
        self.distance_calculator = distance_calculator
        
    def build_index(self, restaurants_df: pd.DataFrame) -> None:
        """
        Build the spatial index from a DataFrame of restaurants.
        
        Args:
            restaurants_df: DataFrame with restaurant data including id, latitude, longitude,
                           availability_radius, open_hour, close_hour, and rating.
        """
        # Store restaurant data for later retrieval
        for i, row in restaurants_df.iterrows():
            restaurant_id = row['id']
            # Store restaurant data as a dictionary for quick access
            self.restaurants[restaurant_id] = {
                'id': restaurant_id,
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'availability_radius': row['availability_radius'],
                'open_hour': row['open_hour'],
                'close_hour': row['close_hour'],
                'rating': row['rating']
            }
            
            # Add to R-tree index
            # The index uses a bounding box, so we insert a point (lat, lon) as (lat, lon, lat, lon)
            self.idx.insert(
                restaurant_id,  # Use restaurant ID as the index identifier
                (row['latitude'], row['longitude'], row['latitude'], row['longitude'])
            )
    
    def find_restaurants_in_radius(self, latitude: float, longitude: float, 
                                  current_time: Optional[datetime] = None) -> List[int]:
        """
        Find all restaurants that are within their delivery radius of the user location
        and are open at the current time.
        
        Implements the Template Method pattern by defining the skeleton of the algorithm
        and delegating specific steps to helper methods.
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            current_time: Current time as datetime object (default: None, uses current time)
            
        Returns:
            list: List of restaurant IDs that are available for delivery
        """
        # Get candidate restaurants using spatial filtering
        candidates = self._get_candidate_restaurants(latitude, longitude)
        
        # Apply detailed filtering criteria
        return self._filter_candidates(candidates, latitude, longitude, current_time)
    
    def _get_candidate_restaurants(self, latitude: float, longitude: float) -> List[int]:
        """
        Get candidate restaurants using spatial filtering.
        
        This is a helper method that implements the spatial filtering step of the algorithm.
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            
        Returns:
            List of candidate restaurant IDs
        """
        # First, create a bounding box that's large enough to encompass all possible restaurants
        # This is an optimization to reduce the number of distance calculations
        # We use 100km as a conservative maximum delivery radius
        MAX_RADIUS_KM = 100
        
        # Convert radius to approximate degrees (very rough approximation)
        # 1 degree of latitude is approximately 111 km
        radius_deg = MAX_RADIUS_KM / 111
        
        # Query the R-tree index with the bounding box
        # This gives us candidate restaurants that might be within range
        return list(self.idx.intersection(
            (latitude - radius_deg, longitude - radius_deg, 
             latitude + radius_deg, longitude + radius_deg)
        ))
    
    def _filter_candidates(self, candidates: List[int], latitude: float, longitude: float,
                          current_time: Optional[datetime] = None) -> List[int]:
        """
        Filter candidate restaurants based on distance and opening hours.
        
        This is a helper method that implements the detailed filtering step of the algorithm.
        
        Args:
            candidates: List of candidate restaurant IDs
            latitude: User's latitude
            longitude: User's longitude
            current_time: Current time as datetime object
            
        Returns:
            List of restaurant IDs that meet all criteria
        """
        available_restaurants = []
        
        # For each candidate, check if it's actually within its delivery radius
        # and if it's open at the current time
        for restaurant_id in candidates:
            restaurant = self.restaurants[restaurant_id]
            
            # Calculate actual distance
            distance = self.distance_calculator.calculate_distance(
                latitude, longitude, 
                restaurant['latitude'], restaurant['longitude']
            )
            
            # Check if user is within delivery radius and restaurant is open
            if (distance <= restaurant['availability_radius'] and 
                self.time_checker.is_open(restaurant['open_hour'], restaurant['close_hour'], current_time)):
                available_restaurants.append(restaurant_id)
        
        return available_restaurants
