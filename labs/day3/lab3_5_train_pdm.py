# %% [markdown]
# # Lab 3.5 — Train the component-failure model
# Remaining useful life (regression) + "fails within 30 cycles" (classification) on C-MAPSS-format data.

# %%
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard import pdm  # noqa: E402

train = pdm.load("train")
print(train.shape, "rows;", train["unit"].nunique(), "engines run to failure")
# RUL label: cycles left until this engine failed (training engines are run to failure)
train["rul"] = train.groupby("unit")["cycle"].transform("max") - train["cycle"]
print(train[["unit", "cycle", "rul"]].head(3))
# Features: level (rolling mean), spread (rolling std) and trend (how fast the mean is moving)
print(pdm.add_features(train).tail(3)[["unit", "cycle", "s4_mean", "s4_std", "s4_trend"]])

# %% Train and evaluate
result = pdm.train()
print(f"RUL error (RMSE): {result.rmse:.1f} cycles")
print(f"Fails-within-30-cycles  precision {result.precision:.2f}  recall {result.recall:.2f}")
print(f"Test engines near failure: caught {result.caught_failures}, MISSED {result.missed_failures}, "
      f"false alarms {result.false_alarms}")
print("Recall matters most: a missed failure (false negative) is the costliest error;")
print("a false alarm only costs an extra inspection.")
print("Saved to", result.model_path)

# %% Try the capstone engine
print(pdm.predict("N123AB-E2"))
print(pdm.predict("N123AB-E1"))
