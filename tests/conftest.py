from typing import Any, Dict, Iterator, Tuple
import pytest
import requests
from tests.helpers.generators import generate_valid_item_payload

BASE_URL: str = "https://qa-internship.avito.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="function")
def created_item(base_url: str) -> Iterator[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]]:
    payload: Dict[str, Any] = generate_valid_item_payload()
    response: requests.Response = requests.post(
        f"{base_url}/api/1/item",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10,
    )
    assert (
        response.status_code == 200
    ), f"Failed to create item: {response.status_code} {response.text}"
    response_data: Dict[str, Any] = response.json()
    item_id: str | None = None
    if isinstance(response_data, dict) and "status" in response_data:
        status_msg: str = response_data["status"]
        if " - " in status_msg:
            item_id = status_msg.split(" - ")[-1].strip()
    if not item_id and isinstance(response_data, list):
        for item in response_data:
            if isinstance(item, dict):
                if "id" in item:
                    item_id = item["id"]
                    break
                if "status" in item and " - " in item["status"]:
                    item_id = item["status"].split(" - ")[-1].strip()
                    break
    item_name: str | None = payload.get("name")
    item_price: int | None = payload.get("price")
    item_seller_id: int = payload["sellerID"]
    item_statistics: Dict[str, Any] = payload.get("statistics", {})
    if isinstance(response_data, dict):
        item_name = response_data.get("name") or item_name
        item_price = response_data.get("price") or item_price
        if "statistics" in response_data:
            item_statistics = response_data["statistics"]
    item_data: Dict[str, Any] = {
        "id": item_id,
        "name": item_name,
        "price": item_price,
        "sellerID": item_seller_id,
        "statistics": item_statistics,
    }
    yield item_data, payload, response_data
    if item_id:
        try:
            requests.delete(
                f"{base_url}/api/2/item/{item_id}",
                headers={"Accept": "application/json"},
                timeout=5,
            )
        except Exception:
            pass
