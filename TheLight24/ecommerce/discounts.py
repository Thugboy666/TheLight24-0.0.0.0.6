# TheLight24 v6 – Coupons & Discounts
import os, json, time, uuid
from typing import Optional, Dict, Any
from .security import file_write_encrypted, file_read_encrypted

DISC_DIR = "data/commerce"
COUPON_DB = os.path.join(DISC_DIR, "coupons.enc")

def _empty():
    return {"coupons":{}}  # code -> dict

class Coupons:
    def __init__(self):
        os.makedirs(DISC_DIR, exist_ok=True)
        self.data = _empty()
    def load(self):
        self.data = file_read_encrypted(COUPON_DB, _empty())
    def save(self):
        file_write_encrypted(COUPON_DB, self.data)

    def create(self, code: str, percent: float, min_amount: float=0.0,
               shop_id: Optional[str]=None, audience: str="any",
               uses: int=0, expires_at: Optional[float]=None):
        """
        percent: 0..100
        audience: any|b2c|b2b
        uses: 0 = illimitato
        """
        code = code.upper()
        self.data["coupons"][code] = {
            "code": code,
            "percent": float(percent),
            "min_amount": float(min_amount),
            "shop_id": shop_id,
            "audience": audience,
            "uses": int(uses),
            "used": 0,
            "expires_at": float(expires_at) if expires_at else None
        }
        self.save()
        return self.data["coupons"][code]

    def list(self, shop_id: Optional[str]=None):
        out=[]
        for c in self.data["coupons"].values():
            if (shop_id is None) or (c["shop_id"]==shop_id):
                out.append(c)
        return out

    def apply(self, code: str, amount: float, audience: str, shop_id: str) -> Dict[str, Any]:
        code = (code or "").upper().strip()
        if not code:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"empty"}
        c = self.data["coupons"].get(code)
        if not c:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"not_found"}
        if c["expires_at"] and time.time() > c["expires_at"]:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"expired"}
        if c["uses"]>0 and c["used"]>=c["uses"]:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"depleted"}
        if c["shop_id"] and c["shop_id"]!=shop_id:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"wrong_shop"}
        if c["audience"]!="any" and c["audience"]!=audience:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"wrong_audience"}
        if amount < c["min_amount"]:
            return {"ok": False, "amount": amount, "discount": 0.0, "reason":"below_min"}

        discount = round(amount * (c["percent"]/100.0), 2)
        new_total = round(amount - discount, 2)
        # NOTE: l'incremento 'used' lo demandiamo al momento del pagamento OK
        return {"ok": True, "amount": new_total, "discount": discount, "coupon": c}

    def mark_used(self, code: str):
        code = (code or "").upper().strip()
        if not code: return
        c = self.data["coupons"].get(code)
        if not c: return
        c["used"] += 1
        self.save()
