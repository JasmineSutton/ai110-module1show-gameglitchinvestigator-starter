def test_event_log_append():
    # Simulate event log usage as in app.py
    event_log = []
    event = {"event": "submit", "at": 1234567890, "attempts": 1}
    event_log.append(event)
    assert event_log[-1]["event"] == "submit"
    assert event_log[-1]["attempts"] == 1

def test_event_log_multiple_events():
    event_log = []
    event_log.append({"event": "submit", "at": 1, "attempts": 1})
    event_log.append({"event": "rate_limited_cooldown", "at": 2, "attempts": 2})
    assert len(event_log) == 2
    assert event_log[0]["event"] == "submit"
    assert event_log[1]["event"] == "rate_limited_cooldown"
import tempfile
import json
def test_load_high_score_missing_file(monkeypatch):
    # Simulate missing file by patching Path.exists to return False
    from app import load_high_score
    class DummyPath:
        def exists(self): return False
    monkeypatch.setattr("app.HIGH_SCORE_FILE", DummyPath())
    assert load_high_score() == 0

def test_load_high_score_invalid_json(monkeypatch, tmp_path):
    # Simulate invalid JSON in high score file
    from app import load_high_score, HIGH_SCORE_FILE
    bad_file = tmp_path / "bad_high_score.json"
    bad_file.write_text("notjson", encoding="utf-8")
    monkeypatch.setattr("app.HIGH_SCORE_FILE", bad_file)
    assert load_high_score() == 0

def test_save_and_load_high_score(tmp_path, monkeypatch):
    # Test saving and loading high score
    from app import save_high_score, load_high_score, HIGH_SCORE_FILE
    test_file = tmp_path / "test_high_score.json"
    monkeypatch.setattr("app.HIGH_SCORE_FILE", test_file)
    save_high_score(42)
    assert json.loads(test_file.read_text(encoding="utf-8"))["best_score"] == 42
    assert load_high_score() == 42
#Fix: Added tests for game logic functions in logic_utils.py, including check_guess and validate_guess_bounds, to ensure correct behavior and improve test coverage. Refactored validate_guess_bounds from app.py into logic_utils.py for better separation of concerns and testability. Used Copilot Agent mode to assist with test creation and refactoring.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logic_utils import check_guess, validate_guess_bounds, get_range_for_difficulty, parse_guess, update_score
def test_get_range_for_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)
    assert get_range_for_difficulty("Unknown") == (1, 100)

def test_parse_guess_valid_int():
    ok, val, err = parse_guess("42")
    assert ok is True
    assert val == 42
    assert err is None

def test_parse_guess_valid_float():
    ok, val, err = parse_guess("42.0")
    assert ok is True
    assert val == 42
    assert err is None

def test_parse_guess_empty():
    ok, val, err = parse_guess("")
    assert not ok
    assert val is None
    assert err == "Enter a guess."

def test_parse_guess_none():
    ok, val, err = parse_guess(None)
    assert not ok
    assert val is None
    assert err == "Enter a guess."

def test_parse_guess_invalid():
    ok, val, err = parse_guess("notanumber")
    assert not ok
    assert val is None
    assert err == "That is not a number."

def test_update_score_win():
    assert update_score(0, "Win", 0) == 90
    assert update_score(0, "Win", 9) == 10

def test_update_score_too_high_even():
    assert update_score(10, "Too High", 2) == 15

def test_update_score_too_high_odd():
    assert update_score(10, "Too High", 3) == 5

def test_update_score_too_low():
    assert update_score(10, "Too Low", 1) == 5

def test_update_score_other():
    assert update_score(10, "Other", 1) == 10
import ast
from pathlib import Path

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result[0] == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result[0] == "Too Low"


def test_guess_bounds_valid_in_range():
    ok, err = validate_guess_bounds(42, 1, 100)
    assert ok is True
    assert err is None


def test_guess_bounds_rejects_negative():
    ok, err = validate_guess_bounds(-3, 1, 100)
    assert ok is False
    assert err == "Guess must be between 1 and 100."


def test_guess_bounds_rejects_above_range():
    ok, err = validate_guess_bounds(101, 1, 100)
    assert ok is False
    assert err == "Guess must be between 1 and 100."


def test_attempts_initializer_starts_at_zero():
    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    attempts_initializer = None

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue

        test = node.test
        if not isinstance(test, ast.Compare):
            continue

        if len(test.ops) != 1 or not isinstance(test.ops[0], ast.NotIn):
            continue

        if not isinstance(test.left, ast.Constant) or test.left.value != "attempts":
            continue

        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue

            for target in stmt.targets:
                if isinstance(target, ast.Attribute) and target.attr == "attempts":
                    if isinstance(stmt.value, ast.Constant):
                        attempts_initializer = stmt.value.value

    assert attempts_initializer == 0, (
        f"Expected attempts to start at 0, found {attempts_initializer}."
    )
