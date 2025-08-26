from __future__ import annotations
from typing import List
from .models import Product

def score_product(p: Product, prefer_brand: str | None, max_price: float | None, min_rating: float | None) -> float:
    score = 0.0
    if p.price is not None:
        if max_price is not None and p.price <= max_price:
            score += 3.0
        else:
            score += 1.0  # price known but above budget
    if p.rating is not None:
        score += min(p.rating / 5.0 * 3.0, 3.0)
        if min_rating is not None and p.rating >= min_rating:
            score += 1.0
    if prefer_brand and prefer_brand.lower() in (p.title or '').lower():
        score += 2.0
    return score

def rank_products(products: List[Product], prefer_brand: str | None, max_price: float | None, min_rating: float | None) -> List[Product]:
    return sorted(products, key=lambda p: score_product(p, prefer_brand, max_price, min_rating), reverse=True)
