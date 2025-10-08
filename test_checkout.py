"""Comprehensive unit tests for the payment checkout system."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from payment_mode import PaymentMode
from checkout import (
    CheckoutService, Checkout, PayPalProcessor, GooglePayProcessor, 
    CreditCardProcessor, PaymentResult, AmountValidator
)
from exceptions import (
    PaymentError, InvalidPaymentModeError, InvalidAmountError,
    PaymentProcessingError, ProcessorNotFoundError
)
from config import PaymentConfig


class TestPaymentMode(unittest.TestCase):
    """Test cases for PaymentMode enum."""
    
    def test_payment_mode_values_exist(self):
        """Test that all expected payment modes exist."""
        expected_modes = ['PAYPAL', 'GOOGLEPAY', 'CREDITCARD']
        actual_modes = [mode.name for mode in PaymentMode]
        
        for expected in expected_modes:
            self.assertIn(expected, actual_modes)
    
    def test_is_valid_with_valid_modes(self):
        """Test is_valid method with valid payment modes."""
        for mode in PaymentMode:
            self.assertTrue(PaymentMode.is_valid(mode))
    
    def test_is_valid_with_invalid_modes(self):
        """Test is_valid method with invalid payment modes."""
        invalid_modes = ["BITCOIN", 123, None, [], {}]
        
        for invalid_mode in invalid_modes:
            with self.subTest(mode=invalid_mode):
                self.assertFalse(PaymentMode.is_valid(invalid_mode))
    
    def test_from_string_valid(self):
        """Test from_string method with valid strings."""
        test_cases = [
            ("PAYPAL", PaymentMode.PAYPAL),
            ("paypal", PaymentMode.PAYPAL),
            ("PayPal", PaymentMode.PAYPAL),
            ("GOOGLEPAY", PaymentMode.GOOGLEPAY),
            ("CREDITCARD", PaymentMode.CREDITCARD),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                result = PaymentMode.from_string(input_str)
                self.assertEqual(result, expected)
    
    def test_from_string_invalid(self):
        """Test from_string method with invalid strings."""
        invalid_strings = ["BITCOIN", "CASH", "INVALID", ""]
        
        for invalid_str in invalid_strings:
            with self.subTest(input_str=invalid_str):
                with self.assertRaises(ValueError):
                    PaymentMode.from_string(invalid_str)
    
    def test_string_representation(self):
        """Test string representation of payment modes."""
        expected_representations = {
            PaymentMode.PAYPAL: "Paypal",
            PaymentMode.GOOGLEPAY: "Googlepay",
            PaymentMode.CREDITCARD: "Creditcard",
        }
        
        for mode, expected_str in expected_representations.items():
            with self.subTest(mode=mode):
                self.assertEqual(str(mode), expected_str)


class TestPaymentResult(unittest.TestCase):
    """Test cases for PaymentResult class."""
    
    def test_payment_result_creation(self):
        """Test PaymentResult creation and properties."""
        result = PaymentResult(True, "Success message", "TXN123")
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success message")
        self.assertEqual(result.transaction_id, "TXN123")
    
    def test_payment_result_without_transaction_id(self):
        """Test PaymentResult creation without transaction ID."""
        result = PaymentResult(False, "Error message")
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Error message")
        self.assertIsNone(result.transaction_id)
    
    def test_payment_result_string_representation(self):
        """Test string representation of PaymentResult."""
        success_result = PaymentResult(True, "Payment processed")
        failure_result = PaymentResult(False, "Payment failed")
        
        self.assertEqual(str(success_result), "[SUCCESS] Payment processed")
        self.assertEqual(str(failure_result), "[FAILED] Payment failed")


class TestAmountValidator(unittest.TestCase):
    """Test cases for AmountValidator."""
    
    def test_validate_valid_amounts(self):
        """Test validation of valid amounts."""
        valid_amounts = [
            (100.50, Decimal("100.50")),
            (Decimal("75.25"), Decimal("75.25")),
            ("150.00", Decimal("150.00")),
            (1, Decimal("1.00")),
            (0.01, Decimal("0.01")),  # Minimum valid amount
        ]
        
        for input_amount, expected in valid_amounts:
            with self.subTest(amount=input_amount):
                result = AmountValidator.validate(input_amount)
                self.assertEqual(result, expected)
    
    def test_validate_invalid_amounts(self):
        """Test validation of invalid amounts."""
        invalid_amounts = [
            0,           # Too low
            -10,         # Negative
            0.001,       # Below minimum
            1000000,     # Too high
            "invalid",   # Not a number
            None,        # None type
            [],          # Wrong type
        ]
        
        for invalid_amount in invalid_amounts:
            with self.subTest(amount=invalid_amount):
                with self.assertRaises(InvalidAmountError):
                    AmountValidator.validate(invalid_amount)
    
    def test_validate_precision_rounding(self):
        """Test that amounts are rounded to correct precision."""
        test_cases = [
            (100.123, Decimal("100.12")),
            (99.999, Decimal("100.00")),
            (150.555, Decimal("150.56")),
        ]
        
        for input_amount, expected in test_cases:
            with self.subTest(amount=input_amount):
                result = AmountValidator.validate(input_amount)
                self.assertEqual(result, expected)


class TestPaymentProcessors(unittest.TestCase):
    """Test cases for payment processors."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_amount = Decimal("100.50")
    
    def test_paypal_processor(self):
        """Test PayPal processor."""
        processor = PayPalProcessor()
        
        self.assertEqual(processor.processor_name, "PayPal")
        
        result = processor.process_payment(self.test_amount)
        
        self.assertIsInstance(result, PaymentResult)
        self.assertTrue(result.success)
        self.assertIn("PayPal", result.message)
        self.assertIn("100.50", result.message)
        self.assertIsNotNone(result.transaction_id)
        self.assertTrue(result.transaction_id.startswith("PP_"))
    
    def test_googlepay_processor(self):
        """Test GooglePay processor."""
        processor = GooglePayProcessor()
        
        self.assertEqual(processor.processor_name, "GooglePay")
        
        result = processor.process_payment(self.test_amount)
        
        self.assertIsInstance(result, PaymentResult)
        self.assertTrue(result.success)
        self.assertIn("GooglePay", result.message)
        self.assertIn("100.50", result.message)
        self.assertIsNotNone(result.transaction_id)
        self.assertTrue(result.transaction_id.startswith("GP_"))
    
    def test_creditcard_processor(self):
        """Test Credit Card processor."""
        processor = CreditCardProcessor()
        
        self.assertEqual(processor.processor_name, "Credit Card")
        
        result = processor.process_payment(self.test_amount)
        
        self.assertIsInstance(result, PaymentResult)
        self.assertTrue(result.success)
        self.assertIn("Credit Card", result.message)
        self.assertIn("100.50", result.message)
        self.assertIsNotNone(result.transaction_id)
        self.assertTrue(result.transaction_id.startswith("CC_"))
    
    @patch('checkout.logger')
    def test_processor_exception_handling(self, mock_logger):
        """Test processor exception handling."""
        processor = PayPalProcessor()
        
        # Mock the payment processing to raise an exception
        with patch.object(processor, '_format_amount', side_effect=Exception("API Error")):
            with self.assertRaises(PaymentProcessingError):
                processor.process_payment(self.test_amount)
            
            # Verify error was logged
            mock_logger.error.assert_called()


