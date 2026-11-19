from pyulog import ULog
import pandas as pd
import numpy as np
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/baseline_x500_01.ulg"
u = ULog(LOG)
est = pd.DataFrame(u.get_dataset("vehicle_local_position").data)
sp = pd.DataFrame(u.get_dataset("vehicle_local_position_setpoint").data)
alt_cmd = float(u.initial_parameters.get("MIS_TAKEOFF_ALT", 2.5))

t0 = est["timestamp"].iloc[0]
te = ((est["timestamp"] - t0) / 1e6).to_numpy()
ae = (-est["z"]).to_numpy()
ts = ((sp["timestamp"] - t0) / 1e6).to_numpy()
asp = (-sp["z"]).to_numpy()
ok = ~np.isnan(asp)
ts, asp = ts[ok], asp[ok]

peak = asp.max()
implied_ref = peak - alt_cmd
w = (te >= ts[0] - 3) & (te <= ts[0])
est_ref = ae[w].mean()
f0 = te[np.where(ae > 0.3)[0][0]]

print("Dosya:", LOG)
print("PX4 baslangicindan kalkisa kadar: %.0f s" % f0)
print("Tepe setpoint: %.3f m | MIS_TAKEOFF_ALT: %.1f m" % (peak, alt_cmd))
print("Ima edilen referans (tepe - MIS_TAKEOFF_ALT): %.3f m" % implied_ref)
print("Ilk setpoint oncesi 3 s tahmin ortalamasi: %.3f m" % est_ref)
print("Fark: %.3f m" % (implied_ref - est_ref))
