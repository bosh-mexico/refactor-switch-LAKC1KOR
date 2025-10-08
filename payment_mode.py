"""Payment mode enumeration and related utilities."""

from enum import Enum, auto
from typing import Any


class PaymentMode(Enum):
    """Enumeration of supported payment modes.
    
    This enum defines all the payment methods that the system supports.
    Each payment mode corresponds to a specific payment processor.
    """
    
    PAYPAL = auto()
    GOOGLEPAY = auto()
    CREDITCARD = auto()
    
    @classmethod
    def is_valid(cls, mode: Any) -> bool:
        """Check if the given mode is a valid PaymentMode.
        
        Args:
            mode: The value to validate
            
        Returns:
            bool: True if the mode is a valid PaymentMode instance, False otherwise
        """
        return isinstance(mode, cls)
    
    @classmethod
    def from_string(cls, mode_str: str) -> 'PaymentMode':
        """Convert string representation to PaymentMode.
        
        Args:
            mode_str: String representation of payment mode
            
        Returns:
            PaymentMode: The corresponding payment mode
            
        Raises:
            ValueError: If the string doesn't match any payment mode
        """
        mode_str = mode_str.upper()
        try:
            return cls[mode_str]
        except KeyError:
            raise ValueError(f"Invalid payment mode: {mode_str}. "
                           f"Valid modes are: {[mode.name for mode in cls]}")
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return self.name.replace('_', ' ').title()