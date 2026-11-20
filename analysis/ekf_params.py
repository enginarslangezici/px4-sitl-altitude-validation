from pyulog import ULog
import numpy as np
a = ULog("logs/protocol_x500_01.ulg")
b = ULog("logs/vtol_protocol_01.ulg")
pa, pb = a.initial_parameters, b.initial_parameters
names = sorted(n for n in set(pa) | set(pb) if n.startswith(("EKF2_", "SENS_", "IMU_")))
print("Farkli parametreler (x500 | vtol):")
n = 0
for k in names:
    va, vb = pa.get(k, "yok"), pb.get(k, "yok")
    if va != vb:
        print("  %-24s %12s | %s" % (k, va, vb)); n += 1
print("fark sayisi: %d / %d" % (n, len(names)))
print()
for tag, u in (("x500", a), ("vtol", b)):
    for mid in (0, 1):
        try:
            d = u.get_dataset("sensor_baro", mid)
            p = d.data["pressure"].astype("float64")
            print("%s sensor_baro[%d]: %d ornek, %d benzersiz deger, std %.3f Pa" % (tag, mid, len(p), len(np.unique(p)), p.std()))
        except Exception as e:
            print("%s sensor_baro[%d]: yok (%s)" % (tag, mid, type(e).__name__))
