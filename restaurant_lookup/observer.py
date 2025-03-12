"""
Observer pattern implementation for restaurant availability updates.

This module provides an observer pattern implementation for notifying
interested parties about changes in restaurant availability.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set


class RestaurantAvailabilityObserver(ABC):
    """
    Abstract base class for observers of restaurant availability.
    
    This class follows the Observer pattern to define the interface
    for objects that should be notified of changes in restaurant availability.
    """
    
    @abstractmethod
    def update(self, restaurant_id: int, is_available: bool) -> None:
        """
        Update the observer with a change in restaurant availability.
        
        Args:
            restaurant_id: ID of the restaurant whose availability changed
            is_available: Whether the restaurant is now available
        """
        pass


class RestaurantAvailabilitySubject:
    """
    Subject for restaurant availability changes.
    
    This class follows the Observer pattern to maintain a list of observers
    and notify them of changes in restaurant availability.
    """
    
    def __init__(self):
        """Initialize the subject with an empty list of observers."""
        self.observers: List[RestaurantAvailabilityObserver] = []
        self.available_restaurants: Set[int] = set()
    
    def attach(self, observer: RestaurantAvailabilityObserver) -> None:
        """
        Attach an observer to the subject.
        
        Args:
            observer: Observer to attach
        """
        if observer not in self.observers:
            self.observers.append(observer)
    
    def detach(self, observer: RestaurantAvailabilityObserver) -> None:
        """
        Detach an observer from the subject.
        
        Args:
            observer: Observer to detach
        """
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_availability_change(self, restaurant_id: int, is_available: bool) -> None:
        """
        Notify all observers of a change in restaurant availability.
        
        Args:
            restaurant_id: ID of the restaurant whose availability changed
            is_available: Whether the restaurant is now available
        """
        # Update internal state
        if is_available:
            self.available_restaurants.add(restaurant_id)
        else:
            self.available_restaurants.discard(restaurant_id)
        
        # Notify observers
        for observer in self.observers:
            observer.update(restaurant_id, is_available)
    
    def get_available_restaurants(self) -> Set[int]:
        """
        Get the set of currently available restaurants.
        
        Returns:
            Set of restaurant IDs that are currently available
        """
        return self.available_restaurants.copy()


class AvailabilityLogger(RestaurantAvailabilityObserver):
    """
    Observer that logs restaurant availability changes.
    
    This class implements the RestaurantAvailabilityObserver interface
    to log changes in restaurant availability.
    """
    
    def __init__(self, log_file: str = None):
        """
        Initialize the logger.
        
        Args:
            log_file: Path to log file (default: None, logs to console)
        """
        self.log_file = log_file
    
    def update(self, restaurant_id: int, is_available: bool) -> None:
        """
        Log a change in restaurant availability.
        
        Args:
            restaurant_id: ID of the restaurant whose availability changed
            is_available: Whether the restaurant is now available
        """
        status = "available" if is_available else "unavailable"
        message = f"Restaurant {restaurant_id} is now {status}"
        
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        else:
            print(message)


class AvailabilityMonitor(RestaurantAvailabilityObserver):
    """
    Observer that monitors restaurant availability for specific restaurants.
    
    This class implements the RestaurantAvailabilityObserver interface
    to monitor changes in availability for specific restaurants of interest.
    """
    
    def __init__(self, restaurants_of_interest: List[int]):
        """
        Initialize the monitor with restaurants of interest.
        
        Args:
            restaurants_of_interest: List of restaurant IDs to monitor
        """
        self.restaurants_of_interest = set(restaurants_of_interest)
        self.available_restaurants_of_interest: Set[int] = set()
    
    def update(self, restaurant_id: int, is_available: bool) -> None:
        """
        Update the monitor with a change in restaurant availability.
        
        Args:
            restaurant_id: ID of the restaurant whose availability changed
            is_available: Whether the restaurant is now available
        """
        if restaurant_id in self.restaurants_of_interest:
            if is_available:
                self.available_restaurants_of_interest.add(restaurant_id)
            else:
                self.available_restaurants_of_interest.discard(restaurant_id)
    
    def get_available_restaurants_of_interest(self) -> Set[int]:
        """
        Get the set of currently available restaurants of interest.
        
        Returns:
            Set of restaurant IDs of interest that are currently available
        """
        return self.available_restaurants_of_interest.copy()
    
    def is_any_available(self) -> bool:
        """
        Check if any restaurant of interest is available.
        
        Returns:
            True if any restaurant of interest is available, False otherwise
        """
        return len(self.available_restaurants_of_interest) > 0
