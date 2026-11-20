from pyulog import ULog
import pandas as pd, numpy as np, sys
LOG = sys.argv[1]
u = ULog(LOG)
est = pd.DataFrame(u.get_dataset("vehicle_local_position").data)
sp = pd.DataFrame(u.get_dataset("vehicle_local_position_setpoint").data)
gt = pd.DataFrame(u.get_dataset("vehicle_local_position_groundtruth").data)
t0 = est["timestamp"].iloc[0]
sec = lambda d: ((d["timestamp"] - t0) / 1e6).to_numpy()
te, ae = sec(est), (-est["z"]).to_numpy()
ts, asp = sec(sp), (-sp["z"]).to_numpy()
tg, ag = sec(gt), (-gt["z"]).to_numpy()
ok = ~np.isnan(asp)
ts, asp = ts[ok], asp[ok]
f0 = te[np.where(ae > 0.3)[0][0]]
off = ag[tg < f0 - 10].mean()
print("Kalkis: %.1f s | GT zemin ofseti: %.3f m" % (f0, off))
print("%8s %10s %10s %10s" % ("t-f0 (s)", "setpoint", "tahmin", "gercek"))
for dt in range(0, 100, 5):
    t = f0 + dt
    s = np.interp(t, ts, asp) if ts.min() <= t <= ts.max() else float("nan")
    print("%8d %10.3f %10.3f %10.3f" % (dt, s, np.interp(t, te, ae), np.interp(t, tg, ag) - off))
