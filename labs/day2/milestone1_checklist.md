# Day 2 — Milestone 1 demo checklist (AeroGuard v1)

Run: `uvicorn api.day2:app --reload` and `AEROGUARD_DAY=2 streamlit run ui/app.py`

Trainer, before class: `python labs/day2/dry_run.py` checks rows 1–5 and 7 automatically with the key in `.env`, plus ATA-chapter accuracy and the Lab 2.4 solution.

| # | Check | How | Pass? |
|---|---|---|---|
| 1 | `.env` holds the key; it is not in code or notebooks, and `.env` is git-ignored | open `.env`; `grep -rn "sk-" labs aeroguard api ui` finds nothing; `.gitignore` lists `.env` | ☐ |
| 2 | `GET /health` returns `{"status":"ok"}` | http://localhost:8000/docs | ☐ |
| 3 | `GET /aircraft/N123AB` returns the aircraft | Swagger | ☐ |
| 4 | `GET /aircraft/XYZ` returns 422, `/aircraft/N999ZZ` returns 404 | Swagger | ☐ |
| 5 | `POST /chat` returns an LLM answer | Swagger | ☐ |
| 6 | Chat page answers "Summarise: hydraulic leak at left main gear actuator" | UI | ☐ |
| 7 | "Is N123AB airworthy?" is refused | UI | ☐ |
| 8 | Stop uvicorn → UI shows "Cannot reach the backend", no crash | UI | ☐ |
| 9 | Switch provider (`LLM_PROVIDER=ollama`) without code changes (optional) | `.env` | ☐ |
| 10 | Lab 2.2 prompt checklist score recorded | `lab2_2_prompting.py` | ☐ |

Participants' own Milestone 1 (Labs 2.3–2.5) follows the same rows. Starters are in `labs/day2/starter/`; solutions are `lab2_3_fastapi_basics.py`, `lab2_4_llm.py` + `lab2_4_chat_api.py` and `lab2_5_streamlit_chat.py`.
