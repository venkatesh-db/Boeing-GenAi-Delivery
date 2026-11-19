"""Generate the course datasets. Run once:  python data/generate_data.py

All data is SYNTHETIC and for training only (no real aircraft, people or records).

Outputs in data/:
  fleet.csv             20 aircraft
  engines.csv           2 engines per aircraft, mapped to a C-MAPSS-format unit
  maintenance_logs.csv  ~400 technician write-ups (squawks)
  ad_compliance.csv     which training ADs apply to each aircraft and their status
  flights.csv           flight distance vs fuel burn (Day 1 regression demo)
  cmapss/train_FD001.txt, test_FD001.txt, RUL_FD001.txt
      Engine run-to-failure data in the NASA C-MAPSS FD001 file format.
      If you have the real NASA C-MAPSS files, drop them in data/cmapss/ instead.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(42)

MODELS = [("737-800", "CFM56-7B"), ("737 MAX 8", "LEAP-1B"), ("787-9", "GEnx-1B"), ("777-300ER", "GE90-115B")]
BASES = ["SEA", "DFW", "ORD", "ATL", "DEN"]
TECHS = ["Alex Morgan", "Priya Raman", "Diego Alvarez", "Mei Chen", "Sam Okafor", "Lena Fischer"]

# ATA chapter -> (component, typical write-ups, severity weights minor/major/critical)
ATA = {
    21: ("Air conditioning pack", ["Pack {n} outlet temp high during climb", "Cabin too warm, pack {n} flow low"], (0.6, 0.35, 0.05)),
    29: ("Hydraulic pump", ["Hyd sys {s} pressure fluctuating", "Hyd pump {n} low pressure light on taxi"], (0.3, 0.5, 0.2)),
    32: ("Landing gear", ["Brake {n} wear pin at limit", "Nose gear steering shimmy on landing roll", "Main gear tire {n} cut found on walkaround"], (0.4, 0.45, 0.15)),
    34: ("Navigation", ["ADIRU {n} fault message after power-up", "Weather radar intermittent"], (0.6, 0.35, 0.05)),
    36: ("Pneumatic bleed", ["Bleed trip off engine {n} at high power", "Duct overheat light engine {n}"], (0.3, 0.5, 0.2)),
    49: ("APU", ["APU auto shutdown on start", "APU EGT high during ground ops"], (0.5, 0.4, 0.1)),
    72: ("Engine", ["Engine {n} vibration N1 above normal in cruise", "Engine {n} EGT margin trending down", "Engine {n} oil consumption high"], (0.2, 0.5, 0.3)),
    79: ("Engine oil", ["Engine {n} low oil pressure indication", "Engine {n} oil filter bypass message"], (0.2, 0.5, 0.3)),
}

TRAINING_ADS = [
    # ad_number, aircraft model, ATA, subject
    ("AD 2026-TR-0101", "737-800", 72, "CFM56-7B fan blade inspection"),
    ("AD 2026-TR-0102", "737 MAX 8", 36, "Bleed air duct clamp replacement"),
    ("AD 2026-TR-0103", "787-9", 29, "Hydraulic pump case drain filter inspection"),
    ("AD 2026-TR-0104", "777-300ER", 32, "Main landing gear axle inspection"),
    ("AD 2026-TR-0105", "ALL", 79, "Engine oil pressure transmitter replacement"),
]


def make_fleet() -> pd.DataFrame:
    rows = []
    for i in range(20):
        model, engine = MODELS[i % len(MODELS)]
        tail = f"N{100 + i * 7}{chr(65 + i % 26)}{chr(66 + (i * 3) % 24)}"
        year = int(rng.integers(2012, 2024))
        hours = int((2026 - year) * rng.integers(2600, 3400))
        rows.append({
            "tail_number": tail, "model": model, "engine_type": engine, "delivery_year": year,
            "flight_hours": hours, "flight_cycles": int(hours / rng.uniform(1.6, 3.2)),
            "base": BASES[i % len(BASES)],
        })
    fleet = pd.DataFrame(rows)
    fleet.loc[0, "tail_number"] = "N123AB"  # the aircraft used in the capstone example
    return fleet


def make_engines(fleet: pd.DataFrame, n_test_units: int) -> pd.DataFrame:
    rows = []
    unit = 1
    for tail in fleet["tail_number"]:
        for pos in (1, 2):
            rows.append({"engine_id": f"{tail}-E{pos}", "tail_number": tail, "position": pos,
                         "cmapss_unit": ((unit - 1) % n_test_units) + 1})
            unit += 1
    return pd.DataFrame(rows)


def make_logs(fleet: pd.DataFrame) -> pd.DataFrame:
    rows = []
    start = date(2026, 1, 1)
    for i in range(400):
        ac = fleet.iloc[int(rng.integers(len(fleet)))]
        ata = int(rng.choice(list(ATA)))
        component, texts, weights = ATA[ata]
        text = str(rng.choice(texts)).format(n=int(rng.integers(1, 3)), s=str(rng.choice(["A", "B"])))
        severity = str(rng.choice(["minor", "major", "critical"], p=weights))
        d = start + timedelta(days=int(rng.integers(0, 300)))
        rows.append({
            "log_id": f"ML-{10000 + i}", "date": d.isoformat(), "tail_number": ac.tail_number,
            "ata_chapter": ata, "component": component, "description": text, "severity": severity,
            "status": "open" if (d > date(2026, 9, 15) and rng.random() < 0.5) else "closed",
            "technician": str(rng.choice(TECHS)), "flight_hours_at_report": int(ac.flight_hours - rng.integers(0, 2000)),
        })
    # Recurring engine-2 trend on the capstone aircraft
    for k, txt in enumerate(["Engine 2 vibration N1 above normal in cruise", "Engine 2 EGT margin trending down",
                             "Engine 2 vibration N1 above normal, recurring"]):
        rows.append({"log_id": f"ML-2{k:04d}", "date": (date(2026, 9, 20) + timedelta(days=12 * k)).isoformat(),
                     "tail_number": "N123AB", "ata_chapter": 72, "component": "Engine", "description": txt,
                     "severity": "major", "status": "open" if k == 2 else "closed",
                     "technician": TECHS[k], "flight_hours_at_report": int(fleet.loc[0, "flight_hours"]) - 60 + 20 * k})
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def make_ad_compliance(fleet: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, ac in fleet.iterrows():
        for ad, model, ata, subject in TRAINING_ADS:
            if model in ("ALL", ac.model):
                complied = rng.random() < 0.75
                rows.append({"tail_number": ac.tail_number, "ad_number": ad, "ata_chapter": ata, "subject": subject,
                             "status": "complied" if complied else "open",
                             "complied_date": (date(2026, 1, 1) + timedelta(days=int(rng.integers(0, 280)))).isoformat() if complied else ""})
    df = pd.DataFrame(rows)
    # Make the capstone aircraft have one open engine AD
    mask = (df.tail_number == "N123AB") & (df.ad_number == "AD 2026-TR-0101")
    df.loc[mask, ["status", "complied_date"]] = ["open", ""]
    return df


def make_flights() -> pd.DataFrame:
    distance = rng.uniform(300, 3500, 300)
    fuel = 1800 + distance * 3.1 + rng.normal(0, 450, 300)  # kg, rough narrow-body figure
    return pd.DataFrame({"distance_nm": distance.round(0), "fuel_burn_kg": fuel.round(0)})


def make_cmapss(n_train: int = 100, n_test: int = 100) -> None:
    """Synthetic engines in the C-MAPSS FD001 layout: unit, cycle, 3 settings, 21 sensors."""
    base = np.array([518.67, 642.5, 1590.0, 1400.0, 14.62, 21.61, 553.9, 2388.0, 9050.0, 1.3, 47.5, 521.7,
                     2388.0, 8140.0, 8.44, 0.03, 392.0, 2388.0, 100.0, 38.8, 23.3])
    drift = np.array([0, 0.6, 9, 12, 0, 0, -1.0, 0.07, 9, 0, 0.35, -0.9, 0.07, 8, 0.05, 0, 3.0, 0, 0, -0.3, -0.18])
    noise = np.array([0, 0.5, 6, 9, 0, 0.001, 0.9, 0.07, 4, 0, 0.27, 0.7, 0.07, 3, 0.04, 0, 1.5, 0, 0, 0.18, 0.11])

    def engine(life: int, cycles: int) -> np.ndarray:
        t = np.arange(1, cycles + 1)
        wear = np.exp(4.0 * t / life) - 1  # slow start, fast at the end of life
        wear = wear / (np.exp(4.0) - 1)
        settings = np.column_stack([rng.normal(0, 0.002, cycles), rng.normal(0, 0.0003, cycles), np.full(cycles, 100.0)])
        sensors = base + np.outer(wear, drift) + rng.normal(0, 1, (cycles, 21)) * noise
        return np.column_stack([t, settings, sensors])

    out = OUT / "cmapss"
    out.mkdir(exist_ok=True)
    fmt = "%d %d " + " ".join(["%.4f"] * 24)
    train = []
    for u in range(1, n_train + 1):
        life = int(rng.integers(130, 360))
        train.append(np.column_stack([np.full(life, u), engine(life, life)]))
    np.savetxt(out / "train_FD001.txt", np.vstack(train), fmt=fmt)

    test, rul = [], []
    for u in range(1, n_test + 1):
        life = int(rng.integers(130, 360))
        seen = int(rng.integers(int(life * 0.3), life - 5))
        test.append(np.column_stack([np.full(seen, u), engine(life, life)[:seen]]))
        rul.append(life - seen)
    # Capstone engine N123AB-E2 maps to test unit 2: make it close to failure
    life = 300
    seen = 285
    test[1] = np.column_stack([np.full(seen, 2), engine(life, life)[:seen]])
    rul[1] = life - seen
    np.savetxt(out / "test_FD001.txt", np.vstack(test), fmt=fmt)
    np.savetxt(out / "RUL_FD001.txt", np.array(rul), fmt="%d")


def main() -> None:
    fleet = make_fleet()
    fleet.to_csv(OUT / "fleet.csv", index=False)
    make_engines(fleet, n_test_units=100).to_csv(OUT / "engines.csv", index=False)
    make_logs(fleet).to_csv(OUT / "maintenance_logs.csv", index=False)
    make_ad_compliance(fleet).to_csv(OUT / "ad_compliance.csv", index=False)
    make_flights().to_csv(OUT / "flights.csv", index=False)
    if not (OUT / "cmapss" / "REAL_NASA_DATA").exists():
        make_cmapss()
    print("Datasets written to", OUT)


if __name__ == "__main__":
    main()
