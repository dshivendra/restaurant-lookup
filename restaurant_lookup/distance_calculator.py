"""
Distance calculation module for geographic coordinates.

This module provides functionality to calculate distances between geographic points,
following the Single Responsibility Principle.
"""

import pyproj
from interfaces import DistanceCalculatorInterface


class DistanceCalculator(DistanceCalculatorInterface):
    """
    Implementation of distance calculation functionality.
    
    This class is responsible for calculating the geodesic distance
    between two geographic points on Earth's surface.
    """
    
    def __init__(self):
        """Initialize the distance calculator with a geodesic model."""
        self.geod = pyproj.Geod(ellps='WGS84')  # For accurate distance calculations
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the geodesic distance between two points in kilometers.
        
        Args:
            lat1, lon1: Coordinates of the first point
            lat2, lon2: Coordinates of the second point
            
        Returns:
            float: Distance in kilometers
        """
        # Use pyproj's Geod for accurate distance calculation on Earth's surface
        _, _, distance = self.geod.inv(lon1, lat1, lon2, lat2)
        return distance / 1000  # Convert meters to kilometers
