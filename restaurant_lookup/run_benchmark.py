"""
Run script for the performance analyzer

This script sets up and runs the performance analyzer with appropriate settings.
It handles installing dependencies if needed and provides a simple interface
for running the analysis.

"""

import os
import sys
import subprocess
import argparse


def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        # Try importing key packages
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import tabulate
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False


def install_dependencies():
    """Install required dependencies for the performance analyzer."""
    print("📦 Installing required dependencies...")
    
    requirements_file = "requirements_updated.txt"
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found!")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_performance_analyzer(args):
    """Run the performance analyzer with the specified arguments."""
    print("\n🚀 Running performance analyzer...")
    
    # Import the analyzer module
    try:
        # Use absolute import to avoid import issues
        import os
        import sys
        
        # Add the current directory to the path if not already there
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from benchmark import PerformanceTester
    except ImportError as e:
        print(f"❌ Error: Could not import benchmark module: {e}")
        print("   Make sure benchmark.py is in the current directory.")
        return False
    
    # Create output directory with proper path handling
    output_dir = os.path.abspath(os.path.expanduser(args.output_dir))
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and run the tester
    tester = PerformanceTester(output_dir=output_dir)
    
    # Run synthetic tests
    if not args.skip_synthetic:
        tester.run_synthetic_tests()
    
    # Run real data test if available
    if not args.skip_real:
        # Use os.path for platform-independent path handling
        takehome_csv = os.path.abspath(os.path.expanduser(args.data_file))
        if os.path.exists(takehome_csv):
            tester.run_real_data_test(takehome_csv)
        else:
            print(f"⚠️ Warning: Data file not found at {takehome_csv}")
    
    # Generate report
    tester.generate_report()
    
    print(f"\n✅ Analysis complete! Results saved to {output_dir}")
    print(f"   View the HTML report at: {os.path.join(output_dir, 'performance_report.html')}")
    
    return True


def main():
    """Main function to parse arguments and run the analyzer."""
    parser = argparse.ArgumentParser(
        description="Run the restaurant lookup performance analyzer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--output-dir", 
        default="benchmark_results",
        help="Directory to save benchmark results"
    )
    
    parser.add_argument(
        "--data-file", 
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "takehome.csv"),
        help="Path to the real data file"
    )
    
    parser.add_argument(
        "--skip-synthetic", 
        action="store_true",
        help="Skip synthetic data tests"
    )
    
    parser.add_argument(
        "--skip-real", 
        action="store_true",
        help="Skip real data tests"
    )
    
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="Install dependencies before running"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            return 1
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️ Missing dependencies. Run with --install-deps to install them.")
        return 1
    
    # Run the analyzer
    if run_performance_analyzer(args):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
