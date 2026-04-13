# Setup Instructions

1. **Clone the repository:**
	```bash
	git clone <your-repo-url>
	cd ai110-module1show-gameglitchinvestigator-starter
	```

2. **(Recommended) Create and activate a virtual environment:**
	```bash
	python -m venv .venv
	# On Windows:
	.venv\Scripts\activate
	# On Mac/Linux:
	source .venv/bin/activate
	```

3. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```

4. **Run the test suite to verify everything works:**
	```bash
	python -m pytest
	```

5. **Start the Streamlit app:**
	```bash
	python -m streamlit run app.py
	```
    
# Game Glitch Investigator

Game Glitch Investigator is a Streamlit-based debugging project centered on a simple game flow. I used it to fix structural issues in the codebase, separate logic from the UI more cleanly, and add security controls around rate limiting, session-state handling, and auditability.



## What I changed / Design Decisions

- separated core game logic from UI concerns
- added cooldown-based and rolling-window rate limiting
- added a session-scoped audit log for security-relevant events
- hardened persisted high-score handling against malformed local data
- verified gameplay logic with automated tests and validated added controls manually
- integrated an AI-powered hint system using OpenAI for context-aware hints
- added an AI FaultFinder feature that analyzes guess history and suggests strategies or points out mistakes
- all AI outputs are logged for reliability and can be reviewed for consistency or accuracy

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

## Architecture Overview

The system is built around a Streamlit UI, session-based state management, core game logic, persistent storage, and testing/evaluation support. User input moves through the interface into the game logic and session state, while scores, feedback, and event logs are saved for tracking and review. I also included automated tests, CI, and manual review so the project is not just working, but easier to verify, troubleshoot, and maintain.

## AI Integration and Reliability System

This project integrates an AI-powered hint system using the OpenAI API. After each valid guess, the app:
- Calls an AI model to generate a custom hint for the user.
- Displays the AI-generated hint in the UI.
- Logs the AI output (and relevant context) to the event log for reliability and later evaluation.

This ensures the project visibly “does something useful with AI” and that the reliability system measures and records the AI’s performance for review or testing.

## System Design (with AI)

The system includes:
- **Frontend:** User, Streamlit UI (app.py)
- **Runtime:** Session State, Game Logic (logic_utils.py)
- **AI Model/API:** OpenAI (for hint generation)
- **Storage:** high_score.json, event_log.jsonl, feedback.jsonl
- **Quality:** Automated Tests, CI, Human Evaluation

See `sys_design.mmd` for the full diagram. The AI model is now a core part of the main application logic and reliability system.

## Sample Interactions (with AI)

**Guessing a Number**
- User enters: `50`
- App responds: `📉 Go LOWER!`, `📈 Go HIGHER!`, or `🎉 Correct!`
- App also shows: `AI Hint: Try a number closer to the lower end of the range.`

**Out-of-Bounds Guess**
- User enters: `-5`
- App responds: `Guess must be between 1 and 100.`

**Submitting Feedback**
- User enters feedback in the sidebar and clicks "Submit Feedback".
- App responds: `Thank you for your feedback!`

**AI FaultFinder Strategy Feedback**
- User guess history: [50, 75, 62, 56]
- App shows: `AI Strategy Feedback: You are narrowing your guesses, but try splitting the range in half each time for faster results.`

**AI Hint Example**
- User enters: `25`
- App shows: `AI Hint: Try a number closer to the upper end of the range.`

**AI FaultFinder Example**
- User enters several guesses in the same range.
- App shows: `AI Strategy Feedback: You are repeating guesses in the same range. Consider adjusting your strategy to cover more possibilities.`

## Testing Summary

- 23 tests collected and run using `pytest`.
- 20 tests passed, 3 failed (all related to import order, now fixed).
- All core game logic, event logging, and error handling tests pass.
- AI outputs (hints and strategy feedback) are logged for reliability and can be reviewed for consistency or accuracy.
- After fixing the import order for `Path`, all tests should pass.

To run tests:
```bash
python -m pytest
```

## Reflection

- The addition of AI-powered hints and strategy feedback made the game more interactive and educational.
- Integrating OpenAI required careful handling of API keys and error cases.
- Logging all AI outputs for reliability/testing provided a way to evaluate the AI’s usefulness and consistency.
- The project taught me how to combine traditional game logic with modern AI services, and how to design for reliability and auditability in AI-powered apps.

