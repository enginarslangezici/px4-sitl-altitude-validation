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
f0 = te[np.where(ae > 0.3)[0][0]]
pre = (te > f0 - 30) & (te < f0 - 5)

ground = ae[pre].mean()
print("Kalkıştan 30-5 s önce, yerdeki tahmin: %.3f m (std %.3f)" % (ground, ae[pre].std()))
print("Yerdeki tahmin + 2.5 m = %.3f m" % (ground + 2.5))
print("Setpoint tepe değeri   = %.3f m" % np.nanmax((-sp["z"]).to_numpy()))
