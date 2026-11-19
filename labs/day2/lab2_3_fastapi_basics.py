"""Lab 2.3 — FastAPI basics: routes, Pydantic models, Swagger UI.

Run from the aeroguard folder:
    uvicorn labs.day2.lab2_3_fastapi_basics:app \
        --reload --port 8001
Then open http://localhost:8001/docs and try every route.
Starter version: labs/day2/starter/lab2_3_fastapi_basics.py
"""
import csv
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi import Path as PathParam
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
TAIL = r"^N[0-9]{1,5}[A-Z]{0,2}$"  # same rule as Lab 1.3

with open(ROOT / "data" / "fleet.csv", newline="") as f:
    FLEET = {row["tail_number"]: row
             for row in csv.DictReader(f)}

app = FastAPI(title="Lab 2.3 — FastAPI basics")


# Step 1: routes
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Step 2: a typed response model
class Aircraft(BaseModel):
    tail_number: str
    model: str
    engine_type: str
    flight_hours: int
    base: str


@app.get("/aircraft/{tail}", response_model=Aircraft)
def get_aircraft(
        tail: str = PathParam(pattern=TAIL)) -> Aircraft:
    row = FLEET.get(tail)
    if row is None:
        raise HTTPException(404, f"Unknown aircraft {tail}")
    return Aircraft(**row)  # CSV text becomes int here


# Step 2: a typed request model (the Day 1 Defect as a body)
class DefectIn(BaseModel):
    tail_number: str = Field(pattern=TAIL)
    ata_chapter: int = Field(ge=0, le=99)
    description: str = Field(min_length=5)
    severity: Literal["minor", "major", "critical"]


class DefectOut(DefectIn):
    defect_id: int


DEFECTS: list[DefectOut] = []  # in memory; a database on Day 3


@app.post("/defects", response_model=DefectOut, status_code=201)
def add_defect(defect: DefectIn) -> DefectOut:
    saved = DefectOut(defect_id=len(DEFECTS) + 1,
                      **defect.model_dump())
    DEFECTS.append(saved)
    return saved
