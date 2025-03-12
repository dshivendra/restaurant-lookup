"""
Unit tests for the refactored spatial indexing module.
"""

import pytest
import pandas as pd
from datetime import datetime, time

from time_checker import TimeChecker
from distance_calculator import DistanceCalculator
from spatial_index import SpatialIndex


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
        'rating': [4.7, 4.8, 4.0, 4.9]
    })


@pytest.fixture
def time_checker():
    """Create a TimeChecker instance for testing."""
    return TimeChecker()


@pytest.fixture
def distance_calculator():
    """Create a DistanceCalculator instance for testing."""
    return DistanceCalculator()


@pytest.fixture
def spatial_index_with_data(sample_restaurants_df, time_checker, distance_calculator):
    """Create a SpatialIndex instance with sample data."""
    idx = SpatialIndex(time_checker, distance_calculator)
    idx.build_index(sample_restaurants_df)
    return idx


def test_build_index(sample_restaurants_df, time_checker, distance_calculator):
    """Test building the spatial index."""
    idx = SpatialIndex(time_checker, distance_calculator)
    idx.build_index(sample_restaurants_df)
    
    # Check if all restaurants are in the index
    assert len(idx.restaurants) == len(sample_restaurants_df)
    
    # Check if restaurant data is stored correctly
    for _, row in sample_restaurants_df.iterrows():
        restaurant_id = row['id']
        assert restaurant_id in idx.restaurants
        assert idx.restaurants[restaurant_id]['latitude'] == row['latitude']
        assert idx.restaurants[restaurant_id]['longitude'] == row['longitude']
        assert idx.restaurants[restaurant_id]['availability_radius'] == row['availability_radius']


def test_time_checker():
    """Test the TimeChecker class."""
    checker = TimeChecker()
    
    # Test during opening hours
    assert checker.is_open('14:00:00', '23:00:00', datetime.strptime('15:00:00', '%H:%M:%S').time())
    assert checker.is_open('14:00:00', '23:00:00', datetime.strptime('22:59:59', '%H:%M:%S').time())
    
    # Test at opening and closing hours
    assert checker.is_open('14:00:00', '23:00:00', datetime.strptime('14:00:00', '%H:%M:%S').time())
    assert checker.is_open('14:00:00', '23:00:00', datetime.strptime('23:00:00', '%H:%M:%S').time())
    
    # Test outside opening hours
    assert not checker.is_open('14:00:00', '23:00:00', datetime.strptime('13:59:59', '%H:%M:%S').time())
    assert not checker.is_open('14:00:00', '23:00:00', datetime.strptime('23:00:01', '%H:%M:%S').time())
    
    # Test overnight hours
    assert checker.is_open('22:00:00', '06:00:00', datetime.strptime('23:00:00', '%H:%M:%S').time())
    assert checker.is_open('22:00:00', '06:00:00', datetime.strptime('02:00:00', '%H:%M:%S').time())
    assert not checker.is_open('22:00:00', '06:00:00', datetime.strptime('21:59:59', '%H:%M:%S').time())
    assert not checker.is_open('22:00:00', '06:00:00', datetime.strptime('06:00:01', '%H:%M:%S').time())


def test_distance_calculator():
    """Test the DistanceCalculator class."""
    calculator = DistanceCalculator()
    
    # Test with known distance (approximately)
    # Berlin to Munich is about 500-600 km
    berlin_lat, berlin_lon = 52.5200, 13.4050
    munich_lat, munich_lon = 48.1351, 11.5820
    
    distance = calculator.calculate_distance(berlin_lat, berlin_lon, munich_lat, munich_lon)
    
    # Check if distance is in the expected range
    assert 500 <= distance <= 600


def test_find_restaurants_in_radius(spatial_index_with_data):
    """Test finding restaurants within radius."""
    idx = spatial_index_with_data
    
    # Test case 1: User near restaurant 1 during opening hours
    user_lat, user_lon = 51.2, 6.45  # Close to restaurant 1
    current_time = datetime.strptime('15:00:00', '%H:%M:%S')
    
    available = idx.find_restaurants_in_radius(user_lat, user_lon, current_time)
    assert 1 in available  # Restaurant 1 should be available
    
    # Test case 2: User near restaurant 1 outside opening hours
    current_time = datetime.strptime('12:00:00', '%H:%M:%S')
    
    available = idx.find_restaurants_in_radius(user_lat, user_lon, current_time)
    assert 1 not in available  # Restaurant 1 should not be available (closed)
    
    # Test case 3: User far from all restaurants
    user_lat, user_lon = 40.0, 0.0  # Far from all restaurants
    current_time = datetime.strptime('15:00:00', '%H:%M:%S')
    
    available = idx.find_restaurants_in_radius(user_lat, user_lon, current_time)
    assert len(available) == 0  # No restaurants should be available
