"""
Setup script for non-poetry installation.
This script allows the project to be installed using pip without poetry.
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="restaurant-lookup",
    version="0.1.0",
    author="Shivendra Dubey",
    author_email="dshivendra88@gmail.com",
    description="A tool that finds restaurants available for delivery based on user locations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dshivendra/restaurant-lookup",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "pyproj>=3.0.0",
        "rtree>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "tabulate>=0.8.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "restaurant-lookup=restaurant_lookup:run_cli",
        ],
    },
)
