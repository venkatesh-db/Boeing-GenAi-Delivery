"""Lab 2.4 STARTER — Milestone 1 backend: POST /chat calls the LLM.

Run from the aeroguard folder:
    uvicorn labs.day2.starter.lab2_4_chat_api:app --reload --port 8002
Fill in every TODO. Solution: labs/day2/lab2_4_chat_api.py
"""
import re  # noqa: F401

from fastapi import FastAPI
from pydantic import BaseModel, Field

from labs.day2.starter import lab2_4_llm as llm  # noqa: F401

# TODO step 2: write the Maintenance Assistant system prompt.
#   Use ROLE / TASK / CONSTRAINTS (Lab 2.2). Must include:
#   advisory only, never certify airworthiness, the allowed ATA
#   chapters, "if unsure, say so", stay on maintenance topics.
SYSTEM_PROMPT = "TODO"

app = FastAPI(title="Lab 2.4 — Maintenance Assistant (starter)")


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatOut(BaseModel):
    answer: str
    model: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# TODO step 2: POST /chat (response_model=ChatOut)
#   1. If the message asks for an airworthiness decision, return a
#      fixed refusal with model="guardrail" (a regex, as in Lab 2.2).
#   2. Otherwise send [system prompt, user message] to llm.chat
#      and return the answer with llm.model_name().
