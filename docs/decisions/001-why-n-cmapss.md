# 001: Use NASA N-CMAPSS as the dataset

- **Date:** 2026-11-26
- **Status:** accepted

## Situation

AeroWatch needs data where engines are followed from new until failure, so the true remaining life is known for every
flight. It also needs a realistic change in the data over time, so the self-healing loop (drift detection, retraining,
promotion) can be shown and measured.

## Decision

Use NASA's N-CMAPSS dataset (Arias Chao et al., Data 2021). Real flight recordings from airliners were flown through
NASA's engine simulator, and each engine was worn out until it failed. Every engine is a complete life, with sensor
readings every second.

Three properties decided it:

- **Three route types** (short, medium, long-haul). Short-haul engines differ on almost every sensor and also live
  longer, which gives a real, measurable change for the drift scenario.
- **Different failure types per file** (fan, compressors, turbines). This gives a second kind of change to test the "
  model got worse" alarm.
- **The true health of each engine part is included.** It is never used as model input, but it lets me check offline
  that the drift detector reacts to real changes.

## Other options considered

- **Original C-MAPSS (2008):** very widely used, but only one snapshot per flight and no realistic route changes, so
  there is little natural drift to detect.
- **Real airline data:** not publicly available, and real engines are removed before they fail, so the full life to
  failure is rarely recorded.

## What follows from this

- The data is large (about 15 GB download, 29 GB unpacked), so each flight is summarised into one row (decision record
  002).
- 9 of the 10 files are used. DS08d is truncated in NASA's own archive, a known issue that other researchers also
  exclude. That leaves 99 engines and 7,473 flights.
- The engines are simulated, with accelerated ageing (lives of about 50 to 100 flights instead of thousands). The method
  transfers to real fleets; the absolute numbers do not. This goes into `docs/limitations.md`.
- File sizes and checksums will be recorded, so a damaged file is refused automatically.
