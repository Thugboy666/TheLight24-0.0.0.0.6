# TheLight24 v6 – ECOM payment adapters (simulated)
import time, uuid

class PaymentResult:
    def __init__(self, ok: bool, provider: str, ref: str, message: str=""):
        self.ok = ok
        self.provider = provider
        self.reference = ref
        self.message = message

class Payments:
    """
    Simula provider:
    - crypto: genera address finto e conferma immediata (dev mode)
    - paypal: sim stub
    - card:  sim stub
    - cod (contrassegno): approvato dal merchant nelle impostazioni
    In produzione sostituire con gateway reali.
    """
    def pay_crypto(self, amount: float, currency: str) -> PaymentResult:
        ref = f"CR-{uuid.uuid4()}"
        return PaymentResult(True, "crypto", ref, f"Tx accepted for {amount} {currency}")

    def pay_paypal(self, amount: float, currency: str) -> PaymentResult:
        ref = f"PP-{uuid.uuid4()}"
        return PaymentResult(True, "paypal", ref, "PayPal OK (sim)")

    def pay_card(self, amount: float, currency: str, brand: str="VISA") -> PaymentResult:
        ref = f"CC-{uuid.uuid4()}"
        return PaymentResult(True, brand, ref, "Card OK (sim)")

    def pay_cod(self, amount: float, currency: str) -> PaymentResult:
        ref = f"COD-{int(time.time())}"
        return PaymentResult(True, "cod", ref, "COD accepted (pay on delivery)")
