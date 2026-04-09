# Game Glitch Investigator Security Hardening - Detailed Change Log

This document summarizes the security hardening that was added to this repository. The starter project did not include a STRIDE model, rate limiting, or security-focused audit logging. This write-up is based on the current code in `app.py`, the security-tagged `Secure Refactor` comments in the code, and the STRIDE notes that were added later as part of the hardening work. I excluded general gameplay fixes unless they materially changed the security posture.

## Frameworks Referenced

| Abbreviation | Full Name | Why it is relevant here |
| --- | --- | --- |
| STRIDE | Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege | STRIDE was introduced during the hardening work and is useful here because the implemented controls mainly address Denial of Service and Repudiation. |
| OWASP Top 10 | OWASP Top 10 (2021) | Useful for mapping design gaps such as missing rate limits and missing auditability. |
| NIST SP 800-53 | NIST Special Publication 800-53 Rev. 5 | Provides concrete control families for logging, input handling, and denial-of-service protection. |
| CWE | Common Weakness Enumeration | Useful for naming the underlying weakness each hardening step addresses. |

## File: app.py

### Change 1 - Defensive high-score file handling (Lines 11, 21-34)

What changed:

```python
HIGH_SCORE_FILE = Path(__file__).with_name("high_score.json")

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
```

What it does: The app reads and writes the persisted score through a fixed local path, converts stored values to integers, clamps negative values to `0`, and falls back safely if the file is missing or malformed.

Why it helps: This is a defensive robustness control around trusted local input. A broken or manually edited `high_score.json` file no longer crashes the app or injects invalid negative state into the score display. It does not prevent tampering, but it reduces the impact of malformed persisted data.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | T (Tampering), partial | The code normalizes local file input before use, but it does not make the file tamper-resistant. |
| CWE | CWE-20 - Improper Input Validation | Stored score data is validated and normalized before entering application state. |
| NIST SP 800-53 | SI-10 - Information Input Validation | The persisted score is validated before being accepted. |
| NIST SP 800-53 | SI-11 - Error Handling | Malformed file content is handled safely instead of crashing the app. |

### Change 2 - Rate-limiting constants added (Lines 13-17)

What changed:

```python
Submit_cooldown_seconds = .20
Max_Submits_per_Window = 4
Rate_window_seconds = 60
```

What it does: These constants define two submit controls: a minimum delay between clicks and a rolling-window cap for total submits.

Why it helps: Before this, a user could spam the submit button and force repeated reruns of the Streamlit script. That can waste resources, make game state harder to reason about, and create a basic denial-of-service path against the session.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | D (Denial of Service) | The control directly targets request spamming and state-abuse through excessive submits. |
| OWASP Top 10 | A04:2021 - Insecure Design | Explicit interaction limits are a design-level hardening control. |
| CWE | CWE-799 - Improper Control of Interaction Frequency | The app now constrains how frequently a user can trigger the sensitive action. |
| CWE | CWE-400 - Uncontrolled Resource Consumption | Rate limits reduce unnecessary reruns and resource use. |
| NIST SP 800-53 | SC-5 - Denial-of-Service Protection | The constants establish the thresholds used by the DoS protection logic. |

### Change 3 - Session-scoped security state initialized (Lines 124-138)

What changed:

```python
if "high_score" not in st.session_state:
    st.session_state.high_score = load_high_score()

if "last_submit_ts" not in st.session_state:
    st.session_state.last_submit_ts = 0.0

if "submit_timestamps" not in st.session_state:
    st.session_state.submit_timestamps = []

if "event_log" not in st.session_state:
    st.session_state.event_log = []
```

What it does: The app now keeps limiter timestamps and a security event log in `st.session_state`, which means the controls persist across Streamlit reruns for the active user session.

