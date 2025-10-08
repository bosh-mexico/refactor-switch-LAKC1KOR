#!/usr/bin/env python3
"""
Main demonstration script for the Payment Checkout System.

This script demonstrates the usage of the improved checkout system with proper
error handling, logging, and clean architecture principles.
"""

import logging
from decimal import Decimal

from payment_mode import PaymentMode
from checkout import CheckoutService, Checkout
from exceptions import PaymentError, InvalidPaymentModeError, InvalidAmountError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demonstrate_checkout_service():
    """Demonstrate the new CheckoutService functionality with proper error handling."""
    print("=== CheckoutService Demonstration ===")
    
    checkout_service = CheckoutService()
    test_amount = Decimal("150.75")
    
    print(f"\nProcessing payment of ${test_amount:.2f} using different payment modes:\n")
    
    # Test all supported payment modes
    for mode in checkout_service.get_supported_payment_modes():
        try:
            result = checkout_service.checkout(mode, test_amount)
            print(f"✓ {result}")
            if result.transaction_id:
                print(f"  Transaction ID: {result.transaction_id}")
        except PaymentError as e:
            print(f"✗ Payment failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"✗ Unexpected error occurred")
        print()
    
    print("Testing error scenarios:")
    print("-" * 30)
    
    # Test invalid payment mode
    try:
        # This should raise InvalidPaymentModeError
        checkout_service.checkout("BITCOIN", test_amount)
    except InvalidPaymentModeError as e:
        print(f"✓ Expected error caught: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test invalid amounts
    invalid_amounts = [-50, 0, "invalid", 1000000, None]
    
    for amount in invalid_amounts:
        try:
            checkout_service.checkout(PaymentMode.PAYPAL, amount)
        except InvalidAmountError as e:
            print(f"✓ Invalid amount {amount} rejected: {e}")
        except Exception as e:
            print(f"✗ Unexpected error for amount {amount}: {e}")


def demonstrate_legacy_checkout():
    """Demonstrate the legacy Checkout class."""
    print("\n\n=== Legacy Checkout Demonstration ===")
    
    checkout = Checkout()
    test_amount = Decimal("99.99")
    
    print(f"\nUsing legacy checkout for payment of ${test_amount:.2f}:\n")
    
    # Test valid payment modes
    test_modes = [PaymentMode.PAYPAL, PaymentMode.GOOGLEPAY, PaymentMode.CREDITCARD]
    
    for mode in test_modes:
        success = checkout.checkout(mode, test_amount)
        status = "Success" if success else "Failed"
        print(f"Result: {status}\n")
    
    # Test invalid scenarios
    print("Testing invalid scenarios with legacy checkout:")
    print("-" * 45)
    
    # Invalid payment mode
    success = checkout.checkout("INVALID_MODE", test_amount)
    print(f"Invalid mode result: {'Success' if success else 'Failed'}")
    
    # Invalid amount
    success = checkout.checkout(PaymentMode.PAYPAL, -100)
    print(f"Invalid amount result: {'Success' if success else 'Failed'}")


def demonstrate_payment_mode_features():
    """Demonstrate PaymentMode enum features."""
    print("\n\n=== PaymentMode Features ===")
    
    print("\nAvailable Payment Modes:")
    for mode in PaymentMode:
        print(f"- {mode} (internal: {mode.name}, value: {mode.value})")
    
    print("\nPayment Mode Validation:")
    test_values = [
        PaymentMode.PAYPAL, 
        "PAYPAL", 
        123, 
        None, 
        PaymentMode.GOOGLEPAY,
        "invalid_mode"
    ]
    
    for value in test_values:
        is_valid = PaymentMode.is_valid(value)
        print(f"PaymentMode.is_valid({value!r}): {is_valid}")
    
    print("\nString conversion examples:")
    try:
        mode = PaymentMode.from_string("PAYPAL")
        print(f"from_string('PAYPAL'): {mode}")
        
        mode = PaymentMode.from_string("googlepay")  # Test case insensitive
        print(f"from_string('googlepay'): {mode}")
        
        # This should raise an error
        PaymentMode.from_string("BITCOIN")
    except ValueError as e:
        print(f"Expected error for invalid string: {e}")


def demonstrate_amount_validation():
    """Demonstrate amount validation features."""
    print("\n\n=== Amount Validation Examples ===")
    
    checkout_service = CheckoutService()
    
    test_amounts = [
        100.50,           # Valid float
        Decimal("75.25"), # Valid Decimal
        150,              # Valid integer
        "200.00",         # Valid string
        0,                # Invalid - too low
        -50,              # Invalid - negative
        "invalid",        # Invalid - not a number
        1000000,          # Invalid - too high
        0.001,            # Invalid - too low (below minimum)
    ]
    
    print("\nTesting various amount formats:")
    for amount in test_amounts:
        try:
            result = checkout_service.checkout(PaymentMode.PAYPAL, amount)
            print(f"✓ Amount {amount!r}: SUCCESS")
        except InvalidAmountError as e:
            print(f"✗ Amount {amount!r}: {e}")
        except Exception as e:
            print(f"✗ Amount {amount!r}: Unexpected error - {e}")


def main():
    """Main function to run all demonstrations."""
    print("Payment Checkout System - Clean Code Demonstration")
    print("=" * 60)
    
    try:
        demonstrate_checkout_service()
        demonstrate_legacy_checkout()
        demonstrate_payment_mode_features()
        demonstrate_amount_validation()
        
        print("\n\n=== Summary ===")
        print("✓ All demonstrations completed successfully!")
        print("\nClean Code Principles Demonstrated:")
        print("- Single Responsibility Principle (SRP)")
        print("- Open/Closed Principle (OCP)")
        print("- Dependency Inversion Principle (DIP)")
        print("- Proper error handling with custom exceptions")
        print("- Comprehensive input validation")
        print("- Configuration management")
        print("- Logging for debugging and monitoring")
        print("- Type hints for better code documentation")
        print("- Immutable configuration constants")
        print("- Precise decimal arithmetic for currency")
        print("- Extensible architecture for new payment methods")
        
    except Exception as e:
        logger.error(f"Critical error during demonstration: {e}", exc_info=True)
        print(f"\n✗ Critical error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
    checkout = Checkout()
    amount = 99.99
    
    print(f"\nUsing legacy checkout for payment of ${amount:.2f}:\n")
    
    # Test valid payment modes
    test_modes = [PaymentMode.PAYPAL, PaymentMode.GOOGLEPAY, PaymentMode.CREDITCARD]
    
    for mode in test_modes:
        success = checkout.checkout(mode, amount)
        print(f"Result: {'Success' if success else 'Failed'}\n")
    
    # Test invalid payment mode
    print("Testing invalid payment mode:")
    success = checkout.checkout("INVALID_MODE", amount)
    print(f"Result: {'Success' if success else 'Failed'}")


def demonstrate_payment_mode_features():
    """Demonstrate PaymentMode enum features."""
    print("\n\n=== PaymentMode Features ===")
    
    print("\nAvailable Payment Modes:")
    for mode in PaymentMode:
        print(f"- {mode.name} (value: {mode.value})")
    
    print("\nPayment Mode Validation:")
    test_values = [PaymentMode.PAYPAL, "PAYPAL", 123, None, PaymentMode.GOOGLEPAY]
    
    for value in test_values:
        is_valid = PaymentMode.is_valid(value)
        print(f"PaymentMode.is_valid({value}): {is_valid}")


def main():
    """Main function to run all demonstrations."""
    print("Payment Checkout System - Demonstration")
    print("=" * 50)
    
    try:
        demonstrate_checkout_service()
        demonstrate_legacy_checkout()
        demonstrate_payment_mode_features()
        
        print("\n\n=== Summary ===")
        print("✓ All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("- Clean separation of concerns with different payment processors")
        print("- Comprehensive input validation")
        print("- Proper error handling and messaging")
        print("- Both new service-oriented and legacy class-based approaches")
        print("- Extensible architecture for adding new payment methods")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()