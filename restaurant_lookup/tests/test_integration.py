"""
Integration tests for the refactored restaurant lookup script.
"""

import os
import pytest
import pandas as pd
import csv
from datetime import datetime, time
import tempfile
import shutil
from freezegun import freeze_time

from time_checker import TimeChecker
from distance_calculator import DistanceCalculator
from spatial_index import SpatialIndex
from data_loader import CSVDataLoader
from result_writer import CSVResultWriter
from restaurant_lookup import RestaurantLookupService


@pytest.fixture
def sample_restaurants_csv():
    """Create a sample CSV file with restaurant data for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, 'restaurants.csv')
    
    # Create sample data
    data = [
        ['id', 'latitude', 'longitude', 'availability_radius', 'open_hour', 'close_hour', 'rating'],
        ['1', '51.1942536', '6.455508', '5', '14:00:00', '23:00:00', '4.7'],
        ['2', '50.132921', '19.6385061', '2', '14:00:00', '23:00:00', '4.8'],
        ['3', '52.5018668', '13.3254556', '3', '09:00:00', '20:00:00', '4.0'],
        ['4', '50.9118822', '4.4350511', '1', '08:00:00', '23:00:00', '4.9']
    ]
    
    # Write to CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    yield csv_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_users_csv():
    """Create a sample CSV file with user locations for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, 'users.csv')
    
    # Create sample data - users at various distances from restaurants
    data = [
        ['51.2', '6.45'],  # Near restaurant 1
        ['50.13', '19.64'],  # Near restaurant 2
        ['52.5', '13.33'],  # Near restaurant 3
        ['50.91', '4.43'],  # Near restaurant 4
        ['40.0', '0.0']  # Far from all restaurants
    ]
    
    # Write to CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    yield csv_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def restaurant_lookup_service():
    """Create a RestaurantLookupService instance for testing."""
    time_checker = TimeChecker()
    distance_calculator = DistanceCalculator()
    spatial_index = SpatialIndex(time_checker, distance_calculator)
    data_loader = CSVDataLoader()
    result_writer = CSVResultWriter()
    
    return RestaurantLookupService(spatial_index, data_loader, result_writer)


@freeze_time("2023-01-01 15:00:00")  # Freeze time to 15:00 (when restaurants 1 and 2 are open)
def test_end_to_end(sample_restaurants_csv, sample_users_csv, restaurant_lookup_service):
    """Test the entire restaurant lookup process end-to-end."""
    # Create a temporary output file
    output_file = tempfile.NamedTemporaryFile(delete=False)
    output_path = output_file.name
    output_file.close()
    
    try:
        # Load restaurant data and build index
        restaurant_lookup_service.load_restaurants(sample_restaurants_csv)
        
        # Process user locations
        restaurant_lookup_service.process_user_locations(sample_users_csv, output_path)
        
        # Read and verify output
        with open(output_path, 'r') as f:
            reader = csv.reader(f)
            results = list(reader)
        
        # Verify results
        assert len(results) == 5  # 5 user locations
        
        # User near restaurant 1 should have restaurant 1 available (it's open at 15:00)
        assert results[0][0] == '51.2,6.45'
        assert '1' in results[0][1]
        
        # User near restaurant 2 should have restaurant 2 available (it's open at 15:00)
        assert results[1][0] == '50.13,19.64'
        assert '2' in results[1][1]
        
        # User near restaurant 3 should have restaurant 3 available (it's open from 9:00 to 20:00)
        assert results[2][0] == '52.5,13.33'
        assert '3' in results[2][1]
        
        # User near restaurant 4 should have restaurant 4 available (it's open from 8:00 to 23:00)
        assert results[3][0] == '50.91,4.43'
        assert '4' in results[3][1]
        
        # User far from all restaurants should have no restaurants available
        assert results[4][0] == '40.0,0.0'
        assert results[4][1] == ''
        
    finally:
        # Cleanup
        os.unlink(output_path)


@freeze_time("2023-01-01 15:00:00")  # Freeze time to 15:00
def test_process_user_locations_with_invalid_data(sample_restaurants_csv, restaurant_lookup_service):
    """Test processing user locations with invalid data."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create a sample users CSV with invalid data
    users_csv_path = os.path.join(temp_dir, 'invalid_users.csv')
    with open(users_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([
            ['not_a_number', '6.45'],  # Invalid latitude
            ['51.2'],  # Missing longitude
            [],  # Empty row
            ['51.2', '6.45']  # Valid row
        ])
    
    # Create a temporary output file
    output_file = tempfile.NamedTemporaryFile(delete=False)
    output_path = output_file.name
    output_file.close()
    
    try:
        # Load restaurant data and build index
        restaurant_lookup_service.load_restaurants(sample_restaurants_csv)
        
        # Process user locations (should handle invalid data gracefully)
        restaurant_lookup_service.process_user_locations(users_csv_path, output_path)
        
        # Read and verify output
        with open(output_path, 'r') as f:
            reader = csv.reader(f)
            results = list(reader)
        
        # Only the valid row should be processed
        assert len(results) == 1
        assert results[0][0] == '51.2,6.45'
        
    finally:
        # Cleanup
        os.unlink(output_path)
        shutil.rmtree(temp_dir)


def test_with_real_data():
    """Test with the real data provided in the takehome.csv file."""
    # Skip this test if the takehome.csv file doesn't exist
    # Use os.path for platform-independent path handling
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    takehome_csv = os.path.join(current_dir, 'data', 'takehome.csv')
    if not os.path.exists(takehome_csv):
        pytest.skip(f"Takehome CSV file not found at {takehome_csv}")
    
    # Create a sample users CSV
    temp_dir = tempfile.mkdtemp()
    users_csv_path = os.path.join(temp_dir, 'test_users.csv')
    with open(users_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([
            ['51.2', '6.45'],  # Near some restaurants in the dataset
            ['40.0', '0.0']    # Far from most restaurants
        ])
    
    # Create a temporary output file
    output_file = tempfile.NamedTemporaryFile(delete=False)
    output_path = output_file.name
    output_file.close()
    
    try:
        # Create service
        time_checker = TimeChecker()
        distance_calculator = DistanceCalculator()
        spatial_index = SpatialIndex(time_checker, distance_calculator)
        data_loader = CSVDataLoader()
        result_writer = CSVResultWriter()
        service = RestaurantLookupService(spatial_index, data_loader, result_writer)
        
        # Load restaurant data and build index
        service.load_restaurants(takehome_csv)
        
        # Process user locations
        service.process_user_locations(users_csv_path, output_path)
        
        # Verify output exists
        assert os.path.exists(output_path)
        
        # Read output
        with open(output_path, 'r') as f:
            reader = csv.reader(f)
            results = list(reader)
        
        # Verify we have results for both user locations
        assert len(results) == 2
        
    finally:
        # Cleanup
        os.unlink(output_path)
        shutil.rmtree(temp_dir)
