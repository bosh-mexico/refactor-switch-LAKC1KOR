"""
Performance and stress tests for the Payment Processing System.

This module contains performance tests to ensure the payment processing system
can handle load and performs efficiently under various conditions.
"""

import unittest
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add the parent directory to the path to import the payment_processor module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from payment_processor import PaymentProcessor, PaymentMode


class TestPaymentProcessorPerformance(unittest.TestCase):
    """Performance tests for the PaymentProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PaymentProcessor()
    
    def test_single_payment_performance(self):
        """Test the performance of a single payment processing."""
        start_time = time.time()
        
        result = self.processor.checkout(PaymentMode.PAYPAL, 100.0)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify successful processing
        self.assertEqual(result["status"], "success")
        
        # Verify reasonable processing time (should be under 1 second for a simple operation)
        self.assertLess(processing_time, 1.0, 
                       f"Single payment took {processing_time:.3f}s, which is too slow")
        
        print(f"Single payment processing time: {processing_time:.6f}s")
    
    def test_bulk_payment_performance(self):
        """Test the performance of processing multiple payments."""
        num_payments = 1000
        
        start_time = time.time()
        
        # Process multiple payments
        for i in range(num_payments):
            mode = list(PaymentMode)[i % len(PaymentMode)]
            amount = (i + 1) * 0.01  # Small amounts to avoid large numbers
            result = self.processor.checkout(mode, amount)
            self.assertEqual(result["status"], "success")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_payment = total_time / num_payments
        
        # Verify all payments were processed
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), num_payments)
        
        # Performance assertions
        self.assertLess(total_time, 30.0, 
                       f"Processing {num_payments} payments took {total_time:.3f}s, which is too slow")
        self.assertLess(avg_time_per_payment, 0.1, 
                       f"Average time per payment is {avg_time_per_payment:.6f}s, which is too slow")
        
        print(f"Bulk payment performance:")
        print(f"  Total time for {num_payments} payments: {total_time:.3f}s")
        print(f"  Average time per payment: {avg_time_per_payment:.6f}s")
        print(f"  Payments per second: {num_payments / total_time:.1f}")
    
    def test_memory_usage_with_large_transaction_history(self):
        """Test memory usage when maintaining a large transaction history."""
        num_transactions = 10000
        
        # Process many transactions
        for i in range(num_transactions):
            mode = PaymentMode.PAYPAL  # Use same mode for consistency
            amount = 100.0
            self.processor.checkout(mode, amount)
        
        # Verify all transactions are stored
        history = self.processor.get_transaction_history()
        self.assertEqual(len(history), num_transactions)
        
        # Test that clearing history works efficiently
        start_time = time.time()
        self.processor.clear_transaction_history()
        end_time = time.time()
        
        clear_time = end_time - start_time
        self.assertLess(clear_time, 1.0, 
                       f"Clearing {num_transactions} transactions took {clear_time:.3f}s")
        
        # Verify history is cleared
        self.assertEqual(len(self.processor.get_transaction_history()), 0)
        
        print(f"Memory management test:")
        print(f"  Processed {num_transactions} transactions")
        print(f"  History clearing time: {clear_time:.6f}s")
    
    def test_transaction_id_generation_performance(self):
        """Test the performance of transaction ID generation."""
        num_ids = 10000
        
        start_time = time.time()
        
        # Generate many transaction IDs
        transaction_ids = []
        for _ in range(num_ids):
            txn_id = self.processor._generate_transaction_id()
            transaction_ids.append(txn_id)
        
        end_time = time.time()
        generation_time = end_time - start_time
        avg_time_per_id = generation_time / num_ids
        
        # Verify all IDs are unique
        self.assertEqual(len(transaction_ids), len(set(transaction_ids)))
        
        # Performance assertions
        self.assertLess(generation_time, 5.0, 
                       f"Generating {num_ids} transaction IDs took {generation_time:.3f}s")
        self.assertLess(avg_time_per_id, 0.001, 
                       f"Average time per ID generation is {avg_time_per_id:.6f}s")
        
        print(f"Transaction ID generation performance:")
        print(f"  Total time for {num_ids} IDs: {generation_time:.3f}s")
        print(f"  Average time per ID: {avg_time_per_id:.6f}s")
        print(f"  IDs per second: {num_ids / generation_time:.1f}")


class TestConcurrentProcessing(unittest.TestCase):
    """Test concurrent payment processing scenarios."""
    
    def test_concurrent_payments_same_processor(self):
        """Test concurrent payments using the same processor instance."""
        processor = PaymentProcessor()
        num_threads = 10
        payments_per_thread = 100
        
        def process_payments(thread_id):
            """Process payments in a thread."""
            results = []
            for i in range(payments_per_thread):
                mode = list(PaymentMode)[i % len(PaymentMode)]
                amount = thread_id * 100 + i + 1
                result = processor.checkout(mode, amount)
                results.append(result)
            return results
        
        start_time = time.time()
        
        # Execute concurrent payments
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(process_payments, i) for i in range(num_threads)]
            all_results = []
            
            for future in as_completed(futures):
                thread_results = future.result()
                all_results.extend(thread_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        total_payments = num_threads * payments_per_thread
        
        # Verify all payments were successful
        for result in all_results:
            self.assertEqual(result["status"], "success")
        
        # Verify correct number of transactions
        self.assertEqual(len(all_results), total_payments)
        
        # Verify transaction history
        history = processor.get_transaction_history()
        self.assertEqual(len(history), total_payments)
        
        # Verify all transaction IDs are unique
        transaction_ids = [result["transaction_id"] for result in all_results]
        self.assertEqual(len(transaction_ids), len(set(transaction_ids)))
        
        print(f"Concurrent processing test:")
        print(f"  Threads: {num_threads}")
        print(f"  Payments per thread: {payments_per_thread}")
        print(f"  Total payments: {total_payments}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Payments per second: {total_payments / total_time:.1f}")
    
    def test_concurrent_payments_separate_processors(self):
        """Test concurrent payments using separate processor instances."""
        num_threads = 5
        payments_per_thread = 200
        
        def process_payments_separate_processor(thread_id):
            """Process payments with a separate processor instance."""
            processor = PaymentProcessor()
            results = []
            
            for i in range(payments_per_thread):
                mode = list(PaymentMode)[i % len(PaymentMode)]
                amount = thread_id * 100 + i + 1
                result = processor.checkout(mode, amount)
                results.append(result)
            
            return results, processor.get_transaction_history()
        
        start_time = time.time()
        
        # Execute concurrent payments with separate processors
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(process_payments_separate_processor, i) 
                      for i in range(num_threads)]
            
            all_results = []
            all_histories = []
            
            for future in as_completed(futures):
                thread_results, thread_history = future.result()
                all_results.extend(thread_results)
                all_histories.append(thread_history)
        
        end_time = time.time()
        total_time = end_time - start_time
        total_payments = num_threads * payments_per_thread
        
        # Verify all payments were successful
        for result in all_results:
            self.assertEqual(result["status"], "success")
        
        # Verify correct number of transactions
        self.assertEqual(len(all_results), total_payments)
        
        # Verify each processor has the correct number of transactions
        for history in all_histories:
            self.assertEqual(len(history), payments_per_thread)
        
        # Verify all transaction IDs are unique across all processors
        transaction_ids = [result["transaction_id"] for result in all_results]
        self.assertEqual(len(transaction_ids), len(set(transaction_ids)))
        
        print(f"Separate processors concurrent test:")
        print(f"  Processors: {num_threads}")
        print(f"  Payments per processor: {payments_per_thread}")
        print(f"  Total payments: {total_payments}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Payments per second: {total_payments / total_time:.1f}")


class TestStressScenarios(unittest.TestCase):
    """Stress tests for edge cases and extreme scenarios."""
    
    def test_rapid_successive_payments(self):
        """Test rapid successive payments without delays."""
        processor = PaymentProcessor()
        num_payments = 5000
        
        start_time = time.time()
        
        for i in range(num_payments):
            # Rapidly process payments without any delays
            mode = list(PaymentMode)[i % len(PaymentMode)]
            amount = 1.0  # Small fixed amount
            result = processor.checkout(mode, amount)
            self.assertEqual(result["status"], "success")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all payments were processed
        history = processor.get_transaction_history()
        self.assertEqual(len(history), num_payments)
        
        print(f"Rapid successive payments test:")
        print(f"  Payments: {num_payments}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Payments per second: {num_payments / total_time:.1f}")
    
    def test_extreme_amounts(self):
        """Test processing payments with extreme amounts."""
        processor = PaymentProcessor()
        
        # Test very large amounts
        large_amounts = [999999999.99, 1000000000.00, 9999999999.99]
        
        for amount in large_amounts:
            result = processor.checkout(PaymentMode.PAYPAL, amount)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["amount"], amount)
        
        # Test very small amounts
        small_amounts = [0.01, 0.001, 0.0001]
        
        for amount in small_amounts:
            result = processor.checkout(PaymentMode.GOOGLEPAY, amount)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["amount"], amount)
        
        print("Extreme amounts test completed successfully")
    
    def test_mixed_load_scenario(self):
        """Test mixed load with various payment modes and amounts."""
        processor = PaymentProcessor()
        num_payments = 2000
        
        start_time = time.time()
        
        for i in range(num_payments):
            # Vary payment modes and amounts
            mode = list(PaymentMode)[i % len(PaymentMode)]
            amount = (i % 1000) + 0.01  # Amounts from 0.01 to 1000.01
            
            result = processor.checkout(mode, amount)
            self.assertEqual(result["status"], "success")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all payments were processed
        history = processor.get_transaction_history()
        self.assertEqual(len(history), num_payments)
        
        # Verify distribution of payment modes
        mode_counts = {}
        for transaction in history:
            mode = transaction["payment_mode"]
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        # Each payment mode should have roughly equal distribution
        expected_count_per_mode = num_payments // len(PaymentMode)
        for mode_name, count in mode_counts.items():
            self.assertAlmostEqual(count, expected_count_per_mode, delta=2)
        
        print(f"Mixed load scenario test:")
        print(f"  Payments: {num_payments}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Payments per second: {num_payments / total_time:.1f}")
        print(f"  Payment mode distribution: {mode_counts}")


if __name__ == "__main__":
    # Run performance tests
    print("Running Payment Processor Performance Tests")
    print("=" * 50)
    
    # Create test suite for performance tests only
    test_suite = unittest.TestSuite()
    
    test_classes = [
        TestPaymentProcessorPerformance,
        TestConcurrentProcessing,
        TestStressScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run with minimal verbosity for performance focus
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 50)
    print("Performance Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 50)