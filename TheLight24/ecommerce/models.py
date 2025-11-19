# TheLight24 v6 – ECOM data models (encrypted JSON store)
import os, time, uuid, json, shutil
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from .security import file_write_encrypted, file_read_encrypted

STORE_DIR = "data/commerce"
MEDIA_DIR = os.path.join(STORE_DIR, "media")
DB_PATH   = os.path.join(STORE_DIR, "db.enc")   # encrypted JSON db

@dataclass
class PriceList:
    b2c: Dict[str, float] = field(default_factory=dict)
    b2b: Dict[str, float] = field(default_factory=dict)

@dataclass
class Product:
    product_id: str
    sku: str
    title: str
    description: str
    images: List[str] = field(default_factory=list)
    stock_qty: int = 0
    price_list: PriceList = field(default_factory=PriceList)
    tags: List[str] = field(default_factory=list)
    active: bool = True

@dataclass
class Shop:
    shop_id: str
    owner: str
    star_name: str
    enabled: bool = False
    country: str = "IT"
    b2c_enabled: bool = True
    b2b_enabled: bool = True
    cod_enabled: bool = False
    # NEW: ranking fields used by BuyBox
    fulfillment_score: float = 0.7  # 0..1
    reputation: float = 0.7         # 0..1
    ethics: float = 0.9             # 0..1
    products: Dict[str, Product] = field(default_factory=dict)

@dataclass
class CartItem:
    product_id: str
    qty: int
    price_currency: str
    price_amount: float

@dataclass
class Order:
    order_id: str
    shop_id: str
    user_id: str
    items: List[CartItem]
    total_currency: str
    total_amount: float
    payment_method: str
    status: str = "pending"
    created_at: float = field(default_factory=lambda: time.time())
    # NEW: coupon + sealing
    coupon_code: Optional[str] = None
    seal_hash: Optional[str] = None

class DB:
    def __init__(self):
        self.data = {
            "shops": {},
            "orders": {},
            "galaxy": {"stars": {}}
        }
        os.makedirs(STORE_DIR, exist_ok=True)
        os.makedirs(MEDIA_DIR, exist_ok=True)

    def load(self):
        self.data = file_read_encrypted(DB_PATH, self.data)

    def save(self):
        file_write_encrypted(DB_PATH, self.data)

    def create_shop(self, owner: str, star_name: str, country: str="IT") -> Shop:
        shop_id = str(uuid.uuid4())
        shop = Shop(shop_id=shop_id, owner=owner, star_name=star_name, country=country)
        self.data["shops"][shop_id] = asdict(shop)
        self.data["galaxy"]["stars"][shop_id] = {
            "x": float((hash(shop_id) % 200 - 100) / 10.0),
            "y": float((hash(owner)  % 200 - 100) / 10.0),
            "z": float((hash(star_name) % 200 - 100) / 10.0)
        }
        self.save()
        return shop

    def set_shop_enabled(self, shop_id: str, enabled: bool):
        shop = self.data["shops"].get(shop_id)
        if not shop: raise KeyError("Shop not found")
        shop["enabled"] = bool(enabled)
        self.save()

    def set_shop_flags(self, shop_id: str, b2c: Optional[bool]=None, b2b: Optional[bool]=None, cod: Optional[bool]=None):
        shop = self.data["shops"].get(shop_id)
        if not shop: raise KeyError("Shop not found")
        if b2c is not None: shop["b2c_enabled"] = bool(b2c)
        if b2b is not None: shop["b2b_enabled"] = bool(b2b)
        if cod is not None: shop["cod_enabled"] = bool(cod)
        self.save()

    def set_shop_scores(self, shop_id: str, fulfillment: Optional[float]=None, reputation: Optional[float]=None, ethics: Optional[float]=None):
        shop = self.data["shops"].get(shop_id)
        if not shop: raise KeyError("Shop not found")
        if fulfillment is not None: shop["fulfillment_score"] = float(max(0.0,min(1.0,fulfillment)))
        if reputation is not None:  shop["reputation"] = float(max(0.0,min(1.0,reputation)))
        if ethics is not None:      shop["ethics"] = float(max(0.0,min(1.0,ethics)))
        self.save()

    def list_shops(self, only_enabled=True) -> List[Shop]:
        out=[]
        for s in self.data["shops"].values():
            if (not only_enabled) or s.get("enabled"):
                out.append(Shop(**s))
        return out

    def add_product(self, shop_id: str, sku: str, title: str, description: str, images: List[str], stock_qty: int,
                    b2c_prices: Dict[str,float], b2b_prices: Dict[str,float], tags: List[str]):
        shop = self.data["shops"].get(shop_id)
        if not shop: raise KeyError("Shop not found")
        product_id = str(uuid.uuid4())
        p = Product(
            product_id=product_id, sku=sku, title=title, description=description,
            images=images, stock_qty=stock_qty,
            price_list=PriceList(b2c=b2c_prices, b2b=b2b_prices), tags=tags, active=True
        )
        shop["products"][product_id] = asdict(p)
        self.save()
        return p

    def update_stock(self, shop_id: str, product_id: str, new_qty: int):
        shop = self.data["shops"].get(shop_id)
        if not shop: raise KeyError("Shop not found")
        p = shop["products"].get(product_id)
        if not p: raise KeyError("Product not found")
        p["stock_qty"] = int(new_qty)
        self.save()

    def list_products(self, shop_id: str, active_only=True) -> List[Product]:
        shop = self.data["shops"].get(shop_id)
        if not shop: raise KeyError("Shop not found")
        out=[]
        for p in shop["products"].values():
            if (not active_only) or p.get("active", True):
                out.append(Product(**p))
        return out

    def create_order(self, shop_id: str, user_id: str, items: List[CartItem], payment_method: str, currency: str,
                     coupon_code=None) -> Order:
        total = 0.0
        for it in items:
            total += float(it.price_amount) * int(it.qty)
        order_id = str(uuid.uuid4())
        order = Order(order_id=order_id, shop_id=shop_id, user_id=user_id,
                      items=[asdict(x) for x in items],
                      total_currency=currency, total_amount=round(total,2),
                      payment_method=payment_method, coupon_code=coupon_code)
        self.data["orders"][order_id] = asdict(order)
        self.save()
        return order

    def set_order_status(self, order_id: str, status: str):
        o = self.data["orders"].get(order_id)
        if not o: raise KeyError("Order not found")
        o["status"] = status
        self.save()

    def attach_order_seal(self, order_id: str, seal_hash: str):
        o = self.data["orders"].get(order_id)
        if not o: raise KeyError("Order not found")
        o["seal_hash"] = seal_hash
        self.save()

def save_media_upload(src_path: str) -> str:
    os.makedirs(MEDIA_DIR, exist_ok=True)
    fname = f"{int(time.time()*1000)}_{os.path.basename(src_path)}"
    dst = os.path.join(MEDIA_DIR, fname)
    shutil.copy2(src_path, dst)
    return os.path.relpath(dst, STORE_DIR)
