"""
Entry point script for running the restaurant lookup tool.
This script provides a unified entry point that works both with and without Poetry.
"""
import os
import sys
import argparse

def main():
    """Main function to parse arguments and run the restaurant lookup tool."""
    parser = argparse.ArgumentParser(
        description='Restaurant Lookup Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --restaurants data/takehome.csv --users data/user_locations.csv --output results.csv
  python run.py --benchmark
        """
    )
    
    # Add arguments
    parser.add_argument('--restaurants', 
                        help='CSV file or URL with restaurant data')
    parser.add_argument('--users', 
                        help='CSV file with user locations (lat,lon)')
    parser.add_argument('--output', 
                        help='Where to save the results')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run benchmarking instead of normal operation')
    
    args = parser.parse_args()
    
    # Ensure the current directory is in the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    if args.benchmark:
        # Run benchmarking
        from run_benchmark import main as run_benchmark_main
        return run_benchmark_main()
    else:
        # Check if all required arguments are provided
        if not all([args.restaurants, args.users, args.output]):
            parser.error("--restaurants, --users, and --output are required for normal operation")
        
        # Run normal operation
        from restaurant_lookup import run_cli
        
        # Override sys.argv to pass arguments to run_cli
        sys.argv = [
            sys.argv[0],
            '--restaurants', args.restaurants,
            '--users', args.users,
            '--output', args.output
        ]
        
        run_cli()
        return 0

if __name__ == "__main__":
    sys.exit(main())
