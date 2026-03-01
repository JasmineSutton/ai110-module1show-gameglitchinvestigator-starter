#Fix: Added tests for game logic functions in logic_utils.py, including check_guess and validate_guess_bounds, to ensure correct behavior and improve test coverage. Refactored validate_guess_bounds from app.py into logic_utils.py for better separation of concerns and testability. Used Copilot Agent mode to assist with test creation and refactoring.
from logic_utils import check_guess, validate_guess_bounds
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
