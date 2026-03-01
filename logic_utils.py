def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        #FIX: Refactored logic into logic_utils.py using Copilot Agent mode to fix hints being reversed
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        #FIXED: Restore valid return for low-guess path after accidental inline note corruption.
        return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"

#FIX: Validate guess bounds in a separate function to keep check_guess focused on game logic and improve testability. Refactored validate_guess_bounds from app.py into logic_utils.py using Copilot Agent mode.
def validate_guess_bounds(guess: int, low: int, high: int):
    """Validate guess is within inclusive [low, high] bounds."""
    if guess < low or guess > high:
        return False, f"Guess must be between {low} and {high}."
    return True, None


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
