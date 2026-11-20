from pyulog import ULog
import numpy as np, glob
for p in sorted(glob.glob("logs/vtol_*.ulg")):
    u = ULog(p)
    d = u.get_dataset("vehicle_local_position")
    t = (d.data["timestamp"].astype("int64") - int(d.data["timestamp"][0])) / 1e6
    a = -d.data["z"]
    f0 = t[np.where(a > 0.3)[0][0]]
    pts = list(np.arange(10, f0 - 1, 20)) + [f0 - 5]
    print(p.split("/")[-1], "kalkis %.0f s" % f0)
    print("   " + "  ".join("%3.0fs:%+.3f" % (x, np.interp(x, t, a)) for x in pts))
