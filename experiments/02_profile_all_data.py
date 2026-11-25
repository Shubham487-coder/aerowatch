"""Complete profile of N-CMAPSS: every file, every engine, every array.

Writes:
  docs/data/inventory.csv         one row per (file, array): shape and size
  docs/data/units.csv             one row per engine
  data/processed/flights.parquet  one row per flight, every variable summarised
"""

import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DOCS = ROOT / "docs" / "data"
PROC = ROOT / "data" / "processed"
GROUPS = ["W", "X_s", "X_v", "T"]  # Y (RUL) and A (labels) are handled separately
STATS = ["mean", "std", "min", "max"]


def names(f: h5py.File, key: str) -> list[str]:
    return [x.decode().strip() for x in np.array(f[key]).ravel()]


inventory, units, flights, nan_counts = [], [], [], {}
columns_seen = None

for path in sorted(RAW.glob("*.h5")):
    t0 = time.time()
    file_id = path.stem.replace("N-CMAPSS_", "")
    with h5py.File(path, "r") as f:
        # ---- Layer 1: inventory ----
        for key in f:
            ds = f[key]
            inventory.append(
                {
                    "file": file_id,
                    "array": key,
                    "rows": ds.shape[0],
                    "cols": ds.shape[1] if ds.ndim > 1 else 1,
                    "dtype": str(ds.dtype),
                    "size_mb": round(ds.size * ds.dtype.itemsize / 1e6, 1),
                }
            )

        a_cols = names(f, "A_var")
        var_cols = {g: names(f, f"{g}_var") for g in GROUPS}
        all_vars = [c for g in GROUPS for c in var_cols[g]]
        assert len(set(all_vars)) == len(all_vars), "duplicate column names across arrays"
        if columns_seen is None:
            columns_seen = (a_cols, var_cols)
        assert (a_cols, var_cols) == columns_seen, f"{file_id}: column names differ from first file"

        for split in ("dev", "test"):
            A = f[f"A_{split}"][:]
            unit_ids = A[:, a_cols.index("unit")]
            for unit in np.unique(unit_ids):
                idx = np.flatnonzero(unit_ids == unit)
                start, end = idx[0], idx[-1] + 1
                assert len(idx) == end - start, f"{file_id} unit {unit}: rows not contiguous"

                # ---- read this engine from every array ----
                blocks = {g: f[f"{g}_{split}"][start:end] for g in GROUPS}
                rul = f[f"Y_{split}"][start:end].ravel()
                for g, b in blocks.items():
                    nan_counts[(file_id, split, g)] = nan_counts.get((file_id, split, g), 0) + int(
                        np.isnan(b).sum()
                    )

                df = pd.DataFrame(np.hstack([blocks[g] for g in GROUPS]), columns=all_vars)
                df[a_cols] = A[start:end]
                df["RUL"] = rul

                # ---- checks ----
                assert df["Fc"].nunique() == 1, f"{file_id} unit {unit}: flight class changes"
                assert (df.groupby("cycle")["RUL"].nunique() == 1).all(), (
                    f"{file_id} unit {unit}: RUL changes inside a flight"
                )

                # ---- Layer 3: one row per flight ----
                g = df.groupby("cycle")
                fl = g[all_vars].agg(STATS)
                fl.columns = [f"{v}_{s}" for v, s in fl.columns]
                fl["duration_s"] = g.size()
                fl["hs"] = g["hs"].min()
                fl["RUL"] = g["RUL"].first()
                fl = fl.reset_index()
                fl.insert(0, "file", file_id)
                fl.insert(1, "split", split)
                fl.insert(2, "unit", int(unit))
                fl.insert(3, "flight_class", int(df["Fc"].iloc[0]))
                flights.append(fl)

                # ---- Layer 2: one row per engine ----
                last = int(fl["cycle"].max())
                fault = fl.loc[fl["hs"] == 0, "cycle"]
                units.append(
                    {
                        "file": file_id,
                        "split": split,
                        "unit": int(unit),
                        "flight_class": int(df["Fc"].iloc[0]),
                        "n_flights": len(fl),
                        "first_cycle": int(fl["cycle"].min()),
                        "last_cycle": last,
                        "avg_flight_min": round(fl["duration_s"].mean() / 60, 1),
                        "fault_starts_at": int(fault.min()) if len(fault) else None,
                        "rul_first": int(fl["RUL"].iloc[0]),
                        "rul_last": int(fl["RUL"].iloc[-1]),
                        "rul_is_countdown": bool((fl["RUL"] == last - fl["cycle"]).all()),
                    }
                )
    print(f"done {file_id:10s} in {time.time() - t0:5.1f} s")

# ---- save ----
DOCS.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)
inv = pd.DataFrame(inventory)
units_df = pd.DataFrame(units)
flights_df = pd.concat(flights, ignore_index=True)
inv.to_csv(DOCS / "inventory.csv", index=False)
units_df.to_csv(DOCS / "units.csv", index=False)
flights_df.to_parquet(PROC / "flights.parquet", index=False)

# ---- short summary ----
print("\nColumn names identical in all files: yes")
print("Total raw size (GB):", round(inv["size_mb"].sum() / 1000, 1))
print("Missing values (NaN) in total:", sum(nan_counts.values()))
print(
    "Engines:",
    len(units_df),
    "| Flights:",
    len(flights_df),
    "| Flight table columns:",
    flights_df.shape[1],
)
print("RUL is a clean countdown for every engine:", units_df["rul_is_countdown"].all())
print("\nEngines per flight class (1=short, 2=medium, 3=long):")
print(pd.crosstab(units_df["flight_class"], units_df["split"], margins=True))
