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

## Corrections

- A timestamp subtraction used unsigned integers. In logs where the first ground-truth sample precedes the first estimate sample (six of ten x500 logs and both VTOL logs), some plots and the time-trace script showed a wrong flat ground-truth line. Fixed with signed subtraction. The summary tables were identical before and after the fix (diff of summary.csv), so the x500 results above are unchanged.

## VTOL baseline (standard_vtol, hover only)

Same pipeline, model `gz_standard_vtol`, `MIS_TAKEOFF_ALT` = 10 m (read from the log). Five flights, wait before takeoff 122-133 s, about 60 s hold at altitude, hover window 49-63 s. One earlier exploratory flight (`vtol_explore_01`, 11 s window) is excluded from the statistics.

| Flight | Wait (s) | Estimate at takeoff command (m) | Setpoint hover (m) | Estimate hover (m) | True hover (m) | Setpoint - estimate (m) | Estimate - truth (m) |
|---|---|---|---|---|---|---|---|
| vtol_protocol_01 | 122 | +0.116 | 10.117 | 9.995 | 9.720 | +0.122 | +0.275 |
| vtol_protocol_02 | 132 | -0.065 | 9.931 | 9.968 | 10.056 | -0.037 | -0.088 |
| vtol_protocol_03 | 130 | -0.411 | 9.583 | 9.806 | 10.304 | -0.223 | -0.498 |
| vtol_protocol_04 | 133 | -0.032 | 9.973 | 9.850 | 9.585 | +0.123 | +0.264 |
| vtol_protocol_05 | 124 | +0.145 | 10.149 | 10.047 | 9.801 | +0.102 | +0.246 |
| **Mean** | 128.2 | -0.049 | 9.951 | 9.933 | 9.893 | +0.017 | +0.040 |
| **Std** | 4.9 | 0.222 | 0.225 | 0.101 | 0.287 | 0.150 | 0.337 |

### VTOL findings

1. The hover setpoint matches *(estimated altitude at the takeoff command) + 10 m* within 5 mm in all five flights (and in the exploratory flight). Not verified in the PX4 source.
2. Spread is much larger than on the x500: the estimate at the takeoff command has a std of 0.222 m (x500: 0.050 m), and true hover minus commanded altitude has a std of 0.287 m with a worst case of 41.5 cm (x500: 0.015 m and 2.9 cm).
3. The controller does not hold its setpoint as tightly as on the x500: setpoint minus estimate ranges from -22 cm to +12 cm (x500: -2 mm to +1 mm). Cause unknown.
4. While the aircraft sits on the ground, the altitude estimate wanders over a range of 18-53 cm within a flight (six VTOL flights, sampled every 20 s) versus 2.6-6.5 cm on the five x500 protocol flights. With 5 s block means over the pre-takeoff window used for the sensor comparisons below, it is 21.9-41.0 cm versus 5.1-7.0 cm. This explains why the estimate at the takeoff command varies so much. The cause is not identified. Ruled out with logged data: (a) barometer noise: the logged barometer is far noisier on the x500 (33-58 cm slow wander, about 20 cm noise) than on the VTOL (0.1-0.2 cm), yet the x500 estimate is the steadier one; (b) height configuration: `EKF2_HGT_REF`, `EKF2_BARO_CTRL`, `EKF2_GPS_CTRL` and `EKF2_BARO_NOISE` are identical in both models (only 8 of 184 `EKF2_`/`SENS_`/`IMU_` parameters differ: `EKF2_ARSP_THR`, `EKF2_BCOEF_X/Y`, `EKF2_FUSE_BETA`, `EKF2_MCOEF`, `EKF2_RNG_FOG`, `IMU_GYRO_RATEMAX`, `SENS_EN_ARSPDSIM`); (c) the GNSS height measurement: it is fused in 100% of ground samples in both models and wanders equally little (4.3-5.7 cm on the x500, 4.5-6.1 cm on the VTOL). The GNSS height innovation (measurement minus estimate) wanders 3.0-7.4 cm on the x500 and 19.5-36.6 cm on the VTOL, so the VTOL estimate drifts away from a stable, fused measurement (by construction, the innovation range mirrors the estimate range). Not tested: how strongly the filter weights that measurement, accelerometer and gyro noise models, and EKF-internal states.
5. The correlation between the estimate at takeoff and the estimate-minus-truth error at hover is r = 0.936 (slope 1.42, n = 5) but drops to r = 0.658 (slope 1.10) without `vtol_protocol_03`. It rests on a single extreme flight and is not reported as a finding.

### VTOL limitations

- Five flights, hover only. No transition or fault injection yet.
- The x500 and VTOL comparisons are between two different models and may reflect model or sensor configuration rather than vehicle type.
- Ground-truth zero offset was +0.095 m in the VTOL logs checked (x500: -0.013 m). It is subtracted before computing "true hover"; if wrong, absolute values shift by a constant, differences between flights do not.
- The VTOL SITL start reports an airspeed-sensor warning ("Switch to non-airspeed mode") and two parameter errors (`wrong type passed to param_get`, `param 65535 invalid`). They did not block takeoff and are unexplained.
- Ground-estimate wander is sampled every 20 s only.
