import pytest
import requests


@pytest.mark.smoke
def test_get_statistic_success(created_item: tuple, base_url: str) -> None:
    """TC-004: Получение статистики по существующему объявлению."""
    item_data, _, _ = created_item
    item_id = item_data["id"]
    response: requests.Response = requests.get(
        f"{base_url}/api/1/statistic/{item_id}", headers={"Accept": "application/json"}, timeout=10
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    assert isinstance(result, list)
    if len(result) > 0:
        stat = result[0]
        assert isinstance(stat, dict)
        for field in ["likes", "viewCount", "contacts"]:
            assert field in stat, f"Missing field: {field}"
            val = stat[field]
            assert val is None or isinstance(
                val, (int, float)
            ), f"Field {field} type error: {type(val)}"


@pytest.mark.negative
def test_get_statistic_nonexistent(base_url: str) -> None:
    """TC-104: Статистика по несуществующему ID → 400."""
    fake_id: str = "fake-stat-id-999"
    response: requests.Response = requests.get(
        f"{base_url}/api/1/statistic/{fake_id}", headers={"Accept": "application/json"}, timeout=10
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"


@pytest.mark.regression
def test_statistic_fields_types(created_item: tuple, base_url: str) -> None:
    item_data, _, _ = created_item
    item_id = item_data["id"]
    response: requests.Response = requests.get(
        f"{base_url}/api/1/statistic/{item_id}", headers={"Accept": "application/json"}, timeout=10
    )
    assert response.status_code == 200
    stats_list = response.json()
    if len(stats_list) > 0:
        stats = stats_list[0]
        for field in ["likes", "viewCount", "contacts"]:
            value = stats.get(field)
            assert value is None or isinstance(
                value, (int, float)
            ), f"Invalid type for {field}: {type(value)}"