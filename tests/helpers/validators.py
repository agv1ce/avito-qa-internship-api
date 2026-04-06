import re
from typing import Any, Dict, List, Tuple

def is_iso8601(value: str) -> bool:
    """Проверяет, что строка в формате ISO 8601."""
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}" r"(\.\d+)?(Z|[+-]\d{2}:\d{2})?$"
    return bool(re.match(pattern, value))

def validate_item_schema(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Валидирует структуру ответа с объявлением."""
    errors: List[str] = []
    required_fields = ["id", "sellerId", "name", "price", "statistics", "createdAt"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    if "id" in data and not isinstance(data["id"], str):
        errors.append(f"Field 'id' must be string, got {type(data['id']).__name__}")
    if "createdAt" in data and not is_iso8601(data["createdAt"]):
        errors.append(f"Field 'createdAt' is not valid ISO8601: {data['createdAt']}")
    if "statistics" in data:
        stats = data["statistics"]
        for stat_field in ["likes", "viewCount", "contacts"]:
            if stat_field in stats and not isinstance(stats[stat_field], (int, type(None))):
                errors.append(f"Statistics.{stat_field} must be int or null")
    return len(errors) == 0, errors
