import copy
import pytest
from app import app as flask_app, inventory


@pytest.fixture
def client():
    original = copy.deepcopy(inventory)
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c
    inventory[:] = original

def test_get_all_items(client):
    res = client.get("/inventory")
    assert res.status_code == 200
    assert len(res.get_json()) == 3

def test_get_one_item(client):
    res = client.get("/inventory/2")
    assert res.status_code == 200
    assert res.get_json()["product"]["product_name"] == "Nutella"

def test_get_missing_item_returns_404(client):
    res = client.get("/inventory/999")
    assert res.status_code == 404

def test_add_item_manually(client):
    res = client.post("/inventory", json={"product_name": "Orange Juice", "price": 2.5, "stock": 10})
    assert res.status_code == 201
    assert res.get_json()["id"] == 4
    assert len(client.get("/inventory").get_json()) == 4

def test_add_item_without_json_returns_400(client):
    res = client.post("/inventory")
    assert res.status_code == 400

def test_add_item_with_bad_price_returns_400(client):
    res = client.post("/inventory", json={"product_name": "X", "price": "abc", "stock": 1})
    assert res.status_code == 400

def test_add_item_with_negative_stock_returns_400(client):
    res = client.post("/inventory", json={"product_name": "X", "price": 1, "stock": -5})
    assert res.status_code == 400

def test_add_item_needs_barcode_or_name(client):
    res = client.post("/inventory", json={"price": 1, "stock": 1})
    assert res.status_code == 400

def test_add_item_by_barcode(client, monkeypatch):
    fake = {"barcode": "123", "product_name": "Fake Cola", "brands": "Test", "ingredients_text": "water"}
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: fake)
    res = client.post("/inventory", json={"barcode": "123", "price": 1, "stock": 5})
    assert res.status_code == 201
    assert res.get_json()["product"]["product_name"] == "Fake Cola"

def test_add_item_barcode_not_found_returns_404(client, monkeypatch):
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: None)
    res = client.post("/inventory", json={"barcode": "123"})
    assert res.status_code == 404

def test_add_item_api_down_returns_502(client, monkeypatch):
    def fake(barcode):
        raise ConnectionError("API down")
    monkeypatch.setattr("app.fetch_by_barcode", fake)
    res = client.post("/inventory", json={"barcode": "123"})
    assert res.status_code == 502
    assert res.get_json()["error"] == "API down"

def test_update_price_keeps_stock(client):
    res = client.patch("/inventory/1", json={"price": 9.99})
    assert res.status_code == 200
    assert res.get_json()["price"] == 9.99
    assert res.get_json()["stock"] == 24

def test_update_missing_item_returns_404(client):
    res = client.patch("/inventory/999", json={"price": 1})
    assert res.status_code == 404

def test_update_with_nothing_to_update_returns_400(client):
    res = client.patch("/inventory/1", json={"color": "red"})
    assert res.status_code == 400

def test_bad_update_changes_nothing(client):
    res = client.patch("/inventory/1", json={"price": 10, "stock": "abc"})
    assert res.status_code == 400
    assert client.get("/inventory/1").get_json()["price"] == 3.99

def test_delete_item(client):
    assert client.delete("/inventory/1").status_code == 200
    assert client.get("/inventory/1").status_code == 404

def test_delete_missing_item_returns_404(client):
    assert client.delete("/inventory/999").status_code == 404

def test_lookup_barcode_with_letters_returns_400(client):
    res = client.get("/lookup/barcode/abc")
    assert res.status_code == 400

def test_lookup_barcode_not_found_returns_404(client, monkeypatch):
    monkeypatch.setattr("app.fetch_by_barcode", lambda barcode: None)
    assert client.get("/lookup/barcode/123").status_code == 404

def test_lookup_search_empty_name_returns_400(client):
    assert client.get("/lookup/search?name=").status_code == 400

def test_lookup_search_returns_results(client, monkeypatch):
    monkeypatch.setattr("app.search_by_name", lambda name: [{"product_name": "Nutella"}])
    res = client.get("/lookup/search?name=nutella")
    assert res.status_code == 200
    assert len(res.get_json()) == 1

def test_lookup_search_api_down_returns_502(client, monkeypatch):
    def fake(name):
        raise ConnectionError("API down")
    monkeypatch.setattr("app.search_by_name", fake)
    assert client.get("/lookup/search?name=milk").status_code == 502