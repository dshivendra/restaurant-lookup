"""
Strategy pattern implementation for filtering restaurants.

This module provides different strategies for filtering restaurants,
allowing for flexibility in how restaurants are filtered.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class FilterStrategy(ABC):
    """
    Abstract base class for restaurant filtering strategies.
    
    This class follows the Strategy pattern to define a family of algorithms
    for filtering restaurants based on different criteria.
    """
    
    @abstractmethod
    def filter_restaurants(self, candidates: List[int], restaurants: Dict[int, Dict[str, Any]], 
                          user_lat: float, user_lon: float, current_time: Optional[datetime] = None) -> List[int]:
        """
        Filter restaurant candidates based on specific criteria.
        
        Args:
            candidates: List of candidate restaurant IDs
            restaurants: Dictionary of restaurant data
            user_lat: User's latitude
            user_lon: User's longitude
            current_time: Current time (default: None, uses current time)
            
        Returns:
            List of restaurant IDs that pass the filter
        """
        pass


class DistanceAndTimeFilterStrategy(FilterStrategy):
    """
    Strategy for filtering restaurants based on distance and time.
    
    This strategy filters restaurants based on whether they are within
    their delivery radius and open at the current time.
    """
    
    def __init__(self, time_checker, distance_calculator):
        """
        Initialize the strategy with dependencies.
        
        Args:
            time_checker: TimeChecker instance for checking restaurant opening hours
            distance_calculator: DistanceCalculator instance for calculating distances
        """
        self.time_checker = time_checker
        self.distance_calculator = distance_calculator
    
    def filter_restaurants(self, candidates: List[int], restaurants: Dict[int, Dict[str, Any]], 
                          user_lat: float, user_lon: float, current_time: Optional[datetime] = None) -> List[int]:
        """
        Filter restaurants based on distance and time.
        
        Args:
            candidates: List of candidate restaurant IDs
            restaurants: Dictionary of restaurant data
            user_lat: User's latitude
            user_lon: User's longitude
            current_time: Current time (default: None, uses current time)
            
        Returns:
            List of restaurant IDs that are within delivery radius and open
        """
        available_restaurants = []
        
        for restaurant_id in candidates:
            restaurant = restaurants[restaurant_id]
            
            # Calculate actual distance
            distance = self.distance_calculator.calculate_distance(
                user_lat, user_lon, 
                restaurant['latitude'], restaurant['longitude']
            )
            
            # Check if user is within delivery radius and restaurant is open
            if (distance <= restaurant['availability_radius'] and 
                self.time_checker.is_open(restaurant['open_hour'], restaurant['close_hour'], current_time)):
                available_restaurants.append(restaurant_id)
        
        return available_restaurants


class RatingFilterStrategy(FilterStrategy):
    """
    Strategy for filtering restaurants based on rating.
    
    This strategy filters restaurants based on a minimum rating threshold
    in addition to distance and time criteria.
    """
    
    def __init__(self, base_strategy, min_rating=4.0):
        """
        Initialize the strategy with dependencies.
        
        Args:
            base_strategy: Base filtering strategy to extend
            min_rating: Minimum rating threshold (default: 4.0)
        """
        self.base_strategy = base_strategy
        self.min_rating = min_rating
    
    def filter_restaurants(self, candidates: List[int], restaurants: Dict[int, Dict[str, Any]], 
                          user_lat: float, user_lon: float, current_time: Optional[datetime] = None) -> List[int]:
        """
        Filter restaurants based on rating, distance, and time.
        
        Args:
            candidates: List of candidate restaurant IDs
            restaurants: Dictionary of restaurant data
            user_lat: User's latitude
            user_lon: User's longitude
            current_time: Current time (default: None, uses current time)
            
        Returns:
            List of restaurant IDs that meet all criteria
        """
        # First apply base filtering (distance and time)
        base_results = self.base_strategy.filter_restaurants(
            candidates, restaurants, user_lat, user_lon, current_time
        )
        
        # Then filter by rating
        return [restaurant_id for restaurant_id in base_results 
                if restaurants[restaurant_id]['rating'] >= self.min_rating]
