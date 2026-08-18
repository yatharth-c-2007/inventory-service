import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_get_stock_existing_item(client):
    resp = client.get("/inventory/sku-001")
    assert resp.status_code == 200
    assert resp.get_json()["item_id"] == "sku-001"


def test_get_stock_missing_item(client):
    resp = client.get("/inventory/does-not-exist")
    assert resp.status_code == 404


def test_reserve_success(client):
    resp = client.post("/inventory/sku-004/reserve", json={"quantity": 5})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["reserved"] == 5


def test_reserve_insufficient_stock(client):
    resp = client.post("/inventory/sku-003/reserve", json={"quantity": 1})
    assert resp.status_code == 409


def test_reserve_bad_quantity(client):
    resp = client.post("/inventory/sku-001/reserve", json={"quantity": -1})
    assert resp.status_code == 400
