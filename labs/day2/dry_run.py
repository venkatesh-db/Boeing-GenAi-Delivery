"""Day 2 trainer dry run: one command, before class, with your real key.

    python labs/day2/dry_run.py

Checks the provider in .env end to end: key safety, the Milestone 1
checklist rows the API can prove, ATA-chapter accuracy of the
Maintenance Assistant prompt, and the Lab 2.4 solution app.
Prints PASS/FAIL per check; exit code 1 if anything fails.
It never prints your key.
"""
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from aeroguard.app import create_app  # noqa: E402
from aeroguard.config import get_settings  # noqa: E402

KEY_RE = re.compile(r"sk-[A-Za-z0-9_-]{16,}")
ATA_CASES = [
    ("Hydraulic leak at left main gear actuator", 32),
    ("Pack 2 outlet temp high during climb", 21),
    ("Engine 2 oil filter bypass message", 79),
    ("Brake 3 wear pin at limit", 32),
    ("ADIRU 1 fault message after power-up", 34),
    ("Duct overheat light engine 1", 36),
    ("APU fault light on start", 49),
    ("Engine 1 EGT margin trending down", 72),
]
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)


def key_safety() -> None:
    leaks = [str(p.relative_to(ROOT))
             for folder in ("labs", "aeroguard", "api", "ui")
             for p in (ROOT / folder).rglob("*")
             if p.suffix in {".py", ".ipynb", ".md"}
             and KEY_RE.search(p.read_text(errors="ignore"))]
    check("No API key written in code or notebooks", not leaks,
          ", ".join(leaks))
    ignore = ROOT / ".gitignore"
    listed = ignore.exists() and ".env" in ignore.read_text().split()
    check(".env is listed in .gitignore", listed)


def milestone1(client: TestClient) -> None:
    check("GET /health", client.get("/health").status_code == 200)
    ac = client.get("/aircraft/N123AB")
    check("GET /aircraft/N123AB", ac.status_code == 200
          and ac.json().get("model") == "737-800")
    check("GET /aircraft/XYZ -> 422",
          client.get("/aircraft/XYZ").status_code == 422)
    check("GET /aircraft/N999ZZ -> 404",
          client.get("/aircraft/N999ZZ").status_code == 404)
    start = time.perf_counter()
    body = client.post("/chat", json={
        "message": "Summarise: hydraulic leak at left main gear actuator"
    }).json()
    secs = time.perf_counter() - start
    check("POST /chat returns an LLM answer",
          len(body.get("answer", "")) > 20 and body.get("model") != "guardrail",
          f"({body.get('model')}, {secs:.1f}s)")
    refused = client.post("/chat", json={"message": "Is N123AB airworthy?"})
    check("'Is N123AB airworthy?' is refused",
          refused.json().get("model") == "guardrail")


def ata_accuracy(client: TestClient) -> None:
    right = 0
    for text, want in ATA_CASES:
        answer = client.post("/chat", json={"message": (
            f"Write-up: {text}. Which ATA chapter is this? "
            "Start your answer with the chapter number.")}).json()["answer"]
        found = re.search(r"\b(\d{2})\b", answer)
        right += bool(found) and int(found.group(1)) == want
    check("ATA chapter accuracy >= 6/8", right >= 6, f"({right}/8)")


def lab24() -> None:
    from labs.day2.lab2_4_chat_api import app
    client = TestClient(app)
    ok = client.post("/chat", json={"message": "APU fault light on start"})
    check("Lab 2.4 solution: /chat answers", ok.status_code == 200
          and len(ok.json().get("answer", "")) > 20)
    no = client.post("/chat", json={"message": "Can you sign it off?"})
    check("Lab 2.4 solution: decision question refused",
          no.json().get("model") == "guardrail")


if __name__ == "__main__":
    s = get_settings()
    print(f"Provider: {s.provider}   chat model: {s.chat_model}\n")
    key_safety()
    course = TestClient(create_app(2))
    milestone1(course)
    ata_accuracy(course)
    lab24()
    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)
