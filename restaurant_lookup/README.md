# Restaurant Lookup

A Python tool that finds restaurants available for delivery based on user locations, considering delivery radius and opening hours.

## Overview

This tool takes restaurant information and user locations as input, then determines which restaurants are:
1. Within delivery range of each user
2. Open at the current time

The solution is optimized for performance, using spatial indexing to achieve better than O(N*M) complexity, making it suitable for handling millions of restaurant entries efficiently.

## Features

- Fast spatial indexing using R-tree for location-based queries
- Accurate time-based filtering for restaurant opening hours
- Support for loading restaurant data from local files or URLs
- Comprehensive test suite with unit and integration tests
- Performance analysis with visual reporting
- Clean, maintainable code following SOLID principles

## Requirements

- Python 3.8+
- Dependencies managed through Poetry (recommended) or pip

## Installation

### Using Poetry (Recommended)

1. Install Poetry if you don't have it already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run commands within the Poetry environment:
   ```bash
   poetry run python restaurant_lookup.py
   ```

### Using pip (Alternative)

If you prefer not to use Poetry:

1. Install the required packages:
   ```bash
   pip install pandas numpy pyproj rtree matplotlib seaborn tabulate pytest pytest-benchmark freezegun
   ```

## Usage

### Basic Usage

```bash
# With Poetry
poetry run python restaurant_lookup.py --restaurants RESTAURANTS_CSV --users USERS_CSV --output OUTPUT_CSV

# Without Poetry
python restaurant_lookup.py --restaurants RESTAURANTS_CSV --users USERS_CSV --output OUTPUT_CSV
```

Where:
- `RESTAURANTS_CSV`: Path to CSV file or URL containing restaurant data
- `USERS_CSV`: Path to CSV file containing user locations
- `OUTPUT_CSV`: Path to write the output CSV file

### Example

```bash
# With Poetry
poetry run python restaurant_lookup.py --restaurants data/takehome.csv --users user_locations.csv --output results.csv




# Without Poetry
python restaurant_lookup.py --restaurants data/takehome.csv --users user_locations.csv --output results.csv
```

### Input Format

#### Restaurant CSV Format

The restaurant CSV file should have the following columns:
- `id`: Restaurant ID
- `latitude`: Latitude of the restaurant location
- `longitude`: Longitude of the restaurant location
- `availability_radius`: Delivery radius in kilometers
- `open_hour`: Start of the delivery schedule in ISO format (HH:MM:SS)
- `close_hour`: End of delivery schedule in ISO format (HH:MM:SS)
- `rating`: Rating between 1 and 5

Example:
```
id,latitude,longitude,availability_radius,open_hour,close_hour,rating
1,51.1942536,6.455508,5,14:00:00,23:00:00,4.7
2,50.132921,19.6385061,2,14:00:00,23:00:00,4.8
```

#### User Locations CSV Format

The user locations CSV file should have one location per line in the format:
```
USER_LATITUDE,USER_LONGITUDE
```

Example:
```
51.2,6.45
50.13,19.64
```

### Output Format

The output CSV file will have the following format:
- If at least one restaurant is available for delivery:
  ```
  USER_LOCATION,ID_RESTAURANT1;ID_RESTAURANT2;ID_RESTAURANT3
  ```
- If no restaurants are available for delivery:
  ```
  USER_LOCATION,
  ```

Example:
```
51.2,6.45,1;5;8
50.13,19.64,2
40.0,0.0,
```

## Performance Analysis

To run the performance analysis and generate visual reports:

```bash
# With Poetry
poetry run python run_benchmark.py

poetry run python run_benchmark.py --data-file data/takehome.csv --output-dir custom_results --skip-synthetic

# Without Poetry
python run_benchmark.py
```

This will:
1. Run benchmarks with different dataset sizes
2. Generate performance charts and visualizations
3. Create an HTML report with detailed analysis
4. Save all results to the `benchmark_results` directory

Each benchmark run automatically saves results to files, including:
- CSV summary tables
- JSON raw data
- PNG chart images
- HTML report with visualizations

You can customize the analysis with these options:
```bash
poetry run python run_benchmark.py --output-dir custom_results --skip-synthetic --data-file path/to/data.csv
```

## Testing

To run the tests:

```bash
# With Poetry
poetry run pytest

# Without Poetry
pytest
```

This will run all unit and integration tests to verify the functionality.

## Project Structure

- `restaurant_lookup.py`: Main script for finding restaurants
- `spatial_index.py`: Implements spatial indexing using R-tree
- `time_checker.py`: Handles checking if restaurants are open
- `distance_calculator.py`: Calculates distances between coordinates
- `data_loader.py`: Loads restaurant data from CSV files
- `result_writer.py`: Writes results to CSV files
- `interfaces.py`: Defines interfaces for components
- `tests/`: Contains all test files
- `data/`: Contains sample data files
- `benchmark.py`: Tool for performance analysis
- `run_benchmark.py`: Helper script to run the analyzer
- `pyproject.toml`: Poetry configuration and dependencies

## Design Approach

The solution follows SOLID principles with a clear separation of concerns:

1. **Single Responsibility**: Each class has a single responsibility
   - `TimeChecker` only handles time-related operations
   - `DistanceCalculator` only handles distance calculations
   - `SpatialIndex` only handles spatial indexing

2. **Open/Closed**: Components are open for extension but closed for modification
   - New implementations of interfaces can be added without modifying existing code

3. **Liskov Substitution**: Implementations can be substituted for their interfaces
   - Any implementation of `SpatialIndexInterface` can be used in the service

4. **Interface Segregation**: Interfaces are specific to client needs
   - Separate interfaces for time checking, distance calculation, etc.

5. **Dependency Inversion**: High-level modules depend on abstractions
   - `RestaurantLookupService` depends on interfaces, not concrete implementations

## Performance Considerations

The solution achieves better than O(N*M) complexity through:

1. **Spatial Indexing**: Using R-tree to efficiently find restaurants near user locations
2. **Bounding Box Optimization**: Initial filtering using a bounding box before exact distance calculation
3. **Memory Efficiency**: Optimized data structures to minimize memory usage


