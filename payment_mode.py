from enum import Enum, auto

class PaymentMode(Enum):
    PAYPAL = auto()
    GOOGLEPAY = auto()
    CREDITCARD = auto()