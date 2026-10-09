import pytest
import cli

def fake_inputs(monkeypatch, answers):
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))


def test_choice_7_quits(monkeypatch, capsys):
    fake_inputs(monkeypatch, ["7"])
    cli.main()
    assert "Program exited successfully" in capsys.readouterr().out


def test_input_is_stripped_of_spaces(monkeypatch, capsys):
    fake_inputs(monkeypatch, ["  7  "])
    cli.main()
    assert "Program exited successfully" in capsys.readouterr().out

@pytest.mark.parametrize(
    "choice, function_name",
    [
        ("1", "view_all"),
        ("2", "view_one"),
        ("3", "add_item"),
        ("4", "update_item"),
        ("5", "delete_item"),
        ("6", "find_on_api"),
    ],
)
def test_each_choice_calls_the_right_function(monkeypatch, choice, function_name):
    calls = []

    monkeypatch.setattr(f"cli.{function_name}", lambda: calls.append(function_name))

    fake_inputs(monkeypatch, [choice, "7"])  
    cli.main()

    assert calls == [function_name]  

def test_invalid_choice_shows_message_and_keeps_running(monkeypatch, capsys):
    fake_inputs(monkeypatch, ["9", "7"]) 
    cli.main()

    out = capsys.readouterr().out
    assert "Invalid choice" in out
    assert "Program exited successfully" in out  