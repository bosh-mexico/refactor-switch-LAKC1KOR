"""
Integration tests for the Payment Processing System.

This module contains integration tests that test the payment processing system
as a whole, including end-to-end scenarios and interactions between components.
"""

import unittest
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path to import the payment_processor module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from payment_processor import PaymentProcessor, PaymentMode


class TestPaymentProcessorIntegration(unittest.TestCase):
    """Integration tests for the PaymentProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PaymentProcessor()
    
    def test_complete_payment_workflow(self):
        """Test a complete payment processing workflow."""
        # Test data
        test_payments = [
            (PaymentMode.PAYPAL, 100.0),
            (PaymentMode.GOOGLEPAY, 250.50),
            (PaymentMode.CREDITCARD, 75.25),
            (PaymentMode.PAYPAL, 500.0)
        ]
        
        # Process all payments
        results = []
        for mode, amount in test_payments:
            result = self.processor.checkout(mode, amount)
            results.append(result)
        
        # Verify all payments were successful
        for result in results:
            self.assertEqual(result["status"], "success")
            self.assertIsNotNone(result["transaction_id"])
        
        # Verify transaction history
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), 4)
        
        # Verify amounts and payment modes
        expected_data = [
            ("PayPal", 100.0),
            ("GooglePay", 250.50),
            ("CreditCard", 75.25),
            ("PayPal", 500.0)
        ]
        
        for i, (expected_mode, expected_amount) in enumerate(expected_data):
            self.assertEqual(history[i]["payment_mode"], expected_mode)
            self.assertEqual(history[i]["amount"], expected_amount)
            self.assertEqual(history[i]["status"], "success")
    
    def test_mixed_success_and_error_scenarios(self):
        """Test scenarios with both successful and failed payments."""
        # Successful payment
        success_result = self.processor.checkout(PaymentMode.PAYPAL, 100.0)
        self.assertEqual(success_result["status"], "success")
        
        # Failed payment (will raise exception, but we'll catch it)
        try:
            self.processor.checkout(PaymentMode.GOOGLEPAY, -50.0)
        except ValueError:
            pass  # Expected
        
        # Another successful payment
        success_result2 = self.processor.checkout(PaymentMode.CREDITCARD, 200.0)
        self.assertEqual(success_result2["status"], "success")
        
        # Verify only successful payments are in history
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), 2)
        
        # Verify all logged transactions are successful
        for transaction in history:
            self.assertEqual(transaction["status"], "success")
    
    @patch('builtins.print')
    def test_console_output_integration(self, mock_print):
        """Test that console output works correctly across multiple payments."""
        # Process multiple payments
        payments = [
            (PaymentMode.PAYPAL, 100.0),
            (PaymentMode.GOOGLEPAY, 200.0)
        ]
        
        for mode, amount in payments:
            self.processor.checkout(mode, amount)
        
        # Verify correct number of print calls
        # Each successful payment should result in 2 print calls
        self.assertEqual(len(mock_print.call_args_list), 4)
        
        # Verify content of print calls
        calls = [call[0][0] for call in mock_print.call_args_list]
        
        # Check PayPal payment messages
        self.assertIn("Processing PayPal payment of $100.00", calls[0])
        self.assertIn("Transaction ID:", calls[1])
        
        # Check GooglePay payment messages
        self.assertIn("Processing GooglePay payment of $200.00", calls[2])
        self.assertIn("Transaction ID:", calls[3])
    
    def test_transaction_id_format_and_uniqueness(self):
        """Test that transaction IDs follow the expected format and are unique."""
        # Process multiple payments
        results = []
        for _ in range(10):
            result = self.processor.checkout(PaymentMode.PAYPAL, 100.0)
            results.append(result)
        
        transaction_ids = [result["transaction_id"] for result in results]
        
        # Verify all transaction IDs are unique
        self.assertEqual(len(transaction_ids), len(set(transaction_ids)))
        
        # Verify transaction ID format (should start with "TXN_" and be followed by 8 characters)
        for txn_id in transaction_ids:
            self.assertTrue(txn_id.startswith("TXN_"))
            self.assertEqual(len(txn_id), 12)  # "TXN_" + 8 characters
            # Verify the suffix is alphanumeric and uppercase
            suffix = txn_id[4:]
            self.assertTrue(suffix.isalnum())
            self.assertTrue(suffix.isupper())
    
    def test_large_volume_processing(self):
        """Test processing a large number of transactions."""
        num_transactions = 100
        
        # Process many transactions
        for i in range(num_transactions):
            mode = list(PaymentMode)[i % len(PaymentMode)]  # Cycle through payment modes
            amount = (i + 1) * 10.0  # Varying amounts
            result = self.processor.checkout(mode, amount)
            self.assertEqual(result["status"], "success")
        
        # Verify all transactions were logged
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), num_transactions)
        
        # Verify transaction details
        for i, transaction in enumerate(history):
            expected_mode = list(PaymentMode)[i % len(PaymentMode)]
            expected_amount = (i + 1) * 10.0
            
            self.assertEqual(transaction["payment_mode"], expected_mode.value)
            self.assertEqual(transaction["amount"], expected_amount)
            self.assertEqual(transaction["status"], "success")
    
    def test_processor_state_persistence(self):
        """Test that processor state persists across multiple operations."""
        # Initial state
        self.assertEqual(len(self.processor.get_transaction_history()), 0)
        
        # Process some payments
        self.processor.checkout(PaymentMode.PAYPAL, 100.0)
        self.assertEqual(len(self.processor.get_transaction_history()), 1)
        
        self.processor.checkout(PaymentMode.GOOGLEPAY, 200.0)
        self.assertEqual(len(self.processor.get_transaction_history()), 2)
        
        # Clear history
        self.processor.clear_transaction_history()
        self.assertEqual(len(self.processor.get_transaction_history()), 0)
        
        # Process more payments after clearing
        self.processor.checkout(PaymentMode.CREDITCARD, 300.0)
        self.assertEqual(len(self.processor.get_transaction_history()), 1)
    
    def test_all_payment_modes_coverage(self):
        """Test that all payment modes are properly supported."""
        amount = 150.0
        
        # Test each payment mode
        for mode in PaymentMode:
            result = self.processor.checkout(mode, amount)
            
            # Verify successful processing
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["payment_mode"], mode.value)
            self.assertEqual(result["amount"], amount)
            self.assertIsNotNone(result["transaction_id"])
            self.assertIn(mode.value, result["message"])
            self.assertIn("provider_response", result)
        
        # Verify all transactions were logged
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), len(PaymentMode))
        
        # Verify each payment mode appears exactly once
        payment_modes_in_history = [txn["payment_mode"] for txn in history]
        expected_modes = [mode.value for mode in PaymentMode]
        
        self.assertEqual(sorted(payment_modes_in_history), sorted(expected_modes))


class TestConcurrentPaymentProcessing(unittest.TestCase):
    """Test cases for concurrent payment processing scenarios."""
    
    def test_multiple_processor_instances(self):
        """Test that multiple processor instances work independently."""
        processor1 = PaymentProcessor()
        processor2 = PaymentProcessor()
        
        # Process payments with different processors
        result1 = processor1.checkout(PaymentMode.PAYPAL, 100.0)
        result2 = processor2.checkout(PaymentMode.GOOGLEPAY, 200.0)
        
        # Verify both are successful
        self.assertEqual(result1["status"], "success")
        self.assertEqual(result2["status"], "success")
        
        # Verify independent transaction histories
        history1 = processor1.get_transaction_history()
        history2 = processor2.get_transaction_history()
        
        self.assertEqual(len(history1), 1)
        self.assertEqual(len(history2), 1)
        
        self.assertEqual(history1[0]["payment_mode"], "PayPal")
        self.assertEqual(history2[0]["payment_mode"], "GooglePay")
        
        # Verify different transaction IDs
        self.assertNotEqual(result1["transaction_id"], result2["transaction_id"])


if __name__ == "__main__":
    # Run integration tests
    unittest.main(verbosity=2)