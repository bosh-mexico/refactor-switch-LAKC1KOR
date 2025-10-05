"""
Unit tests for the Payment Processing System.

This module contains comprehensive unit tests for the PaymentProcessor class
and related functionality, ensuring proper behavior for all payment modes
and error conditions.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import the payment_processor module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from payment_processor import PaymentProcessor, PaymentMode, checkout


class TestPaymentMode(unittest.TestCase):
    """Test cases for the PaymentMode enum."""
    
    def test_payment_mode_values(self):
        """Test that PaymentMode enum has correct values."""
        self.assertEqual(PaymentMode.PAYPAL.value, "PayPal")
        self.assertEqual(PaymentMode.GOOGLEPAY.value, "GooglePay")
        self.assertEqual(PaymentMode.CREDITCARD.value, "CreditCard")
    
    def test_payment_mode_count(self):
        """Test that PaymentMode enum has exactly 3 members."""
        self.assertEqual(len(PaymentMode), 3)


class TestPaymentProcessor(unittest.TestCase):
    """Test cases for the PaymentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = PaymentProcessor()
        self.test_amount = 100.50
    
    def tearDown(self):
        """Clean up after each test method."""
        self.processor.clear_transaction_history()
    
    def test_processor_initialization(self):
        """Test that PaymentProcessor initializes correctly."""
        processor = PaymentProcessor()
        self.assertIsInstance(processor.transaction_log, list)
        self.assertEqual(len(processor.transaction_log), 0)
    
    def test_successful_paypal_payment(self):
        """Test successful PayPal payment processing."""
        result = self.processor.checkout(PaymentMode.PAYPAL, self.test_amount)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], self.test_amount)
        self.assertEqual(result["payment_mode"], "PayPal")
        self.assertIsNotNone(result["transaction_id"])
        self.assertIn("PayPal payment", result["message"])
    
    def test_successful_googlepay_payment(self):
        """Test successful GooglePay payment processing."""
        result = self.processor.checkout(PaymentMode.GOOGLEPAY, self.test_amount)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], self.test_amount)
        self.assertEqual(result["payment_mode"], "GooglePay")
        self.assertIsNotNone(result["transaction_id"])
        self.assertIn("GooglePay payment", result["message"])
    
    def test_successful_creditcard_payment(self):
        """Test successful Credit Card payment processing."""
        result = self.processor.checkout(PaymentMode.CREDITCARD, self.test_amount)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], self.test_amount)
        self.assertEqual(result["payment_mode"], "CreditCard")
        self.assertIsNotNone(result["transaction_id"])
        self.assertIn("Credit Card payment", result["message"])
    
    def test_invalid_payment_mode_type(self):
        """Test that invalid payment mode type raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.processor.checkout("invalid_mode", self.test_amount)
        
        self.assertIn("Payment mode must be a PaymentMode enum", str(context.exception))
    
    def test_negative_amount(self):
        """Test that negative amount raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.processor.checkout(PaymentMode.PAYPAL, -10.0)
        
        self.assertIn("Amount must be positive", str(context.exception))
    
    def test_zero_amount(self):
        """Test that zero amount raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.processor.checkout(PaymentMode.PAYPAL, 0.0)
        
        self.assertIn("Amount must be positive", str(context.exception))
    
    def test_invalid_amount_type(self):
        """Test that invalid amount type raises TypeError."""
        with self.assertRaises(TypeError) as context:
            self.processor.checkout(PaymentMode.PAYPAL, "invalid_amount")
        
        self.assertIn("Amount must be a number", str(context.exception))
    
    def test_transaction_id_uniqueness(self):
        """Test that transaction IDs are unique."""
        result1 = self.processor.checkout(PaymentMode.PAYPAL, self.test_amount)
        result2 = self.processor.checkout(PaymentMode.GOOGLEPAY, self.test_amount)
        
        self.assertNotEqual(result1["transaction_id"], result2["transaction_id"])
    
    def test_transaction_logging(self):
        """Test that transactions are properly logged."""
        # Initially, transaction log should be empty
        self.assertEqual(len(self.processor.get_transaction_history()), 0)
        
        # Process a payment
        self.processor.checkout(PaymentMode.PAYPAL, self.test_amount)
        
        # Check that transaction was logged
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["payment_mode"], "PayPal")
        self.assertEqual(history[0]["amount"], self.test_amount)
    
    def test_multiple_transactions_logging(self):
        """Test that multiple transactions are properly logged."""
        # Process multiple payments
        self.processor.checkout(PaymentMode.PAYPAL, 50.0)
        self.processor.checkout(PaymentMode.GOOGLEPAY, 75.0)
        self.processor.checkout(PaymentMode.CREDITCARD, 100.0)
        
        # Check transaction history
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), 3)
        
        # Verify order and details
        self.assertEqual(history[0]["payment_mode"], "PayPal")
        self.assertEqual(history[0]["amount"], 50.0)
        self.assertEqual(history[1]["payment_mode"], "GooglePay")
        self.assertEqual(history[1]["amount"], 75.0)
        self.assertEqual(history[2]["payment_mode"], "CreditCard")
        self.assertEqual(history[2]["amount"], 100.0)
    
    def test_clear_transaction_history(self):
        """Test that transaction history can be cleared."""
        # Process some payments
        self.processor.checkout(PaymentMode.PAYPAL, self.test_amount)
        self.processor.checkout(PaymentMode.GOOGLEPAY, self.test_amount)
        
        # Verify transactions exist
        self.assertEqual(len(self.processor.get_transaction_history()), 2)
        
        # Clear history
        self.processor.clear_transaction_history()
        
        # Verify history is empty
        self.assertEqual(len(self.processor.get_transaction_history()), 0)
    
    def test_transaction_history_immutability(self):
        """Test that returned transaction history is a copy (immutable)."""
        self.processor.checkout(PaymentMode.PAYPAL, self.test_amount)
        
        history1 = self.processor.get_transaction_history()
        history2 = self.processor.get_transaction_history()
        
        # Modifying one copy should not affect the other
        history1.append({"test": "data"})
        
        self.assertNotEqual(len(history1), len(history2))
        self.assertEqual(len(history2), 1)  # Original length
    
    @patch('builtins.print')
    def test_console_output_success(self, mock_print):
        """Test that successful payments print correct confirmation messages."""
        self.processor.checkout(PaymentMode.PAYPAL, self.test_amount)
        
        # Check that print was called with the correct messages
        calls = mock_print.call_args_list
        self.assertEqual(len(calls), 2)  # Two print statements expected
        
        # Check the payment confirmation message
        self.assertIn("Processing PayPal payment of $100.50", calls[0][0][0])
        
        # Check the transaction ID message
        self.assertIn("Transaction ID:", calls[1][0][0])
    
    @patch('builtins.print')
    def test_console_output_error(self, mock_print):
        """Test that error cases print correct error messages."""
        try:
            self.processor.checkout(PaymentMode.PAYPAL, -10.0)
        except ValueError:
            pass  # Expected error
        
        # For error cases, no print should occur since exception is raised
        mock_print.assert_not_called()
    
    def test_integer_amount(self):
        """Test that integer amounts work correctly."""
        result = self.processor.checkout(PaymentMode.PAYPAL, 100)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], 100)
    
    def test_float_amount(self):
        """Test that float amounts work correctly."""
        result = self.processor.checkout(PaymentMode.PAYPAL, 99.99)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], 99.99)
    
    def test_large_amount(self):
        """Test processing of large amounts."""
        large_amount = 999999.99
        result = self.processor.checkout(PaymentMode.CREDITCARD, large_amount)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], large_amount)
    
    def test_small_amount(self):
        """Test processing of very small amounts."""
        small_amount = 0.01
        result = self.processor.checkout(PaymentMode.GOOGLEPAY, small_amount)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], small_amount)


class TestConvenienceFunction(unittest.TestCase):
    """Test cases for the convenience checkout function."""
    
    def test_convenience_function_success(self):
        """Test that the convenience checkout function works correctly."""
        result = checkout(PaymentMode.PAYPAL, 50.0)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["amount"], 50.0)
        self.assertEqual(result["payment_mode"], "PayPal")
    
    def test_convenience_function_error(self):
        """Test that the convenience checkout function handles errors correctly."""
        with self.assertRaises(ValueError):
            checkout(PaymentMode.PAYPAL, -10.0)


class TestErrorHandling(unittest.TestCase):
    """Test cases for comprehensive error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PaymentProcessor()
    
    def test_none_payment_mode(self):
        """Test that None payment mode raises TypeError."""
        with self.assertRaises(TypeError):
            self.processor.checkout(None, 100.0)
    
    def test_none_amount(self):
        """Test that None amount raises TypeError."""
        with self.assertRaises(TypeError):
            self.processor.checkout(PaymentMode.PAYPAL, None)
    
    def test_string_amount(self):
        """Test that string amount raises TypeError."""
        with self.assertRaises(TypeError):
            self.processor.checkout(PaymentMode.PAYPAL, "100.0")
    
    def test_list_amount(self):
        """Test that list amount raises TypeError."""
        with self.assertRaises(TypeError):
            self.processor.checkout(PaymentMode.PAYPAL, [100.0])


if __name__ == "__main__":
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPaymentMode,
        TestPaymentProcessor,
        TestConvenienceFunction,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")