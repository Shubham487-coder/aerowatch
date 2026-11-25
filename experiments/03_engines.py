"""Layer 2: understand the 99 engines (reads docs/data/units.csv, no raw data)."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
u = pd.read_csv(ROOT / "docs" / "data" / "units.csv")
pd.set_option("display.width", 200, "display.max_rows", 200)

print("1) Engines per file and flight class (1=short, 2=medium, 3=long)")
print(pd.crosstab(u["file"], u["flight_class"], margins=True))

print("\n2) Average flight length in minutes, per class")
print(u.groupby("flight_class")["avg_flight_min"].describe()[["min", "mean", "max"]].round(0))

print("\n3) Lifetime (number of flights), per class")
print(u.groupby("flight_class")["n_flights"].describe()[["min", "mean", "max"]].round(0))

print("\n4) When the fault starts, as % of the engine's life")
u["fault_pct"] = 100 * (u["fault_starts_at"] - u["first_cycle"]) / u["n_flights"]
print(u.groupby("flight_class")["fault_pct"].describe()[["min", "mean", "max"]].round(0))

print("\n5) First flight number, dev vs test")
print(u.groupby("split")["first_cycle"].agg(["min", "max"]))
