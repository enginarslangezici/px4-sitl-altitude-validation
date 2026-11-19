from pyulog import ULog
import pandas as pd
import numpy as np
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/baseline_x500_01.ulg"
u = ULog(LOG)
est = pd.DataFrame(u.get_dataset("vehicle_local_position").data)
sp = pd.DataFrame(u.get_dataset("vehicle_local_position_setpoint").data)

t0 = est["timestamp"].iloc[0]
te = ((est["timestamp"] - t0) / 1e6).to_numpy()
ae = (-est["z"]).to_numpy()
ts = ((sp["timestamp"] - t0) / 1e6).to_numpy()
asp = (-sp["z"]).to_numpy()
ok = ~np.isnan(asp)

f0 = te[np.where(ae > 0.3)[0][0]]
print("Kalkış (irtifa>0.3 m): %.1f s" % f0)
print("MIS_TAKEOFF_ALT:", u.initial_parameters.get("MIS_TAKEOFF_ALT", "log'da yok"))
print()
print("%8s %10s %12s" % ("t-f0 (s)", "tahmin (m)", "setpoint (m)"))
for dt in range(-10, 3):
    t = f0 + dt
    e = np.interp(t, te, ae)
    if ts[ok].min() <= t <= ts[ok].max():
        s = "%.3f" % np.interp(t, ts[ok], asp[ok])
    else:
        s = "yok"
    print("%8d %10.3f %12s" % (dt, e, s))
