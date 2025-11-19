#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate

python3 - <<'PY'
import requests, json, os

API="http://127.0.0.1:8000"

def post(path, data=None, files=None):
    return requests.post(API+path, data=data, files=files, timeout=5.0).json()

def get(path):
    return requests.get(API+path, timeout=5.0).json()

# Shop 1
s1 = post("/ecom/merchant/shop/create", {"owner":"merchant_demo", "star_name":"Stella Ormanet", "country":"IT"})
sid1 = s1["shop"]["shop_id"]
post("/ecom/merchant/shop/enable", {"shop_id":sid1, "enabled":"true"})
post("/ecom/merchant/shop/flags", {"shop_id":sid1, "b2c":"true", "b2b":"true", "cod":"true"})
post("/ecom/merchant/shop/scores", {"shop_id":sid1, "fulfillment":0.85, "reputation":0.80, "ethics":0.95})

post("/ecom/merchant/product/add", {
    "shop_id":sid1, "sku":"A4-CARTA-500", "title":"Risam Carta A4 500fg", "description":"Carta A4 bianca 80g/m²",
    "stock_qty":"120", "b2c_json":json.dumps({"EUR":4.90}), "b2b_json":json.dumps({"EUR":4.10}), "tags_csv":"carta,ufficio"
})
post("/ecom/merchant/product/add", {
    "shop_id":sid1, "sku":"TN-241BK", "title":"Toner Nero TN-241", "description":"Compatibile alta resa",
    "stock_qty":"35", "b2c_json":json.dumps({"EUR":28.90}), "b2b_json":json.dumps({"EUR":24.50}), "tags_csv":"toner,stampa"
})

# Shop 2 (Competitor sulla stessa SKU per BuyBox)
s2 = post("/ecom/merchant/shop/create", {"owner":"merchant_comp", "star_name":"Stella Zenith", "country":"IT"})
sid2 = s2["shop"]["shop_id"]
post("/ecom/merchant/shop/enable", {"shop_id":sid2, "enabled":"true"})
post("/ecom/merchant/shop/flags", {"shop_id":sid2, "b2c":"true", "b2b":"true", "cod":"false"})
post("/ecom/merchant/shop/scores", {"shop_id":sid2, "fulfillment":0.90, "reputation":0.70, "ethics":0.92})

post("/ecom/merchant/product/add", {
    "shop_id":sid2, "sku":"A4-CARTA-500", "title":"Carta A4 500 Classic", "description":"80g/m² office",
    "stock_qty":"80", "b2c_json":json.dumps({"EUR":4.70}), "b2b_json":json.dumps({"EUR":4.00}), "tags_csv":"carta"
})

# Coupon demo per shop1
post("/ecom/merchant/coupon/create", {"code":"WELCOME10", "percent":"10", "min_amount":"5", "shop_id":sid1, "audience":"any", "uses":"100"})

print("Demo commerce initialized.")
PY
