# Day 1 Quiz — AI vocabulary and Python (10 questions)

1. Which is the broadest term: AI, ML, DL or GenAI?
2. Give one aviation example of ML that is *not* GenAI.
3. Predicting fuel burn in kg is regression or classification?
4. Predicting defect severity (minor / major / critical) is regression or classification?
5. Why do we split data into train and test sets?
6. What does `{row["tail_number"] for row in logs}` return — list, dict or set — and why use it?
7. In `def f(*args, **kwargs)`, what types are `args` and `kwargs`?
8. When does a `finally:` block run?
9. What does a Pydantic model do when you pass `tail_number="XYZ"` and the field requires a valid tail number?
10. Where should the OpenAI API key live — in the notebook, in `.env`, or in Git? Why?

---

## Answer key (trainer)

1. AI (ML ⊂ AI, DL ⊂ ML, GenAI is mostly built on DL).
2. Predicting remaining useful life of an engine from sensor data; detecting cracks in borescope images.
3. Regression — the output is a number.
4. Classification — the output is a category.
5. To measure how the model does on data it has never seen (avoid fooling ourselves).
6. A set — unique tail numbers, no duplicates.
7. `args` is a tuple, `kwargs` is a dict.
8. Always — after `try`, whether or not an exception happened.
9. It raises a `ValidationError` with a clear message; the bad record is rejected.
10. In `.env`, which is git-ignored. Never in the notebook or Git — they get shared.
