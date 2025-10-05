from payment_mode import PaymentMode
from checkout import Checkout

def run_tests():
    checkout_service = Checkout()

    print("Test 1: PayPal")
    assert checkout_service.checkout(PaymentMode.PAYPAL, 50.00) == True

    print("Test 2: GooglePay")
    assert checkout_service.checkout(PaymentMode.GOOGLEPAY, 75.25) == True

    print("Test 3: CreditCard")
    assert checkout_service.checkout(PaymentMode.CREDITCARD, 120.10) == True

    print("Test 4: Invalid mode (string)")
    assert checkout_service.checkout("BITCOIN", 100.00) == False

    print("All tests passed.")

if __name__ == "__main__":
    run_tests()