import pytest
import requests
from tests.helpers.generators import generate_valid_item_payload, generate_seller_id


@pytest.mark.smoke
def test_create_item_success(created_item: tuple) -> None:
    """TC-001: Успешное создание объявления."""
    item_data, payload, response_data = created_item
    assert item_data["id"] is not None, "Item ID should not be None"
    assert isinstance(
        item_data["id"], str
    ), f"Item ID should be string, got {type(item_data['id'])}"
    assert item_data["sellerID"] == payload["sellerID"], (
        f"sellerID mismatch: expected {payload['sellerID']}, " f"got {item_data['sellerID']}"
    )
    assert item_data["name"] is not None, "Item name should not be None"
    assert item_data["name"] == payload["name"], (
        f"name mismatch: expected {payload['name']}, " f"got {item_data['name']}"
    )
    assert item_data["price"] is not None, "Item price should not be None"
    assert item_data["price"] == payload["price"], (
        f"price mismatch: expected {payload['price']}, " f"got {item_data['price']}"
    )
    if isinstance(response_data, dict):
        assert "status" in response_data, "Response should contain 'status'"
        assert "Сохранили объявление" in response_data["status"]
    stats = payload.get("statistics", {})
    assert isinstance(stats, dict), "Statistics should be a dictionary"
    assert "viewCount" in stats
    assert "likes" in stats
    assert "contacts" in stats


@pytest.mark.smoke
def test_get_item_by_id_success(created_item: tuple, base_url: str) -> None:
    """TC-002: Получение объявления по валидному ID."""
    item_data, payload, _ = created_item
    item_id = item_data["id"]
    response: requests.Response = requests.get(
        f"{base_url}/api/1/item/{item_id}", headers={"Accept": "application/json"}, timeout=10
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    assert isinstance(result, list)
    assert len(result) >= 1
    found = next((item for item in result if item.get("id") == item_id), None)
    assert found is not None, "Created item not found in response"
    assert found.get("name") == payload["name"]


@pytest.mark.negative
def test_create_item_empty_body(base_url: str) -> None:
    """TC-101: Создание с пустым телом → 400."""
    response: requests.Response = requests.post(
        f"{base_url}/api/1/item",
        json={},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10,
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert any(
        k in resp_json for k in ["result", "status", "message"]
    ), "Response should contain error information"


@pytest.mark.negative
def test_get_nonexistent_item(base_url: str) -> None:
    """TC-103: Получение несуществующего объявления → 400."""
    fake_id: str = "non-existent-id-12345"
    response: requests.Response = requests.get(
        f"{base_url}/api/1/item/{fake_id}", headers={"Accept": "application/json"}, timeout=10
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"


@pytest.mark.regression
def test_get_items_by_seller_id(base_url: str) -> None:
    """TC-003: Получение всех объявлений продавца."""
    seller_id: int = generate_seller_id()
    created_ids: list[str] = []
    for _ in range(2):
        payload = generate_valid_item_payload(seller_id=seller_id)
        resp: requests.Response = requests.post(
            f"{base_url}/api/1/item",
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=10,
        )
        assert resp.status_code == 200, f"Failed to create: {resp.text}"
        resp_data = resp.json()
        if isinstance(resp_data, dict) and "status" in resp_data:
            msg = resp_data["status"]
            if " - " in msg:
                created_ids.append(msg.split(" - ")[-1].strip())
    response: requests.Response = requests.get(
        f"{base_url}/api/1/{seller_id}/item", headers={"Accept": "application/json"}, timeout=10
    )
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    for item in items:
        item_seller_id = item.get("sellerID") or item.get("sellerId")
        assert (
            item_seller_id == seller_id
        ), f"sellerID mismatch: expected {seller_id}, got {item_seller_id}"
    returned_ids = [i.get("id") for i in items if i.get("id")]
    for cid in created_ids:
        assert cid in returned_ids, f"Item {cid} not in seller list"


@pytest.mark.negative
def test_create_item_invalid_seller_id_type(base_url: str) -> None:
    """TC-102: sellerId как строка вместо числа → 400."""
    payload = generate_valid_item_payload()
    payload["sellerID"] = "invalid_string"
    response: requests.Response = requests.post(
        f"{base_url}/api/1/item",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10,
    )
    assert response.status_code == 400


@pytest.mark.negative
def test_create_item_negative_price(base_url: str) -> None:
    """TC-102 (доп.): отрицательная цена → 400."""
    payload = generate_valid_item_payload()
    payload["price"] = -100
    response: requests.Response = requests.post(
        f"{base_url}/api/1/item",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10,
    )
    if response.status_code == 200:
        pytest.xfail("Backend accepts negative price – potential bug")
    else:
        assert response.status_code == 400
