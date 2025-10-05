from payment_mode import PaymentMode

class Checkout:
    def checkout(self, mode: PaymentMode, amount: float) -> bool:
        """
        Processes the payment based on the selected PaymentMode.
        Prints confirmation messages and handles unsupported modes gracefully.
        Returns True if processed, False otherwise.
        """
        if not isinstance(mode, PaymentMode):
            print("Error: Unsupported or invalid payment mode selected.")
            return False

        if mode == PaymentMode.PAYPAL:
            print(f"Processing payment via PayPal: ${amount:.2f}")
            # TODO: Integrate PayPal API here
        elif mode == PaymentMode.GOOGLEPAY:
            print(f"Processing payment via GooglePay: ${amount:.2f}")
            # TODO: Integrate GooglePay API here
        elif mode == PaymentMode.CREDITCARD:
            print(f"Processing payment via CreditCard: ${amount:.2f}")
            # TODO: Integrate CreditCard API here
        else:
            print("Error: Unsupported or invalid payment mode selected.")
            return False
        return True