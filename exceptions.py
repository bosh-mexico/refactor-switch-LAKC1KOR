"""Custom exceptions for the payment checkout system."""


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """Initialize payment error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.error_code = error_code


class InvalidPaymentModeError(PaymentError):
    """Raised when an invalid payment mode is provided."""
    
    def __init__(self, mode: str):
        super().__init__(
            f"Invalid payment mode: {mode}",
            error_code="INVALID_PAYMENT_MODE"
        )
        self.invalid_mode = mode


class InvalidAmountError(PaymentError):
    """Raised when an invalid payment amount is provided."""
    
    def __init__(self, amount, reason: str):
        super().__init__(
            f"Invalid payment amount {amount}: {reason}",
            error_code="INVALID_AMOUNT"
        )
        self.invalid_amount = amount


class PaymentProcessingError(PaymentError):
    """Raised when payment processing fails."""
    
    def __init__(self, message: str, payment_mode: str = None):
        super().__init__(message, error_code="PROCESSING_FAILED")
        self.payment_mode = payment_mode


class ProcessorNotFoundError(PaymentError):
    """Raised when no processor is found for a payment mode."""
    
    def __init__(self, payment_mode: str):
        super().__init__(
            f"No processor found for payment mode: {payment_mode}",
            error_code="PROCESSOR_NOT_FOUND"
        )
        self.payment_mode = payment_mode