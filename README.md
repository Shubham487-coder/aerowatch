# Aerowatch

A self-healing MLOps system that predicts the remaining useful life (RUL) of aircraft turbofan engines, in flights, with
an uncertainty range.

The system watches its incoming data for drift, retrains itself when the world changes, compares the new model fairly
against the current one, tests it in shadow mode, and promotes it only if it is proven better. No human in the loop.

**Status:** Phase 0 (setup). Work in progress.

## Data

NASA N-CMAPSS (Arias Chao et al., *Data*, 2021), from the NASA Prognostics Center of Excellence data repository, entry
17 "Turbofan Engine Degradation Simulation Data Set-2". 9 of the 10 files are used (DS08d is truncated in the official
archive). The data is not stored in this repository.
