"""Lab 2.4 — Milestone 1 backend: POST /chat calls the LLM.

Run from the aeroguard folder:
    uvicorn labs.day2.lab2_4_chat_api:app --reload --port 8002
Then try POST /chat in http://localhost:8002/docs
Starter version: labs/day2/starter/lab2_4_chat_api.py
"""
import re

from fastapi import FastAPI
from pydantic import BaseModel, Field

from labs.day2 import lab2_4_llm as llm

# Step 2: the system prompt (role - task - constraint)
SYSTEM_PROMPT = """ROLE: You are AeroGuard, an assistant for
aircraft maintenance technicians.
TASK: Summarise write-ups, suggest troubleshooting steps and
point to the maintenance manual or directives to check.
CONSTRAINTS:
- Advisory only. Never say an aircraft is airworthy or approve a
  return to service: a certificated person decides.
- If you name an ATA chapter, use only: 21 air conditioning,
  29 hydraulic power, 32 landing gear, 34 navigation,
  36 pneumatic/bleed, 49 APU, 72 engine, 79 engine oil.
- If unsure, say so. Never invent part numbers or AD numbers.
- Keep answers short. Decline topics outside maintenance."""

# The safety rule in code: a prompt is a request, not a control.
DECISION = re.compile(
    r"airworth|safe to (fly|dispatch)|return(ed)? to service"
    r"|sign (it )?off|release to service", re.IGNORECASE)
REFUSAL = ("I can't make airworthiness decisions. A "
           "certificated person must decide, using the "
           "manual and the records.")

app = FastAPI(title="Lab 2.4 — Maintenance Assistant")


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatOut(BaseModel):
    answer: str
    model: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatOut)
def chat(req: ChatIn) -> ChatOut:
    if DECISION.search(req.message):
        return ChatOut(answer=REFUSAL, model="guardrail")
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.message}]
    return ChatOut(answer=llm.chat(messages),
                   model=llm.model_name())
