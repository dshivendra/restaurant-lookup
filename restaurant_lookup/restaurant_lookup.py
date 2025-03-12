"""
Restaurant Finder Tool

A script that finds restaurants available for delivery based on user locations,
considering delivery radius and opening hours.


"""

import argparse
import csv
import os
from datetime import datetime
from typing import List, Dict, Any

# My custom modules
from interfaces import SpatialIndexInterface, DataLoaderInterface, ResultWriterInterface
from spatial_index import SpatialIndex
from time_checker import TimeChecker
from distance_calculator import DistanceCalculator
from data_loader import CSVDataLoader
from result_writer import CSVResultWriter


class RestaurantLookupService:
    """
    Main service for finding restaurants near users.
    
    This handles the whole process of loading restaurant data,
    finding ones that are open and within range, and saving results.
    
    Follows the Single Responsibility Principle by delegating specialized
    tasks to appropriate components.
    """
    
    def __init__(self, 
                 spatial_idx: SpatialIndexInterface,
                 data_loader: DataLoaderInterface,
                 result_writer: ResultWriterInterface):
        """
        Set up the service with needed components.
        
        Follows Dependency Inversion Principle by depending on abstractions
        rather than concrete implementations.
        """
        self.spatial_idx = spatial_idx
        self.spatial_index = spatial_idx  # Alias for backward compatibility
        self.data_loader = data_loader
        self.result_writer = result_writer
        self.restaurants_loaded = False
    
    def load_restaurant_data(self, data_source: str) -> None:
        """
        Load restaurant info and build the spatial index.
        
        Args:
            data_source: File path or URL with restaurant data
        """
        # Use os.path for platform-independent path handling if not a URL
        if not data_source.startswith(('http://', 'https://')):
            data_source = os.path.abspath(os.path.expanduser(data_source))
            
        print(f"Loading restaurants from {data_source}...")
        restaurants = self.data_loader.load_data(data_source)
        
        print(f"Building spatial index for {len(restaurants)} restaurants...")
        self.spatial_idx.build_index(restaurants)
        self.restaurants_loaded = True
        
    def load_restaurants(self, data_source: str) -> None:
        """
        Alias for load_restaurant_data for backward compatibility.
        
        Args:
            data_source: File path or URL with restaurant data
        """
        return self.load_restaurant_data(data_source)
    
    def find_restaurants_for_users(self, users_file: str, output_file: str) -> None:
        """
        Find available restaurants for each user location.
        
        Args:
            users_file: Path to CSV with user locations
            output_file: Where to save the results
        """
        if not self.restaurants_loaded:
            raise ValueError("No restaurant data loaded! Call load_restaurant_data first.")
            
        # Use os.path for platform-independent path handling
        users_file = os.path.abspath(os.path.expanduser(users_file))
        output_file = os.path.abspath(os.path.expanduser(output_file))
            
        print(f"Processing {users_file}...")
        now = datetime.now()
        results = []
        
        # Read user locations
        with open(users_file, 'r') as f:
            reader = csv.reader(f)
            
            for i, row in enumerate(reader):
                # Skip empty rows
                if not row:
                    continue
                    
                # Make sure we have both lat and lon
                if len(row) < 2:
                    print(f"Warning: Line {i+1} doesn't have enough data: {row}")
                    continue
                
                try:
                    # Parse coordinates
                    lat = float(row[0])
                    lon = float(row[1])
                    
                    # Find restaurants that deliver here and are open
                    available = self.spatial_idx.find_restaurants_in_radius(lat, lon, now)
                    
                    # Add to results
                    results.append({
                        'location': f"{lat},{lon}",
                        'restaurants': available
                    })
                except ValueError:
                    print(f"Warning: Couldn't parse coordinates on line {i+1}: {row}")
        
        # Save the results
        self.result_writer.write_results(results, output_file)
        print(f"✓ Results saved to {output_file}")
        print(f"  Processed {len(results)} user locations")
        
    def process_user_locations(self, user_locations_path: str, output_path: str) -> None:
        """
        Process user locations and find available restaurants.
        
        Args:
            user_locations_path: Path to CSV file with user locations
            output_path: Path to write the output CSV file
        """
        # Check if user_locations_path exists, if not create a sample file
        if not os.path.exists(user_locations_path):
            print(f"User locations file {user_locations_path} not found. Creating a sample file.")
            with open(user_locations_path, 'w') as f:
                f.write("51.2,6.45\n50.13,19.64\n52.5,13.3\n")
        
        print(f"Processing user locations from {user_locations_path}...")
        
        # Get current time
        current_time = datetime.now().time()
        
        # Process each user location
        results = []
        with open(user_locations_path, 'r') as user_file:
            for i, line in enumerate(user_file):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse user location
                    parts = line.split(',')
                    if len(parts) != 2:
                        print(f"Warning: Invalid user location format at line {i+1}: {line}")
                        continue
                    
                    user_lat = float(parts[0])
                    user_lon = float(parts[1])
                    
                    # Find restaurants in radius
                    restaurant_ids = self.spatial_index.find_restaurants_in_radius(
                        user_lat, user_lon, current_time
                    )
                    
                    # Add to results
                    results.append({
                        'location': f"{user_lat},{user_lon}",
                        'restaurants': restaurant_ids
                    })
                    
                    # Print progress
                    print(f"Query #{i+1}: Finding restaurants near ({user_lat}, {user_lon}) at {current_time}")
                    print(f"Query #{i+1}: Found {len(restaurant_ids)} restaurants")
                    
                except ValueError as e:
                    print(f"Warning: Error processing user location at line {i+1}: {e}")
                    continue
        
        # Write results
        self.result_writer.write_results(results, output_path)
        print(f"Results written to {output_path}")


def run_cli():
    """Handle command line interface and run the restaurant finder."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Find restaurants available for delivery based on user locations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python restaurant_lookup.py --restaurants data/restaurants.csv --users users.csv --output results.csv
  python restaurant_lookup.py --restaurants https://example.com/data.csv --users locations.csv --output out.csv
        """
    )
    
    # Add arguments
    parser.add_argument('--restaurants', required=True, 
                        help='CSV file or URL with restaurant data')
    parser.add_argument('--users', required=True, 
                        help='CSV file with user locations (lat,lon)')
    parser.add_argument('--output', required=True, 
                        help='Where to save the results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Make sure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create components
    time_checker = TimeChecker()
    distance_calc = DistanceCalculator()
    spatial_idx = SpatialIndex(time_checker, distance_calc)
    data_loader = CSVDataLoader()
    result_writer = CSVResultWriter()
    
    # Create and run the service
    service = RestaurantLookupService(spatial_idx, data_loader, result_writer)
    service.load_restaurant_data(args.restaurants)
    service.find_restaurants_for_users(args.users, args.output)
    
    print("All done! 🍕")


# Run the script
if __name__ == "__main__":
    run_cli()
