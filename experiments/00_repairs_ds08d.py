"""DS08d is 32 bytes shorter than its own header says (NASA's original file).
Try opening a padded COPY and check whether any data looks damaged."""

import shutil
from pathlib import Path

import h5py
import numpy as np

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
original = RAW / "N-CMAPSS_DS08d-010.h5"
backup = RAW / "N-CMAPSS_DS08d-010.h5.orig"

# 1-2. keep the original untouched, pad a copy
if not backup.exists():
    shutil.move(original, backup)
shutil.copyfile(backup, original)
with open(original, "ab") as fh:
    fh.write(b"\x00" * 32)
print("padded copy size:", original.stat().st_size)  # expect 2885034880

# 3-4. open and check
with h5py.File(original, "r") as f:
    for key in sorted(f.keys()):
        if key.endswith("_var"):
            continue
        data = f[key][:]
        msg = f"{key:10s} {str(data.shape):18s}"
        if key.startswith(("W_", "X_s_")):
            msg += f" exact zeros: {int((data == 0).sum()):>3}   NaN: {int(np.isnan(data).sum())}"
        print(msg)
