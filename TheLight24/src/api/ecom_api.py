# TheLight24 v6 – ECOM FastAPI Router (STEP 8)
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import List, Optional, Dict
import os, json

from ecommerce.models import DB, CartItem, save_media_upload
from ecommerce.payments import Payments
from ecommerce.buybox import resolve_buybox, Offer
from ecommerce.discounts import Coupons
from ecommerce.ledger_hooks import seal_order, verify_chain

router = APIRouter(prefix="/ecom", tags=["ecommerce"])
_db = DB(); _db.load()
_pay = Payments()
_coupons = Coupons(); _coupons.load()

# -------- Merchant (admin/merchant) --------
@router.post("/merchant/shop/create")
def merchant_create_shop(owner: str = Form(...), star_name: str = Form(...), country: str = Form("IT")):
    shop = _db.create_shop(owner=owner, star_name=star_name, country=country)
    return {"ok":True, "shop": shop.__dict__}

@router.post("/merchant/shop/enable")
def merchant_enable_shop(shop_id: str = Form(...), enabled: bool = Form(True)):
    _db.set_shop_enabled(shop_id, enabled)
    return {"ok":True}

@router.post("/merchant/shop/flags")
def merchant_flags(shop_id: str = Form(...),
                   b2c: Optional[bool] = Form(None),
                   b2b: Optional[bool] = Form(None),
                   cod: Optional[bool] = Form(None)):
    _db.set_shop_flags(shop_id, b2c, b2b, cod)
    return {"ok":True}

@router.post("/merchant/shop/scores")
def merchant_scores(shop_id: str = Form(...),
                    fulfillment: Optional[float] = Form(None),
                    reputation: Optional[float] = Form(None),
                    ethics: Optional[float] = Form(None)):
    _db.set_shop_scores(shop_id, fulfillment, reputation, ethics)
    return {"ok":True}

@router.post("/merchant/product/add")
def merchant_add_product(shop_id: str = Form(...),
                         sku: str = Form(...),
                         title: str = Form(...),
                         description: str = Form(""),
                         stock_qty: int = Form(0),
                         b2c_json: str = Form('{"EUR":0.0}'),
                         b2b_json: str = Form('{"EUR":0.0}'),
                         tags_csv: str = Form(""),
                         image: UploadFile = File(None)):
    images=[]
    if image is not None:
        tmp = os.path.join("data","runtime","upload_tmp_"+image.filename)
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(image.file.read())
        rel = save_media_upload(tmp)
        images.append(rel)

    b2c = json.loads(b2c_json)
    b2b = json.loads(b2b_json)
    tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
    p = _db.add_product(shop_id, sku, title, description, images, stock_qty, b2c, b2b, tags)
    return {"ok":True, "product": p.__dict__}

@router.post("/merchant/stock")
def merchant_stock(shop_id: str = Form(...), product_id: str = Form(...), qty: int = Form(...)):
    _db.update_stock(shop_id, product_id, qty)
    return {"ok":True}

@router.get("/merchant/orders")
def merchant_orders(shop_id: str):
    return {"orders":[o.__dict__ for o in _db.list_orders(shop_id=shop_id)]}

# Coupons
@router.post("/merchant/coupon/create")
def merchant_coupon_create(code: str = Form(...), percent: float = Form(...),
                           min_amount: float = Form(0.0), shop_id: Optional[str] = Form(None),
                           audience: str = Form("any"), uses: int = Form(0), expires_at: Optional[float]=Form(None)):
    c = _coupons.create(code, percent, min_amount, shop_id, audience, uses, expires_at)
    return {"ok":True, "coupon": c}

@router.get("/merchant/coupons")
def merchant_coupons(shop_id: Optional[str]=None):
    return {"coupons": _coupons.list(shop_id)}

# -------- Public browsing --------
@router.get("/galaxy")
def galaxy_stars():
    stars = []
    for shop in _db.list_shops(only_enabled=True):
        pos = _db.data["galaxy"]["stars"].get(shop.shop_id, {"x":0,"y":0,"z":0})
        stars.append({"shop_id":shop.shop_id, "star":shop.star_name, "country":shop.country, "pos":pos})
    return {"stars":stars}

@router.get("/shop")
def shop_info(shop_id: str):
    shops = {s.shop_id:s for s in _db.list_shops(only_enabled=True)}
    s = shops.get(shop_id)
    if not s: raise HTTPException(404, "Shop not found or disabled")
    return {"shop": s.__dict__}

