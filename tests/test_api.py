from unittest.mock import patch, MagicMock
import pytest
import requests
import api

def test_slim_keeps_only_needed_fields():
    raw = {"code": "123", "product_name": "Nutella", "brands": "Ferrero", "extra": "ignored"}
    result = api._slim(raw)
    assert result["barcode"] == "123"
    assert result["product_name"] == "Nutella"
    assert "extra" not in result

def test_slim_uses_defaults_for_missing_fields():
    result = api._slim({})
    assert result["product_name"] == "Unknown"
    assert result["barcode"] == ""
    assert result["ingredients_text"] == ""

def test_barcode_with_letters_raises_valueerror():
    with pytest.raises(ValueError):
        api.fetch_by_barcode("abc123")

def test_fetch_by_barcode_found():
    fake = {"status": 1, "product": {"product_name": "Nutella", "brands": "Ferrero"}}
    with patch("api._get", return_value=fake):
        result = api.fetch_by_barcode("3017620422003")
    assert result["product_name"] == "Nutella"
    assert result["barcode"] == "3017620422003"

def test_fetch_by_barcode_not_found_returns_none():
    with patch("api._get", return_value={"status": 0}):
        assert api.fetch_by_barcode("123") is None

@pytest.mark.parametrize("name", ["", "   "])
def test_empty_search_raises_valueerror(name):
    with pytest.raises(ValueError):
        api.search_by_name(name)

def test_search_by_name_returns_list():
    fake = {"products": [{"product_name": "A"}, {"product_name": "B"}]}
    with patch("api._get", return_value=fake):
        results = api.search_by_name("milk")
    assert [r["product_name"] for r in results] == ["A", "B"]

def test_search_with_no_products_key_returns_empty_list():
    with patch("api._get", return_value={}):
        assert api.search_by_name("zzzz") == []

def test_get_returns_json_on_success():
    fake_response = MagicMock()
    fake_response.json.return_value = {"ok": True}
    with patch("api.requests.get", return_value=fake_response):
        assert api._get("http://example.com") == {"ok": True}
    fake_response.raise_for_status.assert_called_once()

def test_get_timeout_becomes_connectionerror():
    with patch("api.requests.get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(ConnectionError):
            api._get("http://example.com")

def test_get_bad_status_becomes_connectionerror():
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
    with patch("api.requests.get", return_value=fake_response):
        with pytest.raises(ConnectionError):
            api._get("http://example.com")