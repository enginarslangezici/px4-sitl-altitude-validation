from pyulog import ULog
import pandas as pd
import numpy as np
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/baseline_x500_01.ulg"
u = ULog(LOG)
sp = pd.DataFrame(u.get_dataset("vehicle_local_position_setpoint").data)
a = (-sp["z"]).to_numpy()
a = a[~np.isnan(a)]
first, peak = a[0], a.max()
print("Dosya:", LOG)
print("İlk setpoint: %.3f m | Tepe setpoint: %.3f m" % (first, peak))
print("Tepe - ilk = %.3f m (MIS_TAKEOFF_ALT=%s)" % (peak - first, u.initial_parameters.get("MIS_TAKEOFF_ALT")))
