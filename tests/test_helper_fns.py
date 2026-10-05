from unittest.mock import patch, MagicMock
import requests
import helper_fns

def test_call_returns_json_on_success():
    fake = MagicMock(ok=True)
    fake.json.return_value = [{"id": 1}]
    with patch("helper_fns.requests.request", return_value=fake):
        assert helper_fns.call("GET", "/inventory") == [{"id": 1}]

def test_call_prints_server_error_and_returns_none(capsys):
    fake = MagicMock(ok=False, status_code=404)
    fake.json.return_value = {"error": "Item not found"}
    with patch("helper_fns.requests.request", return_value=fake):
        assert helper_fns.call("GET", "/inventory/99") is None
    out = capsys.readouterr().out
    assert "404" in out
    assert "Item not found" in out

def test_call_server_not_running(capsys):
    with patch("helper_fns.requests.request", side_effect=requests.exceptions.ConnectionError):
        assert helper_fns.call("GET", "/inventory") is None
    assert "Cannot reach the server" in capsys.readouterr().out

def test_call_invalid_json_response(capsys):
    fake = MagicMock(ok=True)
    fake.json.side_effect = ValueError
    with patch("helper_fns.requests.request", return_value=fake):
        assert helper_fns.call("GET", "/inventory") is None
    assert "invalid response" in capsys.readouterr().out

ITEM = {"id": 2, "price": 2.49, "stock": 40,
        "product": {"product_name": "Nutella", "brands": "Ferrero", "ingredients_text": "Sugar, palm oil"}}

def test_show_prints_item_details(capsys):
    helper_fns.show(ITEM)
    out = capsys.readouterr().out
    assert "Nutella" in out
    assert "$2.49" in out
    assert "stock: 40" in out
    assert "Sugar, palm oil" in out

def test_show_with_no_brand(capsys):
    item = {"id": 1, "price": 1.0, "stock": 1, "product": {"product_name": "Water", "brands": ""}}
    helper_fns.show(item)
    assert "no brand" in capsys.readouterr().out

def test_view_one_rejects_non_number_id(capsys):
    with patch("builtins.input", return_value="abc"), patch("helper_fns.call") as mock_call:
        helper_fns.view_one()
    mock_call.assert_not_called()
    assert "whole number" in capsys.readouterr().out

def test_view_one_calls_the_right_route():
    with patch("builtins.input", return_value="2"), patch("helper_fns.call", return_value=ITEM) as mock_call:
        helper_fns.view_one()
    mock_call.assert_called_once_with("GET", "/inventory/2")

def test_delete_rejects_non_number_id():
    with patch("builtins.input", return_value="x"), patch("helper_fns.call") as mock_call:
        helper_fns.delete_item()
    mock_call.assert_not_called()

def test_delete_prints_server_message(capsys):
    with patch("builtins.input", return_value="3"), \
        patch("helper_fns.call", return_value={"message": "Item 3 deleted"}) as mock_call:
        helper_fns.delete_item()
    mock_call.assert_called_once_with("DELETE", "/inventory/3")
    assert "Item 3 deleted" in capsys.readouterr().out

def test_add_item_invalid_mode(capsys):
    with patch("builtins.input", side_effect=["9", "2.5", "10"]), patch("helper_fns.call") as mock_call:
        helper_fns.add_item()
    mock_call.assert_not_called()
    assert "Invalid choice" in capsys.readouterr().out

def test_add_item_manually_sends_correct_body():
    inputs = ["2", "2.5", "10", "Juice", "Del Monte"]
    with patch("builtins.input", side_effect=inputs), patch("helper_fns.call", return_value=None) as mock_call:
        helper_fns.add_item()
    mock_call.assert_called_once_with(
        "POST", "/inventory",
        json={"price": "2.5", "stock": "10", "product_name": "Juice", "brands": "Del Monte"})

def test_add_item_by_barcode_sends_correct_body():
    inputs = ["1", "4.5", "20", "3017620422003"]
    with patch("builtins.input", side_effect=inputs), patch("helper_fns.call", return_value=None) as mock_call:
        helper_fns.add_item()
    mock_call.assert_called_once_with(
        "POST", "/inventory",
        json={"price": "4.5", "stock": "20", "barcode": "3017620422003"})

def test_update_rejects_non_number_id():
    with patch("builtins.input", return_value="abc"), patch("helper_fns.call") as mock_call:
        helper_fns.update_item()
    mock_call.assert_not_called()

def test_update_with_nothing_entered(capsys):
    with patch("builtins.input", side_effect=["1", "", ""]), patch("helper_fns.call") as mock_call:
        helper_fns.update_item()
    mock_call.assert_not_called()
    assert "Nothing to update" in capsys.readouterr().out

def test_update_price_only_sends_only_price():
    with patch("builtins.input", side_effect=["1", "5.5", ""]), patch("helper_fns.call", return_value=None) as mock_call:
        helper_fns.update_item()
    mock_call.assert_called_once_with("PATCH", "/inventory/1", json={"price": "5.5"})

def test_find_on_api_invalid_mode(capsys):
    with patch("builtins.input", return_value="9"), patch("helper_fns.call") as mock_call:
        helper_fns.find_on_api()
    mock_call.assert_not_called()
    assert "Invalid choice" in capsys.readouterr().out

def test_find_on_api_by_name_no_results(capsys):
    with patch("builtins.input", side_effect=["2", "zzzz"]), patch("helper_fns.call", return_value=[]) as mock_call:
        helper_fns.find_on_api()
    mock_call.assert_called_once_with("GET", "/lookup/search", params={"name": "zzzz"})
    assert "No results" in capsys.readouterr().out

def test_find_on_api_by_barcode_found(capsys):
    product = {"product_name": "Nutella", "brands": "Ferrero", "barcode": "123"}
    with patch("builtins.input", side_effect=["1", "123"]), patch("helper_fns.call", return_value=product):
        helper_fns.find_on_api()
    assert "Nutella" in capsys.readouterr().out

def test_find_on_api_by_barcode_not_found(capsys):
    with patch("builtins.input", side_effect=["1", "123"]), patch("helper_fns.call", return_value=None):
        helper_fns.find_on_api()
    assert "No results" in capsys.readouterr().out