class TestCheckoutService(unittest.TestCase):
    """Test cases for CheckoutService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checkout_service = CheckoutService()
        self.test_amount = Decimal("150.75")
    
    def test_initialization(self):
        """Test CheckoutService initialization."""
        supported_modes = self.checkout_service.get_supported_payment_modes()
        
        expected_modes = [PaymentMode.PAYPAL, PaymentMode.GOOGLEPAY, PaymentMode.CREDITCARD]
        
        for mode in expected_modes:
            self.assertIn(mode, supported_modes)
    
    def test_successful_checkout(self):
        """Test successful checkout for all supported modes."""
        for mode in self.checkout_service.get_supported_payment_modes():
            with self.subTest(mode=mode):
                result = self.checkout_service.checkout(mode, self.test_amount)
                
                self.assertIsInstance(result, PaymentResult)
                self.assertTrue(result.success)
                self.assertIn(str(self.test_amount), result.message)
                self.assertIsNotNone(result.transaction_id)
    
    def test_checkout_with_invalid_payment_mode(self):
        """Test checkout with invalid payment mode."""
        with self.assertRaises(InvalidPaymentModeError):
            self.checkout_service.checkout("BITCOIN", self.test_amount)
    
    def test_checkout_with_invalid_amount(self):
        """Test checkout with invalid amounts."""
        invalid_amounts = [0, -10, "invalid", None]
        
        for invalid_amount in invalid_amounts:
            with self.subTest(amount=invalid_amount):
                with self.assertRaises(InvalidAmountError):
                    self.checkout_service.checkout(PaymentMode.PAYPAL, invalid_amount)
    
    def test_add_processor(self):
        """Test adding a new payment processor."""
        # Create a mock processor
        mock_processor = Mock(spec=PayPalProcessor)
        mock_processor.processor_name = "Test Processor"
        
        # Create a new payment mode for testing (would normally be in the enum)
        test_mode = PaymentMode.PAYPAL  # Using existing mode for simplicity
        
        # Add the processor
        self.checkout_service.add_processor(test_mode, mock_processor)
        
        # Verify it was added
        processor = self.checkout_service._get_processor(test_mode)
        self.assertEqual(processor, mock_processor)
    
    def test_get_processor_not_found(self):
        """Test getting processor for unsupported mode."""
        # Remove all processors to test error case
        self.checkout_service._processors.clear()
        
        with self.assertRaises(ProcessorNotFoundError):
            self.checkout_service._get_processor(PaymentMode.PAYPAL)


class TestLegacyCheckout(unittest.TestCase):
    """Test cases for legacy Checkout class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checkout = Checkout()
        self.test_amount = Decimal("99.99")
    
    @patch('builtins.print')
    def test_successful_legacy_checkout(self, mock_print):
        """Test successful legacy checkout."""
        result = self.checkout.checkout(PaymentMode.PAYPAL, self.test_amount)
        
        self.assertTrue(result)
        mock_print.assert_called()
        
        # Verify the printed message contains expected content
        printed_message = mock_print.call_args[0][0]
        self.assertIn("PayPal", printed_message)
        self.assertIn(str(self.test_amount), printed_message)
    
    @patch('builtins.print')
    def test_legacy_checkout_with_invalid_mode(self, mock_print):
        """Test legacy checkout with invalid payment mode."""
        result = self.checkout.checkout("INVALID", self.test_amount)
        
        self.assertFalse(result)
        mock_print.assert_called()
        
        # Verify error message was printed
        printed_message = mock_print.call_args[0][0]
        self.assertIn("Error", printed_message)
    
    @patch('builtins.print')
    def test_legacy_checkout_with_invalid_amount(self, mock_print):
        """Test legacy checkout with invalid amount."""
        result = self.checkout.checkout(PaymentMode.PAYPAL, -100)
        
        self.assertFalse(result)
        mock_print.assert_called()
        
        # Verify error message was printed
        printed_message = mock_print.call_args[0][0]
        self.assertIn("Error", printed_message)


