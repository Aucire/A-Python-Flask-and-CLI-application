import pytest
from unittest.mock import patch
import cli


@pytest.mark.parametrize("choice, func_name", [
    ("1", "view_all"),
    ("2", "view_one"),
    ("3", "add_item"),
    ("4", "update_item"),
    ("5", "delete_item"),
    ("6", "find_on_api"),
])
def test_menu_choice_calls_the_right_function(choice, func_name):
    with patch("builtins.input", side_effect=[choice, "7"]), patch(f"cli.{func_name}") as mock_func:
        cli.main()
    mock_func.assert_called_once()

def test_seven_quits_the_loop():
    with patch("builtins.input", side_effect=["7"]) as mock_input:
        cli.main()
    assert mock_input.call_count == 1

def test_invalid_choice_shows_message_and_continues(capsys):
    with patch("builtins.input", side_effect=["abc", "7"]):
        cli.main()
    assert "Invalid choice" in capsys.readouterr().out

def test_zero_is_invalid_because_menu_quits_with_seven(capsys):
    with patch("builtins.input", side_effect=["0", "7"]):
        cli.main()
    assert "Invalid choice" in capsys.readouterr().out

def test_choice_with_extra_spaces_still_works():
    with patch("builtins.input", side_effect=[" 1 ", "7"]), patch("cli.view_all") as mock_func:
        cli.main()
    mock_func.assert_called_once()