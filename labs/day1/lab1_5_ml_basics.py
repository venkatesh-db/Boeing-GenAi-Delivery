# %% [markdown]
# # Lab 1.5 — Two tiny ML demos
# Regression predicts a number.
# Classification predicts a category.

# %%
from pathlib import Path

import pandas as pd
from sklearn.linear_model import (LinearRegression,
                                  LogisticRegression)
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split

HERE = Path(__file__) if "__file__" in globals() else None
ROOT = (HERE.resolve().parents[2] if HERE
        else Path.cwd().parents[1])

# %% Regression: fuel burn from flight distance
flights = pd.read_csv(ROOT / "data" / "flights.csv")  # 1 load
X = flights[["distance_nm"]]                          #   feature
y = flights["fuel_burn_kg"]                           #   target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0)             # 2 split
reg = LinearRegression().fit(X_train, y_train)        # 3 fit
pred = reg.predict(X_test)                            # 4 predict
mae = mean_absolute_error(y_test, pred)               # 5 measure
print(f"Fuel ≈ {reg.intercept_:.0f} + "
      f"{reg.coef_[0]:.2f} × distance  (MAE {mae:.0f} kg)")

# %% Use the model: fuel for a new 1,500 nm flight
new = pd.DataFrame({"distance_nm": [1500]})
kg = round(float(reg.predict(new)[0]))
print("Fuel for 1,500 nm:", kg, "kg")

# %% Compare predictions with what really happened
compare = X_test.assign(actual_kg=y_test,
                        predicted_kg=pred.round())
compare["error_kg"] = compare.predicted_kg - compare.actual_kg
print(compare.head(5).to_string(index=False))

# %% Classification: severity from ATA chapter and hours
logs = pd.read_csv(ROOT / "data" / "maintenance_logs.csv")
ata = pd.get_dummies(logs["ata_chapter"].astype(str),
                     prefix="ata")                   # 1 features
X = ata.assign(hours=logs["flight_hours_at_report"] / 10_000)
y = logs["severity"]                                 #   target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0,
    stratify=y)                                      # 2 split
clf = LogisticRegression(max_iter=1000,
                         class_weight="balanced")
clf.fit(X_train, y_train)                            # 3 fit
pred_cls = clf.predict(X_test)                       # 4 predict
acc = accuracy_score(y_test, pred_cls)               # 5 measure
base = y_test.value_counts(normalize=True).max()
print("Accuracy:", round(acc, 2))
print("Baseline (always the most common class):", round(base, 2))

# %% Compare classification predictions with actual values
check = pd.DataFrame({"actual": y_test.values,
                      "predicted": pred_cls})
print(check.head(8).to_string(index=False))
print(pd.crosstab(y_test, pred_cls,
                  rownames=["actual"], colnames=["predicted"]))

# %% Discuss
print("Accuracy is below the baseline, yet the model finds")
print("most critical defects; the baseline finds none.")
print("ATA chapter and hours are weak features: the text")
print("matters (Day 3, with precision and recall).")
print("Regression = a number (error in kg).")
print("Classification = a category (accuracy, confusion table).")
