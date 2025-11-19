# TheLight24 v6 – Ethical BuyBox Engine
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Offer:
    shop_id: str
    shop_star: str
    sku: str
    title: str
    price: float
    currency: str
    stock: int
    fulfillment_score: float  # 0..1 (spedizioni, SLA, resi)
    reputation: float         # 0..1 (governance reputation)
    ethics: float             # 0..1 (ethics guard score)
    product_id: str

def score_offer(o: Offer) -> float:
    """
    Punteggio BuyBox etico:
      - prezzo (più basso vince): 40%
      - fulfillment: 20%
      - reputation: 20%
      - ethics: 20%
    Normalizziamo prezzo invertito rispetto al minimo del gruppo.
    """
    # Questi valori verranno normalizzati nel resolver
    return 0.0

def resolve_buybox(offers: List[Offer]) -> Dict[str, Any]:
    if not offers:
        return {"winner": None, "ranking": []}

    # Normalizzazione prezzo: 1.0 per il meno caro, decresce linearmente
    min_price = min(o.price for o in offers)
    max_price = max(o.price for o in offers)
    price_span = max(0.01, max_price - min_price)

    def price_score(p):
        # p == min -> 1.0 ; p == max -> ~0.0
        return max(0.0, 1.0 - (p - min_price)/price_span)

    ranking = []
    for o in offers:
        s_price = price_score(o.price)
        s_full  = max(0.0, min(1.0, o.fulfillment_score))
        s_rep   = max(0.0, min(1.0, o.reputation))
        s_eth   = max(0.0, min(1.0, o.ethics))

        score = (0.40*s_price) + (0.20*s_full) + (0.20*s_rep) + (0.20*s_eth)
        ranking.append((score, o))

    ranking.sort(key=lambda x: x[0], reverse=True)
    best = ranking[0][1]
    return {
        "winner": {
            "shop_id": best.shop_id,
            "shop_star": best.shop_star,
            "sku": best.sku,
            "product_id": best.product_id,
            "price": best.price,
            "currency": best.currency,
            "score": round(ranking[0][0], 4)
        },
        "ranking": [{
            "shop_id": r[1].shop_id, "shop_star": r[1].shop_star,
            "price": r[1].price, "currency": r[1].currency,
            "score": round(r[0],4), "stock": r[1].stock
        } for r in ranking]
    }
