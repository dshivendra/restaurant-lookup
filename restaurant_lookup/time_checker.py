"""
Time checking module for restaurant availability.

This module provides functionality to check if restaurants are open
at a specific time, following the Single Responsibility Principle.
"""

from datetime import datetime, time
from interfaces import TimeCheckerInterface


class TimeChecker(TimeCheckerInterface):
    """
    Implementation of time checking functionality.
    
    This class is responsible for determining if a restaurant is open
    at a specific time based on its opening and closing hours.
    """
    
    def is_open(self, open_hour: str, close_hour: str, current_time=None) -> bool:
        """
        Check if a location is open at the specified time.
        
        Args:
            open_hour: Opening hour in ISO format (HH:MM:SS)
            close_hour: Closing hour in ISO format (HH:MM:SS)
            current_time: Time to check (default: current time)
            
        Returns:
            True if open, False otherwise
        """
        if current_time is None:
            current_time = datetime.now().time()
        elif isinstance(current_time, datetime):
            current_time = current_time.time()
            
        # Parse open and close hours
        open_time = datetime.strptime(open_hour, '%H:%M:%S').time()
        close_time = datetime.strptime(close_hour, '%H:%M:%S').time()
        
        # Check if current time is within opening hours
        if open_time <= close_time:
            # Normal case: open_time <= current_time <= close_time
            return open_time <= current_time <= close_time
        else:
            # Special case: restaurant closes after midnight
            # In this case: current_time >= open_time OR current_time <= close_time
            return current_time >= open_time or current_time <= close_time
