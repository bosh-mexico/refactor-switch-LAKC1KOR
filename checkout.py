"""Checkout system with payment processing capabilities."""

import logging
from decimal import Decimal, InvalidOperation
from typing import Dict, Tuple, List, Optional
from abc import ABC, abstractmethod

from payment_mode import PaymentMode
from config import PaymentConfig, ProcessorConfig
from exceptions import (
    PaymentError, InvalidPaymentModeError, InvalidAmountError,
    PaymentProcessingError, ProcessorNotFoundError
)


# Configure logging
logger = logging.getLogger(__name__)


class PaymentResult:
    """Result of a payment processing operation."""
    
    def __init__(self, success: bool, message: str, transaction_id: Optional[str] = None):
        """Initialize payment result.
        
        Args:
            success: Whether the payment was successful
            message: Descriptive message about the result
            transaction_id: Optional transaction identifier
        """
        self.success = success
        self.message = message
        self.transaction_id = transaction_id
    
    def __str__(self) -> str:
        """Return string representation of the result."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{status}] {self.message}"


class PaymentProcessor(ABC):
    """Abstract base class for payment processors."""
    
    def __init__(self, timeout: int = ProcessorConfig.DEFAULT_TIMEOUT):
        """Initialize payment processor.
        
        Args:
            timeout: Timeout for payment operations in seconds
        """
        self.timeout = timeout
    
    @abstractmethod
    def process_payment(self, amount: Decimal) -> PaymentResult:
        """Process payment and return result.
        
        Args:
            amount: Payment amount to process
            
        Returns:
            PaymentResult: Result of the payment processing
            
        Raises:
            PaymentProcessingError: If payment processing fails
        """
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        """Return the name of this processor."""
        pass
    
    def _format_amount(self, amount: Decimal) -> str:
        """Format amount for display."""
        return f"${amount:.{PaymentConfig.CURRENCY_PRECISION}f}"


class PayPalProcessor(PaymentProcessor):
    """PayPal payment processor implementation."""
    
    def __init__(self):
        """Initialize PayPal processor with specific timeout."""
        super().__init__(timeout=ProcessorConfig.PAYPAL_TIMEOUT)
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "PayPal"
    
    def process_payment(self, amount: Decimal) -> PaymentResult:
        """Process PayPal payment.
        
        Args:
            amount: Payment amount
            
        Returns:
            PaymentResult: Processing result
        """
        try:
            # TODO: Integrate with actual PayPal API
            logger.info(f"Processing PayPal payment of {self._format_amount(amount)}")
            
            # Simulate successful processing
            message = PaymentConfig.PAYMENT_SUCCESS_TEMPLATE.format(
                payment_type="PayPal",
                amount=amount
            )
            
            # Generate mock transaction ID
            transaction_id = f"PP_{hash(str(amount)) % 100000:05d}"
            
            return PaymentResult(True, message, transaction_id)
            
        except Exception as e:
            logger.error(f"PayPal payment failed: {str(e)}")
            raise PaymentProcessingError(f"PayPal payment failed: {str(e)}", "PayPal")


class GooglePayProcessor(PaymentProcessor):
    """GooglePay payment processor implementation."""
    
    def __init__(self):
        """Initialize GooglePay processor with specific timeout."""
        super().__init__(timeout=ProcessorConfig.GOOGLEPAY_TIMEOUT)
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "GooglePay"
    
    def process_payment(self, amount: Decimal) -> PaymentResult:
        """Process GooglePay payment.
        
        Args:
            amount: Payment amount
            
        Returns:
            PaymentResult: Processing result
        """
        try:
            # TODO: Integrate with actual GooglePay API
            logger.info(f"Processing GooglePay payment of {self._format_amount(amount)}")
            
            # Simulate successful processing
            message = PaymentConfig.PAYMENT_SUCCESS_TEMPLATE.format(
                payment_type="GooglePay",
                amount=amount
            )
            
            # Generate mock transaction ID
            transaction_id = f"GP_{hash(str(amount)) % 100000:05d}"
            
            return PaymentResult(True, message, transaction_id)
            
        except Exception as e:
            logger.error(f"GooglePay payment failed: {str(e)}")
            raise PaymentProcessingError(f"GooglePay payment failed: {str(e)}", "GooglePay")


class CreditCardProcessor(PaymentProcessor):
    """Credit Card payment processor implementation."""
    
    def __init__(self):
        """Initialize Credit Card processor with specific timeout."""
        super().__init__(timeout=ProcessorConfig.CREDITCARD_TIMEOUT)
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "Credit Card"
    
    def process_payment(self, amount: Decimal) -> PaymentResult:
        """Process Credit Card payment.
        
        Args:
            amount: Payment amount
            
        Returns:
            PaymentResult: Processing result
        """
        try:
            # TODO: Integrate with actual Credit Card API
            logger.info(f"Processing Credit Card payment of {self._format_amount(amount)}")
            
            # Simulate successful processing
            message = PaymentConfig.PAYMENT_SUCCESS_TEMPLATE.format(
                payment_type="Credit Card",
                amount=amount
            )
            
            # Generate mock transaction ID
            transaction_id = f"CC_{hash(str(amount)) % 100000:05d}"
            
            return PaymentResult(True, message, transaction_id)
            
        except Exception as e:
            logger.error(f"Credit Card payment failed: {str(e)}")
            raise PaymentProcessingError(f"Credit Card payment failed: {str(e)}", "Credit Card")


class AmountValidator:
    """Validator for payment amounts."""
    
    @staticmethod
    def validate(amount) -> Decimal:
        """Validate and convert payment amount to Decimal.
        
        Args:
            amount: Amount to validate (can be int, float, or Decimal)
            
        Returns:
            Decimal: Validated amount
            
        Raises:
            InvalidAmountError: If amount is invalid
        """
        # Type validation
        if not isinstance(amount, (int, float, Decimal, str)):
            raise InvalidAmountError(amount, PaymentConfig.INVALID_AMOUNT_TYPE_ERROR)
        
        # Convert to Decimal for precise calculations
        try:
            decimal_amount = Decimal(str(amount))
        except (ValueError, InvalidOperation):
            raise InvalidAmountError(amount, PaymentConfig.INVALID_AMOUNT_TYPE_ERROR)
        
        # Range validation
        if decimal_amount < PaymentConfig.MIN_PAYMENT_AMOUNT:
            raise InvalidAmountError(amount, PaymentConfig.AMOUNT_TOO_LOW_ERROR)
        
        if decimal_amount > PaymentConfig.MAX_PAYMENT_AMOUNT:
            raise InvalidAmountError(amount, PaymentConfig.AMOUNT_TOO_HIGH_ERROR)
        
        # Round to appropriate precision
        return decimal_amount.quantize(Decimal('0.01'))


class CheckoutService:
    """Service class for handling checkout operations with improved architecture."""
    
    def __init__(self):
        """Initialize checkout service with payment processors."""
        self._processors: Dict[PaymentMode, PaymentProcessor] = {
            PaymentMode.PAYPAL: PayPalProcessor(),
            PaymentMode.GOOGLEPAY: GooglePayProcessor(),
            PaymentMode.CREDITCARD: CreditCardProcessor(),
        }
        self._amount_validator = AmountValidator()
        
        logger.info("CheckoutService initialized with processors: %s", 
                   list(self._processors.keys()))
    
    def checkout(self, mode: PaymentMode, amount) -> PaymentResult:
        """Process the payment based on the selected PaymentMode.
        
        Args:
            mode: The payment mode to use
            amount: The payment amount (will be converted to Decimal)
            
        Returns:
            PaymentResult: Result of the payment processing
            
        Raises:
            InvalidPaymentModeError: If payment mode is invalid
            InvalidAmountError: If amount is invalid
            ProcessorNotFoundError: If no processor found for mode
            PaymentProcessingError: If payment processing fails
        """
        # Validate payment mode
        if not PaymentMode.is_valid(mode):
            logger.warning(f"Invalid payment mode attempted: {mode}")
            raise InvalidPaymentModeError(str(mode))
        
        # Validate and convert amount
        validated_amount = self._amount_validator.validate(amount)
        
        # Get processor
        processor = self._get_processor(mode)
        
        # Process payment
        logger.info(f"Processing payment: {mode.name}, amount: ${validated_amount}")
        return processor.process_payment(validated_amount)
    
    def _get_processor(self, mode: PaymentMode) -> PaymentProcessor:
        """Get processor for given payment mode.
        
        Args:
            mode: Payment mode
            
        Returns:
            PaymentProcessor: Processor for the mode
            
        Raises:
            ProcessorNotFoundError: If no processor found
        """
        if mode not in self._processors:
            raise ProcessorNotFoundError(mode.name)
        return self._processors[mode]
    
    def get_supported_payment_modes(self) -> List[PaymentMode]:
        """Get list of supported payment modes.
        
        Returns:
            List[PaymentMode]: List of supported payment modes
        """
        return list(self._processors.keys())
    
    def add_processor(self, mode: PaymentMode, processor: PaymentProcessor) -> None:
        """Add a new payment processor.
        
        Args:
            mode: Payment mode
            processor: Payment processor instance
        """
        self._processors[mode] = processor
        logger.info(f"Added processor for {mode.name}: {processor.processor_name}")


# Legacy class for backward compatibility
class Checkout:
    """Legacy checkout class - deprecated, use CheckoutService instead."""
    
    def __init__(self):
        """Initialize legacy checkout with new service."""
        self._service = CheckoutService()
        logger.warning("Using deprecated Checkout class. Consider migrating to CheckoutService.")
    
    def checkout(self, mode: PaymentMode, amount) -> bool:
        """Legacy checkout method.
        
        Args:
            mode: Payment mode
            amount: Payment amount
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self._service.checkout(mode, amount)
            print(result.message)
            return result.success
        except PaymentError as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in legacy checkout: {e}")
            print(f"Error: An unexpected error occurred")
            return False