# Day 1: notebook checks (trainer)

The syllabus assessment for Day 1 is "10-question quiz on AI vocabulary and Python; notebook checks".
This sheet covers the notebook checks. Tick each row per participant.

Each check follows a lab's success criterion from the syllabus. Reference values come from running the course lab files on the course data. Participants who wrote their own code should get the same numbers on the same data.

Run each lab from the `aeroguard` folder (`python labs/day1/<file>.py`), or run its cells in VS Code.

| # | Lab | Check (syllabus success criterion) | How to verify | Reference value | Pass? |
|---|---|---|---|---|---|
| 1 | 1.1 | Check cell prints all library versions with no errors | Run `lab1_1_env_check.py` | Last line `Environment OK` | ☐ |
| 2 | 1.1 | LLM key stored in `.env`, not in the notebook | Open `.env`; search the lab files for `sk-`; `git status` must not list `.env` | Key only in `.env` | ☐ |
| 3 | 1.2 | Lists open-defect aircraft | Run `lab1_2_python_fleet.py` | `16 aircraft with open defects` | ☐ |
| 4 | 1.2 | Filters by ATA chapter | Same output | `53 ATA 79 write-ups` | ☐ |
| 5 | 1.2 | Rejects bad tail numbers | Same output | `rejected: not a tail number: 'XYZ'` and `'N1234567'` | ☐ |
| 6 | 1.3 | Invalid records are rejected with a clear error | Run `lab1_3_classes_pydantic.py` | `Rejected with 4 errors:` followed by 4 field messages | ☐ |
| 7 | 1.3 | Decorator, generator and async example run | Same output | `Engine (ATA 72) log lines: 54` and `3 lookups in 0.20s` (the time may vary slightly) | ☐ |
| 8 | 1.4 | Chart and top-5 table produced | Run `lab1_4_pandas.py`; open `storage/defects_per_month.png` | Top row `N226SH 34 Navigation 8`; chart file exists | ☐ |
| 9 | 1.5 | Both models trained | Run `lab1_5_ml_basics.py` | `MAE 362 kg` and `Accuracy: 0.39` | ☐ |
| 10 | 1.5 | Can explain which model is regression and which is classification | Ask: "Which model predicts a number, and how do we measure it?" | Regression: kg, measured by error (MAE). Classification: severity, measured by accuracy against a baseline. | ☐ |

**Quiz:** score ____ / 10 (`quiz_day1.md`; answer key at the bottom of that file).

**End-of-day deliverable (syllabus):** working environment (rows 1–2), completed Python notebook (rows 3–8), two small trained models (rows 9–10).
