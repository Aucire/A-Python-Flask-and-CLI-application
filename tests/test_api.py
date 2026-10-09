import pytest
import requests
import api

class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_slim_keeps_the_fields_we_need():
    product = {"code": "123", "product_name": "Nutella", "brands": "Ferrero", "extra": "ignored"}
    assert api._slim(product) == {
        "barcode": "123",
        "product_name": "Nutella",
        "brands": "Ferrero",
    }

def test_slim_uses_defaults_for_missing_fields():
    result = api._slim({})
    assert result["barcode"] == ""
    assert result["product_name"] == "Unknown"
    assert result["brands"] == ""

def test_get_returns_json_on_success(monkeypatch):
    monkeypatch.setattr("api.requests.get", lambda *a, **kw: FakeResponse({"ok": True}))
    assert api._get("http://fake-url") == {"ok": True}

def test_get_raises_connection_error_when_request_fails(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr("api.requests.get", boom)
    with pytest.raises(ConnectionError):
        api._get("http://fake-url")


def test_fetch_by_barcode_rejects_non_digits():
    with pytest.raises(ValueError):
        api.fetch_by_barcode("abc123")

def test_fetch_by_barcode_found(monkeypatch):
    fake_data = {"status": 1, "product": {"product_name": "Nutella", "brands": "Ferrero"}}
    monkeypatch.setattr("api._get", lambda url, params=None: fake_data)
    result = api.fetch_by_barcode("3017620422003")
    assert result["product_name"] == "Nutella"
    assert result["barcode"] == "3017620422003"  # filled in from the barcode we asked for

def test_fetch_by_barcode_not_found_returns_none(monkeypatch):
    monkeypatch.setattr("api._get", lambda url, params=None: {"status": 0})
    assert api.fetch_by_barcode("0000000000000") is None


@pytest.mark.parametrize("bad_name", ["", "   ", None])
def test_search_rejects_empty_name(bad_name):
    with pytest.raises(ValueError):
        api.search_by_name(bad_name)

def test_search_returns_slimmed_products(monkeypatch):
    fake_data = {
        "products": [
            {"code": "1", "product_name": "Milk", "brands": "A"},
            {"code": "2", "product_name": "Oat Milk", "brands": "B"},
        ]
    }
    monkeypatch.setattr("api._get", lambda url, params=None: fake_data)
    results = api.search_by_name("milk")
    assert len(results) == 2
    assert results[0]["product_name"] == "Milk"

def test_search_with_no_products_returns_empty_list(monkeypatch):
    monkeypatch.setattr("api._get", lambda url, params=None: {})
    assert api.search_by_name("zzzz") == []



def test_search_sends_name_and_limit(monkeypatch):
    captured = {}
    def fake_get(url, params=None):
        captured["params"] = params
        return {"products": []}

    monkeypatch.setattr("api._get", fake_get)
    api.search_by_name("milk", limit=5)
    assert captured["params"]["search_terms"] == "milk"
    assert captured["params"]["page_size"] == 5