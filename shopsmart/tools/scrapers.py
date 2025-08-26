from __future__ import annotations
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
import re, json
import extruct
from w3lib.html import get_base_url
from ..core.models import Product
from ..core.utils import fetch, parse_price_to_float, domain_of

AMAZON_DOMAINS = {"amazon.eg", "www.amazon.eg"}
JUMIA_DOMAINS = {"jumia.com.eg", "www.jumia.com.eg"}
NOON_DOMAINS = {"noon.com", "www.noon.com"}

def _extract_jsonld(html: str, url: str) -> Dict:
    base_url = get_base_url(html, url)
    data = extruct.extract(html, base_url=base_url, syntaxes=["json-ld"], errors="log")
    items = data.get("json-ld", []) if data else []
    for it in items:
        if isinstance(it, dict) and it.get("@type") in ("Product","ProductGroup"):
            return it
    return {}

def _first_image(images) -> List[str]:
    vals = []
    if isinstance(images, list):
        for im in images:
            if isinstance(im, str):
                vals.append(im)
            elif isinstance(im, dict) and "url" in im:
                vals.append(im["url"])
    elif isinstance(images, str):
        vals = [images]
    return vals

def _from_jsonld(ld: Dict, url: str, source: str) -> Optional[Product]:
    if not ld:
        return None
    title = ld.get("name") or ld.get("title") or ""
    offers = ld.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price = offers.get("price")
    currency = offers.get("priceCurrency") or "EGP"
    rating = None
    review_count = None
    agg = ld.get("aggregateRating") or {}
    if isinstance(agg, dict):
        rating = agg.get("ratingValue")
        review_count = agg.get("reviewCount")
        try:
            rating = float(rating) if rating is not None else None
            review_count = int(review_count) if review_count is not None else None
        except Exception:
            pass
    images = _first_image(ld.get("image"))
    p = Product(
        title=title or "Unknown",
        url=url,
        price=float(price) if price not in (None, "") else None,
        currency=currency,
        rating=rating,
        review_count=review_count,
        availability=(offers.get("availability") or "").split("/")[-1] if offers else None,
        images=images,
        source=source,
        extra={"jsonld": "true"}
    )
    return p

def _from_dom(html: str, url: str, source: str) -> Product:
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("meta[property='og:title']") or soup.select_one("title")
    title_text = title.get("content") if title and title.has_attr("content") else (title.get_text(strip=True) if title else "Unknown")
    # Heuristics for price across sites
    candidates = []
    for sel in [
        "[data-asin-price]", "#priceblock_ourprice", "#priceblock_dealprice", "[data-old-price]",
        ".price ._price", ".-fs24", ".price-number", ".product-price", "meta[itemprop='price']",
        "span[data-price]", "span.price", "div.price"
    ]:
        node = soup.select_one(sel)
        if node:
            candidates.append(node.get("content") if node.has_attr("content") else node.get_text(" ", strip=True))
    price = None
    for c in candidates:
        price = parse_price_to_float(c)
        if price:
            break
    # Rating
    rating = None
    for sel in ["i[data-hook='average-star-rating'] span", "span[data-hook='rating-out-of-text']", ".rating-stars", ".rating .-fs16", "span.rating__value"]:
        node = soup.select_one(sel)
        if node:
            m = re.search(r"(\d[\d\. ]*)", node.get_text(" ", strip=True))
            if m:
                try:
                    rating = float(m.group(1).replace(" ", ""))
                except Exception:
                    pass
            if rating:
                break
    # Images
    images = []
    for im in soup.select("img"):
        src = im.get("src") or im.get("data-src")
        if src and src.startswith("http"):
            images.append(src)
    images = images[:5]
    return Product(
        title=title_text,
        url=url,
        price=price,
        currency="EGP",
        rating=rating,
        review_count=None,
        availability=None,
        images=images,
        source=source,
        extra={"jsonld": "false"}
    )

def extract_product(url: str) -> Optional[Product]:
    html = fetch(url)
    source_dom = domain_of(url)
    jsonld = _extract_jsonld(html, url)
    if source_dom in AMAZON_DOMAINS:
        prod = _from_jsonld(jsonld, url, "amazon.eg") or _from_dom(html, url, "amazon.eg")
        return prod
    if source_dom in JUMIA_DOMAINS:
        prod = _from_jsonld(jsonld, url, "jumia.com.eg") or _from_dom(html, url, "jumia.com.eg")
        return prod
    if source_dom in NOON_DOMAINS:
        # ensure url is Egypt product page
        if "/egypt" not in url and "/egypt-" not in url:
            return None
        prod = _from_jsonld(jsonld, url, "noon.com/egypt-en") or _from_dom(html, url, "noon.com/egypt-en")
        return prod
    return None
