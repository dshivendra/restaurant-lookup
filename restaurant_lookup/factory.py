"""
Factory pattern implementation for creating spatial indexes.

This module provides a factory for creating different types of spatial indexes,
allowing for flexibility in choosing the appropriate spatial indexing strategy.
"""

from interfaces import SpatialIndexInterface
from spatial_index import SpatialIndex


class SpatialIndexFactory:
    """
    Factory for creating different types of spatial indexes.
    
    This class follows the Factory Method pattern to create different
    implementations of the SpatialIndexInterface.
    """
    
    @staticmethod
    def create_index(index_type, time_checker, distance_calculator):
        """
        Create a spatial index of the specified type.
        
        Args:
            index_type: Type of spatial index to create ('rtree' is currently supported)
            time_checker: TimeChecker instance for checking restaurant opening hours
            distance_calculator: DistanceCalculator instance for calculating distances
            
        Returns:
            SpatialIndexInterface: An instance of the specified spatial index type
            
        Raises:
            ValueError: If the specified index type is not supported
        """
        if index_type == "rtree":
            return SpatialIndex(time_checker, distance_calculator)
        else:
            raise ValueError(f"Unsupported spatial index type: {index_type}")