@router.get("/products")
def shop_products(shop_id: str, audience: str = Query("b2c", regex="^(b2c|b2b)$")):
    s = None
    for x in _db.list_shops(only_enabled=True):
        if x.shop_id==shop_id: s=x; break
    if not s: raise HTTPException(404, "Shop not found or disabled")
    if audience=="b2c" and not s.b2c_enabled: return {"products":[]}
    if audience=="b2b" and not s.b2b_enabled: return {"products":[]}
    items=[]
    for p in _db.list_products(shop_id):
        price_table = p.price_list.b2c if audience=="b2c" else p.price_list.b2b
        items.append({
            "product_id": p.product_id,
            "sku": p.sku,
            "title": p.title,
            "description": p.description,
            "images": p.images,
            "stock_qty": p.stock_qty,
            "price": price_table
        })
    return {"products":items}

# BuyBox multi-shop per SKU
@router.get("/buybox")
def buybox_sku(sku: str, audience: str = Query("b2c", regex="^(b2c|b2b)$"), currency: str="EUR"):
    offers=[]
    for s in _db.list_shops(only_enabled=True):
        if audience=="b2c" and not s.b2c_enabled: continue
        if audience=="b2b" and not s.b2b_enabled: continue
        for p in _db.list_products(s.shop_id):
            if p.sku != sku or not p.active or p.stock_qty<=0: continue
            table = p.price_list.b2c if audience=="b2c" else p.price_list.b2b
            price = float(table.get(currency, 0.0))
            if price<=0: continue
            offers.append(Offer(
                shop_id=s.shop_id, shop_star=s.star_name, sku=sku,
                title=p.title, price=price, currency=currency, stock=p.stock_qty,
                fulfillment_score=s.fulfillment_score, reputation=s.reputation, ethics=s.ethics,
                product_id=p.product_id
            ))
    result = resolve_buybox(offers)
    return result

# -------- Checkout --------
@router.post("/checkout")
def checkout(shop_id: str = Form(...),
             user_id: str = Form(...),
             audience: str = Form("b2c"),
             currency: str = Form("EUR"),
             payment: str = Form("crypto"),
             items_json: str = Form(...),
             coupon_code: Optional[str] = Form(None)):
    items_req = json.loads(items_json)  # [{product_id, qty}]
    prods = {p.product_id:p for p in _db.list_products(shop_id)}
    cart=[]
    for it in items_req:
        p = prods.get(it["product_id"])
        if not p or not p.active: raise HTTPException(400, "Invalid product")
        table = p.price_list.b2c if audience=="b2c" else p.price_list.b2b
        price = float(table.get(currency, 0.0))
        if price<=0: raise HTTPException(400, "Price not available in selected currency")
        if it["qty"]>p.stock_qty: raise HTTPException(400, "Insufficient stock")
        cart.append(CartItem(product_id=p.product_id, qty=int(it["qty"]), price_currency=currency, price_amount=price))

    order = _db.create_order(shop_id, user_id, cart, payment, currency, coupon_code=coupon_code)

    # Coupon apply (pre-payment)
    amount = order.total_amount
    discount_applied = None
    if coupon_code:
        r = _coupons.apply(coupon_code, amount, audience, shop_id)
        if r["ok"]:
            discount_applied = r
            amount = r["amount"]

    # Simulated payment
    if payment=="crypto":
        res = _pay.pay_crypto(amount, currency)
    elif payment=="paypal":
        res = _pay.pay_paypal(amount, currency)
    elif payment=="card":
        res = _pay.pay_card(amount, currency, "VISA")
    elif payment=="cod":
        s=None
        for x in _db.list_shops(only_enabled=True):
            if x.shop_id==shop_id: s=x; break
        if not s or not s.cod_enabled:
            raise HTTPException(400, "COD not enabled by merchant")
        res = _pay.pay_cod(amount, currency)
    else:
        raise HTTPException(400, "Unknown payment method")

    if res.ok:
        _db.set_order_status(order.order_id, "paid" if payment!="cod" else "pending")
        # decrement stock
        for it in cart:
            p = prods[it.product_id]
            _db.update_stock(shop_id, it.product_id, p.stock_qty - it.qty)
        # mark coupon as used
        if discount_applied and discount_applied.get("coupon"):
            _coupons.mark_used(coupon_code)
        # seal on ledger
        sealed = seal_order({
            "order_id": order.order_id,
            "shop_id": shop_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "payment": payment,
            "coupon": coupon_code or "",
            "items": [{"product_id":c.product_id,"qty":c.qty,"price":c.price_amount} for c in cart]
        })
        _db.attach_order_seal(order.order_id, sealed["hash"])

    return {
        "ok": res.ok, "order_id": order.order_id,
        "status": "paid" if payment!="cod" else "pending",
        "provider": res.provider, "reference": res.reference,
        "amount": amount,
        "coupon": coupon_code or None,
        "seal_hash": _db.data["orders"][order.order_id].get("seal_hash")
    }

# -------- Ledger verify --------
@router.get("/ledger/verify")
def ecom_ledger_verify():
    return verify_chain()
