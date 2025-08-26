from __future__ import annotations
import os
from typing import List
from tavily import TavilyClient

EGYPT_DOMAINS = [
    "www.amazon.eg", "amazon.eg",
    "www.jumia.com.eg", "jumia.com.eg",
    "www.noon.com", "noon.com"
]

def search_products(query: str, max_results: int = 12) -> List[str]:
    """Use Tavily to search product pages on Amazon.eg, Jumia, Noon (Egypt).
    Returns a list of URLs.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY missing")
    client = TavilyClient(api_key=api_key)
    results = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_domains=EGYPT_DOMAINS,
        exclude_domains=None,
        include_answer=False,
        include_raw_content=False,
    )
    urls = []
    for item in results.get("results", []):
        u = item.get("url")
        if u:
            # Prefer Egypt subpaths for Noon
            if "noon.com" in u and "/egypt-" not in u and "/egypt_en" not in u and "/egypt-en" not in u:
                continue
            urls.append(u)
    # de-duplicate preserving order
    seen = set()
    dedup = []
    for u in urls:
        if u not in seen:
            dedup.append(u)
            seen.add(u)
    return dedup[:max_results]