Why it helps: Streamlit reruns the script on interaction. Without session-scoped state, a limiter or audit trail would reset on the next click and become trivial to bypass. Persisting the timestamps and log is what makes the later controls actually work.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | D (Denial of Service) | The limiter state must survive reruns to be enforceable. |
| STRIDE | R (Repudiation) | The event log must persist within the session to provide any accountability. |
| OWASP Top 10 | A04:2021 - Insecure Design | This closes a design flaw where controls would otherwise disappear on rerun. |
| OWASP Top 10 | A09:2021 - Security Logging and Monitoring Failures | It creates the application state needed for audit records. |
| NIST SP 800-53 | AU-2 - Event Logging | Establishes the mechanism used to store security-relevant events. |
| NIST SP 800-53 | AU-12 - Audit Record Generation | Supports generation of audit entries during gameplay actions. |
| NIST SP 800-53 | SC-5 - Denial-of-Service Protection | Stores the data required to enforce the limiter. |

### Change 4 - New-game flow resets limiter state and records the reset (Lines 172-184)

What changed:

```python
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
```

What it does: Starting a new game now clears the active rate-limit window and writes a `new_game` audit event.

Why it helps: This keeps the limiter state consistent and prevents stale timestamps from leaking across games. The event record also makes the session timeline easier to interpret when reviewing how a win, loss, or rate-limit block happened.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | D (Denial of Service) | Resets limiter state cleanly at the same lifecycle boundary as the game reset. |
| STRIDE | R (Repudiation) | Adds a timestamped record showing when a new session of play began. |
| OWASP Top 10 | A04:2021 - Insecure Design | Avoids cross-game leakage of control state. |
| OWASP Top 10 | A09:2021 - Security Logging and Monitoring Failures | Adds a security-relevant lifecycle event to the audit trail. |
| NIST SP 800-53 | AU-12 - Audit Record Generation | Generates an event for the reset action. |
| NIST SP 800-53 | SC-5 - Denial-of-Service Protection | Keeps the limiter logic in a valid state after reset. |

### Change 5 - Cooldown-based submit throttling (Lines 196-210)

What changed:

```python
if submit:
    now = time.monotonic()

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
```

What it does: The app blocks submit attempts that occur too soon after the previous submit and records the block in the event log.

Why it helps: This prevents rapid-fire clicking from hammering the app, spamming reruns, and mutating state at a pace the interface was not designed to handle. It is the first line of defense against button-mash abuse.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | D (Denial of Service) | The control mitigates rapid request abuse within a single session. |
| OWASP Top 10 | A04:2021 - Insecure Design | Adds an explicit safety boundary around a sensitive state-changing action. |
| CWE | CWE-799 - Improper Control of Interaction Frequency | The app now rejects submits that arrive too quickly. |
| CWE | CWE-400 - Uncontrolled Resource Consumption | Fewer abusive reruns means lower resource pressure. |
| NIST SP 800-53 | SC-5 - Denial-of-Service Protection | This is the direct enforcement step for the DoS mitigation. |

### Change 6 - Rolling-window rate limiting (Lines 212-228)

What changed:

```python
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
```

What it does: The app keeps only recent timestamps inside the active window and blocks the request if the session has already reached the maximum number of submits allowed in that period.

Why it helps: The cooldown alone stops bursts, but it does not stop sustained abuse. The rolling-window cap covers that second case by limiting total submit volume over time.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | D (Denial of Service) | Protects against sustained request flooding within a session. |
| OWASP Top 10 | A04:2021 - Insecure Design | Adds a missing throughput boundary for the core action. |
| CWE | CWE-799 - Improper Control of Interaction Frequency | Enforces a maximum action count per time window. |
| CWE | CWE-400 - Uncontrolled Resource Consumption | Reduces repeated reruns and state churn over time. |
| NIST SP 800-53 | SC-5 - Denial-of-Service Protection | This is a standard rate-based DoS mitigation pattern. |

### Change 7 - Audit trail for submit, win, and loss events (Lines 233-237, 272-301)

What changed:

```python
st.session_state.event_log.append(
    {
        "event": "submit",
        "at": time.time(),
        "attempts": st.session_state.attempts,
    }
)

...

st.session_state.event_log.append(
    {
        "event": "win",
        "at": time.time(),
        "score": st.session_state.score,
        "attempts": st.session_state.attempts,
    }
)

...

st.session_state.event_log.append(
    {
        "event": "loss",
        "at": time.time(),
        "score": st.session_state.score,
        "attempts": st.session_state.attempts,
    }
)
```

