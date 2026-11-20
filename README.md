# PX4 SITL Altitude-Hold Validation (x500, Gazebo)

A small, reproducible test pipeline for PX4 software-in-the-loop (SITL) flights: record a flight, extract metrics from the ULog, and compare what the controller was told to do (setpoint), what the flight stack believed (estimate) and what the simulator knows (ground truth).

This is the baseline stage. The same pipeline is meant to be reused for fault-injection tests on a quadplane VTOL model.

## Goal

Characterize altitude hold after PX4's default takeoff and separate **controller error** from **state-estimation error**.

## Setup

- PX4-Autopilot v1.18.0-beta1 (SITL), Gazebo 8.15, model `gz_x500`
- Windows 11, WSL2 (Ubuntu 24.04), QGroundControl connected as GCS
- Python: pyulog, pandas, matplotlib

## Method

1. Start `make px4_sitl gz_x500`, wait, then `commander takeoff` (`MIS_TAKEOFF_ALT` = 2.5 m).
2. Hold about 30 s, then `commander land`.
3. Compare three ULog signals: `vehicle_local_position_setpoint`, `vehicle_local_position` (estimate) and `vehicle_local_position_groundtruth` (Gazebo).
4. Ground truth is zeroed with its mean value before takeoff (about -0.013 m). This is an assumption.
5. Hover window: samples where the setpoint is within 5 cm of its peak, trimmed by 5 s on each side.

## Results (5 protocol flights, wait before takeoff 120-158 s)

| Flight | Wait (s) | Estimate at takeoff command (m) | Setpoint hover (m) | True hover (m) | Estimate - truth (m) |
|---|---|---|---|---|---|
| protocol_01 | 158 | -0.008 | 2.487 | 2.472 | +0.016 |
| protocol_02 | 154 | +0.058 | 2.549 | 2.504 | +0.044 |
| protocol_03 | 132 | -0.023 | 2.469 | 2.493 | -0.022 |
| protocol_04 | 120 | -0.072 | 2.423 | 2.471 | -0.048 |
| protocol_05 | 129 | -0.052 | 2.448 | 2.474 | -0.024 |
| **Mean** | 138.6 | -0.019 | 2.475 | 2.483 | -0.007 |
| **Std** | 16.5 | 0.050 | 0.048 | 0.015 | 0.036 |

## Findings

1. The controller holds its setpoint within 2 mm of the estimated altitude (setpoint - estimate: -2 to +1 mm in all five flights).
2. The hover setpoint matches *(estimated altitude at the takeoff command) + 2.5 m* within 8 mm in these flights, and within 1.1 cm across all ten flights recorded. This is consistent with the data but was **not verified in the PX4 source**.
3. The estimate offset at takeoff correlates with the estimate-minus-truth error at hover (r = 0.958, slope 0.70, n = 5). Descriptive only, not a mechanism claim.
4. True hover altitude stays within 2.9 cm of 2.5 m, while the setpoint itself varies by up to 7.7 cm.

## Limitations

- Only 5 protocol flights; the correlation in finding 3 can be driven by single points.
- Wait before takeoff varied (120-158 s); only 3 flights are inside the intended 130-160 s window.
- SITL only. Results depend on Gazebo's sensor noise model and do not transfer to real hardware.
- The ground-truth zero point is an assumption (see Method). If wrong, "true hover" shifts by a constant, but differences between flights do not change.
- Earlier exploratory flights (`baseline_*`, `longwait_*`, `short_*`) used different conditions and are excluded from the statistics. They are listed in `reports/summary.csv`.
- WSL2 produced `vehicle_imu` timestamp warnings in some flights.
- An early analysis used the commanded 2.5 m as the target and reported a false 6 cm controller error. It was corrected after comparing setpoint, estimate and ground truth.

## Repository layout

- `analysis/` - metric and comparison scripts (`summarize.py`, `compare_altitude.py`, `protocol_stats.py`, ...)
- `reports/` - plots and summary tables
- `save_flight.sh` - copies the newest log, refuses duplicates, updates the summary table and commits
- `logs/` - raw `.ulg` files (git-ignored because of size)

## Reproduce

```
python3 -m venv .venv
.venv/bin/pip install pyulog pandas matplotlib
.venv/bin/python3 analysis/summarize.py
.venv/bin/python3 analysis/protocol_stats.py
```

Raw logs are not in the repository. The tables above come from `reports/summary.csv`.