class TestExceptionHandling(unittest.TestCase):
    """Test cases for exception handling."""
    
    def test_invalid_payment_mode_error(self):
        """Test InvalidPaymentModeError."""
        error = InvalidPaymentModeError("BITCOIN")
        
        self.assertEqual(error.error_code, "INVALID_PAYMENT_MODE")
        self.assertEqual(error.invalid_mode, "BITCOIN")
        self.assertIn("BITCOIN", str(error))
    
    def test_invalid_amount_error(self):
        """Test InvalidAmountError."""
        error = InvalidAmountError(-100, "Amount must be positive")
        
        self.assertEqual(error.error_code, "INVALID_AMOUNT")
        self.assertEqual(error.invalid_amount, -100)
        self.assertIn("-100", str(error))
        self.assertIn("Amount must be positive", str(error))
    
    def test_payment_processing_error(self):
        """Test PaymentProcessingError."""
        error = PaymentProcessingError("API failure", "PayPal")
        
        self.assertEqual(error.error_code, "PROCESSING_FAILED")
        self.assertEqual(error.payment_mode, "PayPal")
        self.assertIn("API failure", str(error))
    
    def test_processor_not_found_error(self):
        """Test ProcessorNotFoundError."""
        error = ProcessorNotFoundError("BITCOIN")
        
        self.assertEqual(error.error_code, "PROCESSOR_NOT_FOUND")
        self.assertEqual(error.payment_mode, "BITCOIN")
        self.assertIn("BITCOIN", str(error))


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration constants."""
    
    def test_payment_config_constants(self):
        """Test that payment configuration constants are properly defined."""
        self.assertIsInstance(PaymentConfig.MIN_PAYMENT_AMOUNT, Decimal)
        self.assertIsInstance(PaymentConfig.MAX_PAYMENT_AMOUNT, Decimal)
        self.assertIsInstance(PaymentConfig.CURRENCY_PRECISION, int)
        
        # Verify minimum is less than maximum
        self.assertLess(PaymentConfig.MIN_PAYMENT_AMOUNT, PaymentConfig.MAX_PAYMENT_AMOUNT)
        
        # Verify precision is reasonable
        self.assertEqual(PaymentConfig.CURRENCY_PRECISION, 2)
    
    def test_error_message_constants(self):
        """Test that error message constants are strings."""
        error_messages = [
            PaymentConfig.INVALID_PAYMENT_MODE_ERROR,
            PaymentConfig.INVALID_AMOUNT_TYPE_ERROR,
            PaymentConfig.AMOUNT_TOO_LOW_ERROR,
            PaymentConfig.AMOUNT_TOO_HIGH_ERROR,
            PaymentConfig.PROCESSOR_NOT_FOUND_ERROR,
        ]
        
        for message in error_messages:
            self.assertIsInstance(message, str)
            self.assertTrue(len(message) > 0)


if __name__ == "__main__":
    # Configure test runner for better output
    unittest.main(
        verbosity=2,
        buffer=True,  # Capture print statements during tests
        failfast=False,  # Continue running tests after failures
    )


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_end_to_end_checkout_flow(self):
        """Test complete checkout flow."""
        checkout_service = CheckoutService()
        
        # Test each supported payment mode
        for mode in checkout_service.get_supported_payment_modes():
            result = checkout_service.checkout(mode, 100.00)
            self.assertTrue(result.success, f"Checkout failed for {mode}")
            self.assertIn("100.00", result.message)


if __name__ == "__main__":
    # Configure test runner for better output
    unittest.main(
        verbosity=2,
        buffer=True,  # Capture print statements during tests
        failfast=False,  # Continue running tests after failures
    )