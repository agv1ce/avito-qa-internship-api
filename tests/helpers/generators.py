import random
import string
from datetime import datetime, timezone
from typing import Dict, Any, Optional

def generate_seller_id() -> int:
    """Генерирует уникальный sellerId в диапазоне 111111–999999."""
    return random.randint(111111, 999999)

def generate_unique_name(prefix: str = "TestItem") -> str:
    """Генерирует уникальное имя с временной меткой."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[:-3]
    random_suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_valid_item_payload(
    seller_id: Optional[int] = None, override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "sellerID": seller_id or generate_seller_id(),
        "name": generate_unique_name(),
        "price": random.randint(100, 1000000),
        "statistics": {
            "viewCount": 100,
            "likes": 10, 
            "contacts": 5, 
        },
    }
    if override:
        for key, value in override.items():
            if key == "statistics" and value is not None:
                if isinstance(value, dict):
                    for stat_key in ["viewCount", "likes", "contacts"]:
                        if stat_key in value and value[stat_key] is not None:
                            payload["statistics"][stat_key] = value[stat_key]
            elif value is not None:
                payload[key] = value

    return payload