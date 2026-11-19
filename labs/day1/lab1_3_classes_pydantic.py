# %% [markdown]
# # Lab 1.3 — Classes, dataclasses, Pydantic,
# # decorators, generators and async

# %%
import asyncio
import csv
import time
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Iterator, Literal

from pydantic import (BaseModel, Field, ValidationError,
                      field_validator)

HERE = Path(__file__) if "__file__" in globals() else None
ROOT = (HERE.resolve().parents[2] if HERE
        else Path.cwd().parents[1])
LOGS = ROOT / "data" / "maintenance_logs.csv"


# %% A plain class with type hints
class PlainDefect:
    def __init__(self, tail_number: str, ata_chapter: int,
                 severity: str) -> None:
        self.tail_number = tail_number
        self.ata_chapter = ata_chapter
        self.severity = severity

    def is_engine(self) -> bool:
        return self.ata_chapter in (72, 79)


bad = PlainDefect("ABC", 172, "urgent")  # hints are not checks
print(bad.tail_number, bad.ata_chapter, bad.severity)
print("engine defect:", bad.is_engine())


# %% Dataclass: __init__ and __repr__ written for you
@dataclass(frozen=True)
class Aircraft:
    tail_number: str
    model: str
    flight_hours: int
    engines: tuple[str, ...] = field(default_factory=tuple)

    def is_high_time(self, limit: int = 40_000) -> bool:
        return self.flight_hours > limit


ac = Aircraft("N123AB", "737-800", 41_847,
              ("N123AB-E1", "N123AB-E2"))
print(ac)
print("high time:", ac.is_high_time())


# %% Pydantic model: validation at the boundary
class Defect(BaseModel):
    tail_number: str = Field(pattern=r"^N[0-9]{1,5}[A-Z]{0,2}$")
    ata_chapter: int = Field(ge=0, le=99)
    description: str = Field(min_length=5)
    severity: Literal["minor", "major", "critical"]

    @field_validator("description")
    @classmethod
    def capitalize_first(cls, v: str) -> str:
        return v[0].upper() + v[1:]


good = Defect(tail_number="N123AB", ata_chapter=72,
              description="engine 2 vibration high",
              severity="major")
print(good.model_dump())

# %% From a CSV row: Pydantic turns the text "34" into 34
with open(LOGS, newline="") as f:
    row = next(csv.DictReader(f))
keys = ["tail_number", "ata_chapter", "description", "severity"]
d = Defect(**{k: row[k] for k in keys})
print(repr(row["ata_chapter"]), "->", repr(d.ata_chapter))

# %% Bad input: every problem reported at once
try:
    Defect(tail_number="ABC", ata_chapter=172,
           description="bad", severity="urgent")
except ValidationError as err:
    print(f"Rejected with {err.error_count()} errors:")
    for e in err.errors():
        print("  ", e["loc"], e["msg"])


# %% Decorator: time any function
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        ms = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {ms:.1f} ms")
        return result
    return wrapper


# %% Generator: stream log lines, one at a time
def stream_logs(path: Path) -> Iterator[str]:
    with open(path) as f:
        next(f)  # skip header
        for line in f:
            yield line.rstrip()


@timed
def count_engine_logs() -> int:
    lines = stream_logs(LOGS)
    return sum(1 for line in lines if ",72," in line)


print("Engine (ATA 72) log lines:", count_engine_logs())


# %% async / await: run slow lookups at the same time
async def fetch_status(tail: str) -> str:
    await asyncio.sleep(0.2)  # stands in for a network call
    return f"{tail}: status fetched"


async def main() -> list[str]:
    tails = ["N123AB", "N107BE", "N114CH"]
    jobs = [fetch_status(t) for t in tails]
    return await asyncio.gather(*jobs)


start = time.perf_counter()
# In a notebook or VS Code cell a loop is already running:
# there, write  results = await main()  instead.
results = asyncio.run(main())
print(results)
elapsed = time.perf_counter() - start
print(f"3 lookups in {elapsed:.2f}s, not 0.6s")
