"""First look at N-CMAPSS. Exploration only: lives in experiments/, never imported by src/."""

from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "N-CMAPSS_DS01-005.h5"
UNIT = 1  # which engine to look at


def column_names(f: h5py.File, key: str) -> list[str]:
    """The *_var arrays store column names as bytes; turn them into normal strings."""
    return [
        x.decode().strip() if isinstance(x, bytes) else str(x) for x in np.array(f[key]).ravel()
    ]


with h5py.File(DATA_FILE, "r") as f:
    # 1. What is inside the file (shapes only, nothing loaded yet)
    print("Arrays in the file:")
    for key in f:
        print(f"  {key:10s} {str(f[key].shape):18s} {f[key].dtype}")

    a_cols = column_names(f, "A_var")
    w_cols = column_names(f, "W_var")
    xs_cols = column_names(f, "X_s_var")
    print("\nA columns:", a_cols, "\nW columns:", w_cols, "\nX_s columns:", xs_cols)

    # 2. Find the rows of one engine using the small A array
    A = f["A_dev"][:]
    unit_ids = A[:, a_cols.index("unit")]
    print("\nEngines in dev:", np.unique(unit_ids).astype(int))

    rows = np.flatnonzero(unit_ids == UNIT)
    start, end = rows[0], rows[-1] + 1
    assert len(rows) == end - start, "rows of one unit are not stored together"

    # 3. Read only that slice and build one table
    df = pd.DataFrame(
        np.hstack(
            [A[start:end], f["W_dev"][start:end], f["X_s_dev"][start:end], f["Y_dev"][start:end]]
        ),
        columns=a_cols + w_cols + xs_cols + ["RUL"],
    )

pd.set_option("display.width", 200, "display.max_columns", 30)
print(f"\nUnit {UNIT}: {len(df):,} rows (one per second), {df['cycle'].nunique()} flights")
print(df.head())
print(df.describe().T[["mean", "std", "min", "max"]])

sensor = "T48" if "T48" in xs_cols else xs_cols[0]
alt = w_cols[0]  # altitude

# 4. One flight
first = df[df["cycle"] == df["cycle"].min()]
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 6))
ax[0].plot(first[alt].to_numpy())
ax[0].set_ylabel(alt)
ax[0].set_title(f"Unit {UNIT}, first flight")
ax[1].plot(first[sensor].to_numpy())
ax[1].set_ylabel(sensor)
ax[1].set_xlabel("seconds into flight")

# 5. Whole life: one number per flight
per_flight = df.groupby("cycle").agg(sensor_mean=(sensor, "mean"), rul=("RUL", "first"))
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(10, 6))
ax[0].plot(per_flight.index, per_flight["sensor_mean"])
ax[0].set_ylabel(f"mean {sensor} per flight")
ax[0].set_title(f"Unit {UNIT}, whole life")
ax[1].plot(per_flight.index, per_flight["rul"])
ax[1].set_ylabel("RUL (flights left)")
ax[1].set_xlabel("cycle (flight number)")

plt.show()