What it does: The app now records when a submit is attempted and when a game ends in a win or loss. In the same end-game block, a new best score is written back to disk only after the in-memory score is normalized through the current app flow.

Why it helps: Audit entries improve traceability for security-relevant actions. If the rate limiter fires or a game ends in an unexpected state, the session log gives concrete timestamps and context for what happened. This is the control that later got documented under the STRIDE repudiation category.

Frameworks:

| Framework | Control / ID | Relevance |
| --- | --- | --- |
| STRIDE | R (Repudiation) | Timestamped events make user actions within the session harder to deny or misinterpret. |
| OWASP Top 10 | A09:2021 - Security Logging and Monitoring Failures | Adds application-level logging for relevant state transitions. |
| CWE | CWE-778 - Insufficient Logging | The change adds the logging that was previously absent. |
| NIST SP 800-53 | AU-2 - Event Logging | Identifies and records security-relevant events. |
| NIST SP 800-53 | AU-3 - Content of Audit Records | Captures timestamps, attempts, score, and outcome metadata. |
| NIST SP 800-53 | AU-12 - Audit Record Generation | Generates records when the monitored events occur. |

## Summary Table

| # | File | Lines | What changed | Primary issue addressed | Primary framework(s) |
| --- | --- | --- | --- | --- | --- |
| 1 | app.py | 11, 21-34 | Defensive loading and saving of `high_score.json` | Malformed local data causing invalid state or crashes | STRIDE T (partial), NIST SI-10, SI-11, CWE-20 |
| 2 | app.py | 13-17 | Added cooldown and rolling-window constants | Missing interaction limits | STRIDE D, OWASP A04, CWE-799, NIST SC-5 |
| 3 | app.py | 124-138 | Persisted limiter and audit state in `st.session_state` | Controls resetting on Streamlit rerun | STRIDE D/R, OWASP A04/A09, NIST AU-2, AU-12 |
| 4 | app.py | 172-184 | Cleared limiter state and logged `new_game` | Stale limiter state and missing lifecycle trace | STRIDE D/R, OWASP A04/A09, NIST AU-12 |
| 5 | app.py | 196-210 | Blocked rapid-fire submits with cooldown | Rapid interaction abuse | STRIDE D, CWE-799, CWE-400, NIST SC-5 |
| 6 | app.py | 212-228 | Added rolling-window submit cap | Sustained request abuse | STRIDE D, CWE-799, CWE-400, NIST SC-5 |
| 7 | app.py | 233-237, 272-301 | Logged submit/win/loss events | Repudiation and weak monitoring | STRIDE R, OWASP A09, CWE-778, NIST AU-2/AU-3/AU-12 |

## Residual Risks and Design Notes

These are relevant to the security story, but they are not fully solved by the current implementation:

- `app.py` lines 151-157 expose the secret number and event log through `Developer Debug Info`. That is acceptable for the lab, but it would be an information-disclosure risk in a deployed build.
- The high-score file is normalized defensively, but it is still trusted local input. A user can still edit `high_score.json` directly because there is no integrity check, authentication, or access control around that file.
- The rate limiter is session-local because it relies on `st.session_state`. That is sufficient for a single-user lab app, but it is not equivalent to a server-side limiter keyed by account, IP, or device.
- The audit trail lives only in session memory. It improves visibility during a session, but it is not durable forensic logging.

## How to Verify the Current Controls

1. Run `python -m pytest`.
2. Run `python -m streamlit run app.py`.
3. Click `Submit Guess` rapidly to trigger the cooldown message.
4. Keep submitting until you trigger the rolling-window message.
5. Open `Developer Debug Info` and confirm that `event_log` records `new_game`, `submit`, `rate_limited_cooldown`, `rate_limited_window`, `win`, and `loss` as those actions happen.
6. Optionally place malformed JSON in `high_score.json` and confirm the app falls back to `0` instead of crashing.

## Verification Gap

The current automated tests in `tests/test_game_logic.py` cover gameplay logic and one state-initialization check, but they do not yet include dedicated regression tests for the rate limiter, audit log, or malformed high-score file handling. Those controls are currently verified primarily through manual testing.