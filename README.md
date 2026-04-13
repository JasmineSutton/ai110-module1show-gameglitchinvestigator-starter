# Glitch Game: [Your Subtitle Here]

## Original Project: Game Glitch Investigator (Modules 1–3)
This project began as a simple number guessing game built with Streamlit. The original goal was to create a playable game where users guess a secret number, with hints and score tracking. The focus was on basic game logic, user interaction, and persistent high score storage.

## Why It Matters
This project demonstrates how a basic interactive app can be enhanced with AI-powered features and robust reliability checks. It shows how to combine traditional logic, modern AI, and best practices in testing and auditability—skills that are valuable for any developer working on user-facing or AI-integrated applications.


# Game Glitch Investigator: Smarter Suggestions

Game Glitch Investigator is a Streamlit-based debugging project centered on a simple game flow. I used it to fix structural issues in the codebase, separate logic from the UI more cleanly, and add security controls around rate limiting, session-state handling, and auditability.

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
    


## Design Decisions

- separated core game logic from UI concerns
- added cooldown-based and rolling-window rate limiting
- added a session-scoped audit log for security-relevant events
- hardened persisted high-score handling against malformed local data
- integrated an AI-powered hint system using OpenAI for context-aware hints
- added an AI Guess Pattern Feedback feature that analyzes guess history and suggests strategies or points out mistakes
- all AI outputs are logged for reliability and can be reviewed for consistency or accuracy
- verified gameplay logic and AI integration with automated tests and manual validation
- integrated an AI-powered hint system using OpenAI for context-aware hints
- added an AI FaultFinder feature that analyzes guess history and suggests strategies or points out mistakes
- all AI outputs are logged for reliability and can be reviewed for consistency or accuracy




## Security Focus

The main hardening work in this project focused on:

- reducing session abuse through rate limiting
- keeping security controls alive across Streamlit reruns
- improving accountability for submits, resets, wins, and losses
- handling malformed persisted score data safely


## Repo Contents

- `app.py` - Streamlit interface and security control flow
- `tests/test_game_logic.py` - gameplay tests
- `Security.md` - detailed security hardening writeup
- case study document - summary of the hardening work




## Architecture Overview & Reliability Flow

The system is built around a Streamlit UI, session-based state management, core game logic, persistent storage, and testing/evaluation support. User input moves through the interface into the game logic and session state, while scores, feedback, and event logs are saved for tracking and review. After each guess, the app calls the AI for a hint and for guess pattern feedback, and logs all AI outputs to the event log. This enables both automated and human review of the AI’s performance, supporting reliability and continuous improvement.

See `sys_design.mmd` for the full diagram. The AI model is now a core part of the main application logic and reliability system.




## Sample Interactions (with AI)

**Guessing a Number**
- User enters: `50`
- App responds: `📉 Go LOWER!`
- AI Hint: `Try a number closer to the lower end of the range.`
- AI Guess Pattern Feedback: `You are narrowing your guesses, but try splitting the range in half each time for faster results.`

**Out-of-Bounds Guess**
- User enters: `-5`
- App responds: `Guess must be between 1 and 100.`

**Submitting Feedback**
- User enters feedback in the sidebar and clicks "Submit Feedback".
- App responds: `Thank you for your feedback!`

**AI Guess Pattern Feedback Example**
- User guess history: [50, 75, 62, 56]
- App shows: `AI Guess Pattern Feedback: You are narrowing your guesses, but try splitting the range in half each time for faster results.`


## Testing Summary

All tests pass successfully. The reliability system logs every AI output (hints and guess pattern feedback) for later review, ensuring the AI’s performance can be evaluated for consistency and usefulness.

To run tests:
```bash
python -m pytest
```


## Reflection

- The addition of AI-powered hints and guess pattern feedback made the game more interactive and educational.
- Integrating OpenAI required careful handling of API keys and error cases.
- Logging all AI outputs for reliability/testing provided a way to evaluate the AI’s usefulness and consistency.
- The project taught me how to combine traditional game logic with modern AI services, and how to design for reliability and auditability in AI-powered apps.

