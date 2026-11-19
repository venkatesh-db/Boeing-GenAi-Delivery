# %% [markdown]
# # Lab 1.4 — Pandas analysis of maintenance logs

# %%
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save to file; remove in Jupyter
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__) if "__file__" in globals() else None
ROOT = (HERE.resolve().parents[2] if HERE
        else Path.cwd().parents[1])
DATA = ROOT / "data"

# %% Load: one CSV file becomes one DataFrame
logs = pd.read_csv(DATA / "maintenance_logs.csv",
                   parse_dates=["date"])
fleet = pd.read_csv(DATA / "fleet.csv")
print(logs.shape, fleet.shape)
print(logs[["log_id", "tail_number", "ata_chapter",
            "severity"]].head(3))

# %% Filter rows, then count write-ups per tail number
open_crit = logs[(logs["status"] == "open")
                 & (logs["severity"] == "critical")]
print(len(open_crit), "open critical write-ups")
per_tail = logs.groupby("tail_number").size()
print(per_tail.sort_values(ascending=False).head(3))

# %% Write-ups per ATA chapter
by_ata = (logs.groupby(["ata_chapter", "component"]).size()
          .sort_values(ascending=False))
print(by_ata.head(5))

# %% Top 5 recurring defects (same aircraft, same ATA chapter)
recurring = (
    logs.groupby(["tail_number", "ata_chapter", "component"])
    .size().rename("count").reset_index()
    .sort_values("count", ascending=False).head(5)
)
print(recurring.to_string(index=False))

# %% Severity mix per component
print(pd.crosstab(logs["component"], logs["severity"]))

# %% Join with the fleet: write-ups per aircraft, by model
per_model = (
    logs.merge(fleet, on="tail_number").groupby("model")
    .agg(defects=("log_id", "count"),
         aircraft=("tail_number", "nunique"))
)
per_model["per_aircraft"] = (per_model["defects"]
                             / per_model["aircraft"]).round(1)
print(per_model)

# %% NumPy: fast maths on whole columns
import numpy as np  # noqa: E402

hours = fleet["flight_hours"].to_numpy()
cycles = fleet["flight_cycles"].to_numpy()
print("mean:", round(np.mean(hours)),
      "median:", round(np.median(hours)),
      "p90:", round(np.percentile(hours, 90)))
high = int(np.sum(hours > 40_000))
print("over 40,000 h:", high, "of", hours.size)
print("hours per cycle:", np.round(hours / cycles, 2)[:5])

# %% Write-ups per month chart
monthly = logs.set_index("date").resample("MS").size()
monthly.index = monthly.index.strftime("%b")
ax = monthly.plot(kind="bar", figsize=(8, 3),
                  title="Maintenance write-ups per month")
ax.set_xlabel("Month (2026)")
ax.set_ylabel("Write-ups")
plt.tight_layout()
out = ROOT / "storage" / "defects_per_month.png"
out.parent.mkdir(exist_ok=True)
plt.savefig(out, dpi=150)
print("Chart saved to", out.name)
print(monthly.to_dict())
