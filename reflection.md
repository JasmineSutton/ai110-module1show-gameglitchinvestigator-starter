# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
The math for the game isn't working. I narrowed the numbers down to 8/9 but the answer was 69, is it changing each guess? Score is negative, possibly intended. Attempts allowed says 8 but user only gets 5. There's no check for if the number given was already guessed. 
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  I used ChatGPT for this project
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  The agent suggested the changes for the Higher and Lower hints being reversed
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  It was giving a lot of errors when attempting to run pytest because the initial fix to hints did not align with the function behavior. 

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  If the behavior was now as I expected.
- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
  Pytest found that the attempts initialized at 1 instead of 0, which affected the attempt counting
- Did AI help you design or understand any tests? How?
  Yes, I identified the bugs I wanted to address and it helped me make tests based on my concerns. 

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
The Steamlit reruns kept reassigning the value
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  It is the re-execution of a script anytime a user interacts with the application. All values are recalculated and can reset, and the session_state is used for memory persistance. 
- What change did you make that finally gave the game a stable secret number?
  Only set the session_state when missing or resetting the game. 
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects? 
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  I think asking AI to help me with test cases is a great approach I will be using in the future.

- What is one thing you would do differently next time you work with AI on a coding task?
I think I'd ask it to consider the functionality of the overall code beyond the quick-fix it is trying to perform for one section. 

- In one or two sentences, describe how this project changed the way you think about AI generated code.
I think AI generated code has potential to help, but also has the great potential to make a codebase that doesn't work, that is also outside of the scope of the developers' understanding. I think it can be a great tool, but I also see the potential and I do think it can cut down quite a bit of time if used appropriately. 
