import copy
import pytest
import app as app_module
from app import app as flask_app

ORIGINAL_INVENTORY = copy.deepcopy(app_module.inventory)
FAKE_PRODUCT = {
    "barcode": "123",
    "product_name": "Fake Juice",
    "brands": "TestBrand",
    "ingredients_text": "Water, apple",
}


@pytest.fixture
def client():
    """Fresh test client with the inventory reset before EVERY test."""
    flask_app.config["TESTING"] = True
    app_module.inventory[:] = copy.deepcopy(ORIGINAL_INVENTORY)  # reset in place
    with flask_app.test_client() as c:
        yield c


def test_get_inventory_returns_all_items(client):
    res = client.get("/inventory")
    assert res.status_code == 200
    assert len(res.get_json()) == 3

def test_get_single_item(client):
    res = client.get("/inventory/1")
    assert res.status_code == 200
    assert res.get_json()["product"]["product_name"] == "Organic Almond Milk"

def test_get_missing_item_returns_404(client):
    res = client.get("/inventory/999")
    assert res.status_code == 404

def test_add_item_manually(client):
    res = client.post(
        "/inventory",
        json={"product_name": "Test Bread", "price": 2.5, "stock": 10},
    )
    assert res.status_code == 201
    assert res.get_json()["id"] == 4
    assert res.get_json()["product"]["product_name"] == "Test Bread"
    assert len(client.get("/inventory").get_json()) == 4

def test_add_item_by_barcode(client, monkeypatch):
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: FAKE_PRODUCT)

    res = client.post("/inventory", json={"barcode": "123", "price": 1, "stock": 2})
    assert res.status_code == 201
    assert res.get_json()["product"]["product_name"] == "Fake Juice"

def test_add_item_empty_body_returns_400(client):
    res = client.post("/inventory", json={})
    assert res.status_code == 400

def test_add_item_without_barcode_or_name_returns_400(client):
    res = client.post("/inventory", json={"price": 1, "stock": 1})
    assert res.status_code == 400

def test_add_item_unknown_barcode_returns_404(client, monkeypatch):
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: None)

    res = client.post("/inventory", json={"barcode": "000", "price": 1, "stock": 1})
    assert res.status_code == 404

def test_update_item(client):
    res = client.patch("/inventory/1", json={"price": 9.99, "stock": 5})
    assert res.status_code == 200
    assert res.get_json()["price"] == 9.99
    assert res.get_json()["stock"] == 5

def test_update_missing_item_returns_404(client):
    res = client.patch("/inventory/999", json={"price": 1, "stock": 1})
    assert res.status_code == 404

def test_delete_item(client):
    res = client.delete("/inventory/1")
    assert res.status_code == 200
    assert client.get("/inventory/1").status_code == 404  # really gone

def test_delete_missing_item_returns_404(client):
    res = client.delete("/inventory/999")
    assert res.status_code == 404

def test_lookup_barcode(client, monkeypatch):
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: FAKE_PRODUCT)

    res = client.get("/lookup/barcode/123")
    assert res.status_code == 200
    assert res.get_json()["product_name"] == "Fake Juice"


def test_lookup_barcode_not_found(client, monkeypatch):
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: None)

    res = client.get("/lookup/barcode/000")
    assert res.status_code == 404

def test_lookup_search(client, monkeypatch):
    monkeypatch.setattr("app.search_by_name", lambda name: [FAKE_PRODUCT])

    res = client.get("/lookup/search?name=juice")
    assert res.status_code == 200
    assert res.get_json()[0]["product_name"] == "Fake Juice"