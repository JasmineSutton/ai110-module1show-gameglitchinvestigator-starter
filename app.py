import json
import random
import time
from pathlib import Path

import streamlit as st
from logic_utils import check_guess, validate_guess_bounds


#REFACTORED: Added high score feature that survives app restarts.
HIGH_SCORE_FILE = Path(__file__).with_name("high_score.json")

#Secure Modification: Adding Rate limiting
#FIX: Implement basic rate limiting to prevent abuse. 
Submit_cooldown_seconds = .20
Max_Submits_per_Window = 4
Rate_window_seconds = 60



def load_high_score() -> int:
    try:
        if not HIGH_SCORE_FILE.exists():
            return 0
        payload = json.loads(HIGH_SCORE_FILE.read_text(encoding="utf-8"))
        value = int(payload.get("best_score", 0))
        return max(0, value)
    except Exception:
        return 0


def save_high_score(score: int) -> None:
    payload = {"best_score": max(0, int(score))}
    HIGH_SCORE_FILE.write_text(json.dumps(payload), encoding="utf-8")


def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)


attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")


if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "high_score" not in st.session_state:
    st.session_state.high_score = load_high_score()

#Secure Modification: Persist submit timing state for cooldown and rolling window limits.
#FIX: Track timestamps in session state so rate limiting is per active user session.
if "last_submit_ts" not in st.session_state:
    st.session_state.last_submit_ts = 0.0

if "submit_timestamps" not in st.session_state:
    st.session_state.submit_timestamps = []

#Secure Modification: Add lightweight audit trail for security-relevant user actions.
#FIX: Use event_log entries for submit attempts, rate-limit blocks, and end-game outcomes.
if "event_log" not in st.session_state:
    st.session_state.event_log = []

#REFACTORED: Added persistent high score display in sidebar.
st.sidebar.metric("High Score", st.session_state.high_score)

st.subheader("Make a guess")

#FIXED: Use the active difficulty bounds in the prompt text.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)
    st.write("Event Log:", st.session_state.event_log)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    st.session_state.last_submit_ts = 0.0
    st.session_state.submit_timestamps = []
    st.session_state.event_log.append(
        {
            "event": "new_game",
            "at": time.time(),
            "difficulty": difficulty,
        }
    )
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

# FIXME: First guess is not being processed. Score is not updating on first guess.
#FIX: Refactored logic into logic_utils.py using Copilot Agent mode
if submit:
    now = time.monotonic()

    #Secure Modification: Enforce minimum delay between submit actions.
    #FIX: Block rapid-fire clicking that can spam reruns and game state updates.
    if (now - st.session_state.last_submit_ts) < Submit_cooldown_seconds:
        st.session_state.event_log.append(
            {
                "event": "rate_limited_cooldown",
                "at": time.time(),
                "attempts": st.session_state.attempts,
            }
        )
        st.error("You're clicking too fast. Please wait a moment.")
        st.stop()

    #Secure Modification: Enforce rolling submit window per session.
    #FIX: Keep only timestamps inside the active window and reject if cap is reached.
    cutoff = now - Rate_window_seconds
    st.session_state.submit_timestamps = [
        ts for ts in st.session_state.submit_timestamps if ts >= cutoff
    ]

    if len(st.session_state.submit_timestamps) >= Max_Submits_per_Window:
        st.session_state.event_log.append(
            {
                "event": "rate_limited_window",
                "at": time.time(),
                "attempts": st.session_state.attempts,
                "window_seconds": Rate_window_seconds,
            }
        )
        st.error("Rate limit reached. Please wait before submitting again.")
        st.stop()

    st.session_state.submit_timestamps.append(now)
    st.session_state.last_submit_ts = now
    st.session_state.event_log.append(
        {
            "event": "submit",
            "at": time.time(),
            "attempts": st.session_state.attempts,
        }
    )

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        #FIXED: Reject out-of-range numeric guesses without consuming an attempt.
        in_bounds, bounds_err = validate_guess_bounds(guess_int, low, high)
        if not in_bounds:
            st.error(bounds_err)
        else:
            #FIXED: Count attempts only for valid in-range numeric guesses.
            st.session_state.attempts += 1
            st.session_state.history.append(guess_int)

            if st.session_state.attempts % 2 == 0:
                secret = str(st.session_state.secret)
            else:
                secret = st.session_state.secret

            outcome, message = check_guess(guess_int, secret)

            if show_hint:
                st.warning(message)

            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )

            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                st.session_state.event_log.append(
                    {
                        "event": "win",
                        "at": time.time(),
                        "score": st.session_state.score,
                        "attempts": st.session_state.attempts,
                    }
                )

                #REFACTORED: Save new best score to disk whenever a higher score is achieved.
                if st.session_state.score > st.session_state.high_score:
                    st.session_state.high_score = st.session_state.score
                    save_high_score(st.session_state.high_score)

                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
            else:
                if st.session_state.attempts >= attempt_limit:
                    st.session_state.status = "lost"
                    st.session_state.event_log.append(
                        {
                            "event": "loss",
                            "at": time.time(),
                            "score": st.session_state.score,
                            "attempts": st.session_state.attempts,
                        }
                    )
                    st.error(
                        f"Out of attempts! "
                        f"The secret was {st.session_state.secret}. "
                        f"Score: {st.session_state.score}"
                    )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
