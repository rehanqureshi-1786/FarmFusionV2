import re
import urllib.parse
from typing import List, Optional

AMAZON_IN_SEARCH = "https://www.amazon.in/s?k={query}"
IMG = "https://images.example.com/{path}"


class StoreRecommendationService:
    @staticmethod
    def _norm(text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9 ]+", "", text).strip().lower()

    @staticmethod
    def _amz(query: str) -> str:
        return AMAZON_IN_SEARCH.format(query=urllib.parse.quote_plus(query))

    @staticmethod
    def search(query: str) -> List[dict]:
        normalized = StoreRecommendationService._norm(query)
        return [
            {"name": query, "url": StoreRecommendationService._amz(query), "price": 0.0}
        ]
