# Game Glitch Investigator

Game Glitch Investigator is a Streamlit-based debugging project centered on a simple game flow. I used it to fix structural issues in the codebase, separate logic from the UI more cleanly, and add security controls around rate limiting, session-state handling, and auditability.

## What I changed

- separated core game logic from UI concerns
- added cooldown-based and rolling-window rate limiting
- added a session-scoped audit log for security-relevant events
- hardened persisted high-score handling against malformed local data
- verified gameplay logic with automated tests and validated added controls manually

## Security focus

The main hardening work in this project focused on:

- reducing session abuse through rate limiting
- keeping security controls alive across Streamlit reruns
- improving accountability for submits, resets, wins, and losses
- handling malformed persisted score data safely

## Repo contents

- `app.py` - Streamlit interface and security control flow
- `tests/test_game_logic.py` - gameplay tests
- `Security.md` - detailed security hardening writeup
- case study document - summary of the hardening work

## Running the project

```bash
python -m pytest
python -m streamlit run app.py
```

## Notes

This project started as a debugging exercise, but I used it to apply more disciplined state handling, availability controls, and audit logging than the starter version included.
