"""Lab 2.3 STARTER — FastAPI basics. Fill in every TODO.

Run from the aeroguard folder:
    uvicorn labs.day2.starter.lab2_3_fastapi_basics:app --reload --port 8001
Open http://localhost:8001/docs after each step to see your routes.
Solution: labs/day2/lab2_3_fastapi_basics.py
"""
import csv
from pathlib import Path
from typing import Literal  # noqa: F401  (you need it in step 2)

from fastapi import FastAPI, HTTPException  # noqa: F401
from fastapi import Path as PathParam  # noqa: F401
from pydantic import BaseModel, Field  # noqa: F401

ROOT = Path(__file__).resolve().parents[3]
TAIL = r"^N[0-9]{1,5}[A-Z]{0,2}$"  # same rule as Lab 1.3

with open(ROOT / "data" / "fleet.csv", newline="") as f:
    FLEET = {row["tail_number"]: row for row in csv.DictReader(f)}

app = FastAPI(title="Lab 2.3 — FastAPI basics (starter)")


# Step 1: routes. /health is done for you as an example.
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# TODO step 2a: a response model `Aircraft` with tail_number, model,
#   engine_type, flight_hours (int) and base.
# TODO step 1b: GET /aircraft/{tail}
#   - validate `tail` with PathParam(pattern=TAIL)
#   - look it up in FLEET; unknown tail -> HTTPException(404, ...)
#   - return Aircraft(**row)
# Check in Swagger: N123AB -> 200, N999ZZ -> 404, XYZ -> 422.


# TODO step 2b: a request model `DefectIn` (the Day 1 Defect):
#   tail_number (pattern=TAIL), ata_chapter (0-99),
#   description (min 5 chars), severity: minor / major / critical.
# TODO step 2c: `DefectOut(DefectIn)` that adds defect_id: int, and
#   POST /defects (status_code=201) that stores and returns it.
# Check in Swagger: a bad severity -> 422 with a clear message.
