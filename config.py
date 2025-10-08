"""Configuration constants for the payment checkout system."""

from decimal import Decimal
from typing import Final


class PaymentConfig:
    """Configuration constants for payment processing."""
    
    # Amount validation
    MIN_PAYMENT_AMOUNT: Final[Decimal] = Decimal('0.01')
    MAX_PAYMENT_AMOUNT: Final[Decimal] = Decimal('999999.99')
    
    # Precision for currency calculations
    CURRENCY_PRECISION: Final[int] = 2
    
    # Error messages
    INVALID_PAYMENT_MODE_ERROR: Final[str] = "Unsupported or invalid payment mode selected"
    INVALID_AMOUNT_TYPE_ERROR: Final[str] = "Amount must be a number"
    AMOUNT_TOO_LOW_ERROR: Final[str] = f"Amount must be at least ${MIN_PAYMENT_AMOUNT}"
    AMOUNT_TOO_HIGH_ERROR: Final[str] = f"Amount cannot exceed ${MAX_PAYMENT_AMOUNT}"
    PROCESSOR_NOT_FOUND_ERROR: Final[str] = "Payment processor not found for the selected mode"
    
    # Success messages
    PAYMENT_SUCCESS_TEMPLATE: Final[str] = "Successfully processed {payment_type} payment of ${amount:.2f}"


class ProcessorConfig:
    """Configuration for payment processors."""
    
    # Timeout settings (in seconds)
    DEFAULT_TIMEOUT: Final[int] = 30
    PAYPAL_TIMEOUT: Final[int] = 45
    GOOGLEPAY_TIMEOUT: Final[int] = 30
    CREDITCARD_TIMEOUT: Final[int] = 60
    
    # Retry settings
    MAX_RETRIES: Final[int] = 3
    RETRY_DELAY: Final[float] = 1.0