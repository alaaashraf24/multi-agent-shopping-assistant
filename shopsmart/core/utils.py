from __future__ import annotations
import re, time, os, math, json
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

class FetchError(Exception):
    pass

def domain_of(url: str) -> str:
    return urlparse(url).netloc.lower()

@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def fetch(url: str, timeout: int = 20) -> str:
    if os.getenv("ALLOW_WEB_FETCH", "true").lower() not in ("1","true","yes","y"):
        raise FetchError("Web fetch disabled by ALLOW_WEB_FETCH")
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    if resp.status_code >= 400:
        raise FetchError(f"HTTP {resp.status_code} for {url}")
    return resp.text

_price_re = re.compile(r"(\d+[\,\.]?\d*)")

def parse_price_to_float(text: str) -> float | None:
    text = text.replace(",", "").strip()
    m = _price_re.search(text)
    if not m: 
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None
