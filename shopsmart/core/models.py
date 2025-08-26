from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

class Product(BaseModel):
    title: str
    url: HttpUrl
    price: Optional[float] = Field(default=None, description="Price in EGP if available")
    currency: Optional[str] = "EGP"
    rating: Optional[float] = None
    review_count: Optional[int] = None
    availability: Optional[str] = None
    images: List[HttpUrl] = []
    source: Optional[str] = None  # 'amazon.eg' | 'jumia.com.eg' | 'noon.com/egypt-en'
    extra: Dict[str, str] = {}

class SearchPlan(BaseModel):
    query: str
    brand: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    features: List[str] = []
