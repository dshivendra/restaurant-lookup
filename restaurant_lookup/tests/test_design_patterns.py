"""
Unit tests for the design pattern implementations.
"""

import pytest
import pandas as pd
from datetime import datetime, time
from freezegun import freeze_time

from time_checker import TimeChecker
from distance_calculator import DistanceCalculator
from spatial_index import SpatialIndex
from factory import SpatialIndexFactory
from filter_strategy import FilterStrategy, DistanceAndTimeFilterStrategy, RatingFilterStrategy
from decorator import CachingSpatialIndex, LoggingSpatialIndex
from observer import RestaurantAvailabilitySubject, AvailabilityLogger, AvailabilityMonitor
from composite import CircleRegion, RectangleRegion, UnionRegion, IntersectionRegion


@pytest.fixture
def sample_restaurants_df():
    """Create a sample DataFrame with restaurant data for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4],
        'latitude': [51.1942536, 50.132921, 52.5018668, 50.9118822],
        'longitude': [6.455508, 19.6385061, 13.3254556, 4.4350511],
        'availability_radius': [5, 2, 3, 1],
        'open_hour': ['14:00:00', '14:00:00', '09:00:00', '08:00:00'],
        'close_hour': ['23:00:00', '23:00:00', '20:00:00', '23:00:00'],
        'rating': [4.7, 4.8, 4.0, 3.5]
    })


@pytest.fixture
def time_checker():
    """Create a TimeChecker instance for testing."""
    return TimeChecker()


@pytest.fixture
def distance_calculator():
    """Create a DistanceCalculator instance for testing."""
    return DistanceCalculator()


def test_factory_pattern(sample_restaurants_df, time_checker, distance_calculator):
    """Test the Factory pattern for creating spatial indexes."""
    # Create a spatial index using the factory
    spatial_index = SpatialIndexFactory.create_index("rtree", time_checker, distance_calculator)
    
    # Verify it's the correct type
    assert isinstance(spatial_index, SpatialIndex)
    
    # Test functionality
    spatial_index.build_index(sample_restaurants_df)
    
    # Check if all restaurants are in the index
    assert len(spatial_index.restaurants) == len(sample_restaurants_df)
    
    # Test with invalid type
    with pytest.raises(ValueError):
        SpatialIndexFactory.create_index("invalid_type", time_checker, distance_calculator)


@freeze_time("2023-01-01 15:00:00")  # Freeze time to 15:00 (when restaurants 1 and 2 are open)
def test_strategy_pattern(sample_restaurants_df, time_checker, distance_calculator):
    """Test the Strategy pattern for filtering restaurants."""
    # Create a spatial index
    spatial_index = SpatialIndex(time_checker, distance_calculator)
    spatial_index.build_index(sample_restaurants_df)
    
    # Get candidate restaurants
    user_lat, user_lon = 51.2, 6.45  # Near restaurant 1
    candidates = list(spatial_index.idx.intersection(
        (user_lat - 1, user_lon - 1, user_lat + 1, user_lon + 1)
    ))
    
    # Create and test the distance and time filter strategy
    distance_time_strategy = DistanceAndTimeFilterStrategy(time_checker, distance_calculator)
    results = distance_time_strategy.filter_restaurants(
        candidates, spatial_index.restaurants, user_lat, user_lon
    )
    assert 1 in results  # Restaurant 1 should be available
    
    # Create and test the rating filter strategy
    rating_strategy = RatingFilterStrategy(distance_time_strategy, min_rating=4.5)
    results = rating_strategy.filter_restaurants(
        candidates, spatial_index.restaurants, user_lat, user_lon
    )
    assert 1 in results  # Restaurant 1 has rating 4.7, should be available
    
    # Test with higher rating threshold
    rating_strategy = RatingFilterStrategy(distance_time_strategy, min_rating=4.8)
    results = rating_strategy.filter_restaurants(
        candidates, spatial_index.restaurants, user_lat, user_lon
    )
    assert 1 not in results  # Restaurant 1 has rating 4.7, should not be available


@freeze_time("2023-01-01 15:00:00")  # Freeze time to 15:00
def test_decorator_pattern(sample_restaurants_df, time_checker, distance_calculator):
    """Test the Decorator pattern for enhancing spatial indexes."""
    # Create a base spatial index
    base_index = SpatialIndex(time_checker, distance_calculator)
    base_index.build_index(sample_restaurants_df)
    
    # Create a caching decorator
    caching_index = CachingSpatialIndex(base_index)
    
    # Test caching functionality
    user_lat, user_lon = 51.2, 6.45  # Near restaurant 1
    
    # First call should be a cache miss
    results1 = caching_index.find_restaurants_in_radius(user_lat, user_lon)
    assert caching_index.cache_hits == 0
    assert caching_index.cache_misses == 1
    
    # Second call with same parameters should be a cache hit
    results2 = caching_index.find_restaurants_in_radius(user_lat, user_lon)
    assert caching_index.cache_hits == 1
    assert caching_index.cache_misses == 1
    
    # Results should be the same
    assert results1 == results2
    
    # Create a logging decorator
    logging_index = LoggingSpatialIndex(base_index)
    
    # Test logging functionality (just check it doesn't raise exceptions)
    logging_index.find_restaurants_in_radius(user_lat, user_lon)
    assert logging_index.query_count == 1
    
    # Test chaining decorators
    chained_index = LoggingSpatialIndex(caching_index)
    chained_index.find_restaurants_in_radius(user_lat, user_lon)
    assert chained_index.query_count == 1
    assert caching_index.cache_hits == 2  # Another hit in the cache


def test_observer_pattern():
    """Test the Observer pattern for restaurant availability updates."""
    # Create a subject
    subject = RestaurantAvailabilitySubject()
    
    # Create observers
    logger = AvailabilityLogger()
    monitor = AvailabilityMonitor([1, 3, 5])
    
    # Attach observers
    subject.attach(logger)
    subject.attach(monitor)
    
    # Test notifications
    subject.notify_availability_change(1, True)
    assert 1 in subject.get_available_restaurants()
    assert 1 in monitor.get_available_restaurants_of_interest()
    assert monitor.is_any_available() == True
    
    subject.notify_availability_change(2, True)
    assert 2 in subject.get_available_restaurants()
    assert 2 not in monitor.get_available_restaurants_of_interest()
    
    subject.notify_availability_change(1, False)
    assert 1 not in subject.get_available_restaurants()
    assert 1 not in monitor.get_available_restaurants_of_interest()
    assert monitor.is_any_available() == False
    
    # Test detaching
    subject.detach(logger)
    subject.notify_availability_change(3, True)
    assert 3 in subject.get_available_restaurants()
    assert 3 in monitor.get_available_restaurants_of_interest()


def test_composite_pattern(distance_calculator):
    """Test the Composite pattern for complex geographic regions."""
    # Create simple regions
    # Using a smaller radius for testing to ensure points are within the expected distance
    circle1 = CircleRegion(51.0, 6.0, 50.0, distance_calculator)  # 50km radius
    circle2 = CircleRegion(52.0, 7.0, 25.0, distance_calculator)  # 25km radius
    rectangle = RectangleRegion(50.0, 5.0, 51.5, 6.5)
    
    # Test simple regions
    assert circle1.contains(51.0, 6.0) == True  # Center point
    assert circle1.contains(51.1, 6.1) == True  # Point within radius
    assert circle1.contains(60.0, 6.0) == False  # Point outside radius
    
    assert rectangle.contains(50.5, 5.5) == True  # Point inside
    assert rectangle.contains(52.0, 5.5) == False  # Point outside
    
    # Create composite regions
    union = UnionRegion()
    union.add_region(circle1)
    union.add_region(rectangle)
    
    intersection = IntersectionRegion()
    intersection.add_region(circle1)
    intersection.add_region(rectangle)
    
    # Test union region
    assert union.contains(51.0, 6.0) == True  # In circle1
    assert union.contains(50.5, 5.5) == True  # In rectangle
    assert union.contains(55.0, 10.0) == False  # Outside both
    
    # Test intersection region - point must be in both regions
    assert intersection.contains(51.0, 6.0) == True  # In both
    
    # The point (50.5, 5.5) is in the rectangle, let's verify it's also in the circle
    assert rectangle.contains(50.5, 5.5) == True
    assert circle1.contains(50.5, 5.5) == True
    assert intersection.contains(50.5, 5.5) == True
    
    # Test adding to composites
    union.add_region(circle2)
    assert union.contains(52.0, 7.0) == True  # In circle2
    
    # Test removing from composites
    union.remove_region(circle1)
    assert union.contains(51.0, 6.0) == True  # Still in rectangle
