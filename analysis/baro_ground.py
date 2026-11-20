from pyulog import ULog
import numpy as np, glob
files = sorted(glob.glob("logs/protocol_x500_0*.ulg")) + sorted(glob.glob("logs/vtol_protocol_0*.ulg"))
print("%-22s %8s %14s %12s %14s" % ("log", "yerde(s)", "baro_yavas_cm", "baro_std_cm", "tahmin_yavas_cm"))
for p in files:
    u = ULog(p)
    est = u.get_dataset("vehicle_local_position")
    te = (est.data["timestamp"].astype("int64") - int(est.data["timestamp"][0])) / 1e6
    ae = -est.data["z"]
    f0 = te[np.where(ae > 0.3)[0][0]]
    names = [d.name for d in u.data_list if d.name == "sensor_baro"]
    if not names:
        print(p, "sensor_baro yok; baro topic'leri:", sorted(set(d.name for d in u.data_list if "baro" in d.name)))
        continue
    b = u.get_dataset("sensor_baro", 0)
    if "pressure" not in b.data:
        print(p, "pressure alani yok, alanlar:", list(b.data.keys())); continue
    tb = (b.data["timestamp"].astype("int64") - int(est.data["timestamp"][0])) / 1e6
    pr = b.data["pressure"].astype("float64")
    m = (tb > 10) & (tb < f0 - 5)
    h = 44330.0 * (1.0 - (pr[m] / pr[m].mean()) ** 0.1903) * 100.0
    tt = tb[m]
    blocks = [h[(tt >= s) & (tt < s + 5)].mean() for s in np.arange(tt.min(), tt.max() - 5, 5)]
    within = np.mean([h[(tt >= s) & (tt < s + 5)].std() for s in np.arange(tt.min(), tt.max() - 5, 5)])
    em = (te > 10) & (te < f0 - 5)
    eb = [ae[em][(te[em] >= s) & (te[em] < s + 5)].mean() * 100 for s in np.arange(te[em].min(), te[em].max() - 5, 5)]
    print("%-22s %8.0f %14.1f %12.1f %14.1f" % (p.split("/")[-1], f0 - 15, max(blocks) - min(blocks), within, max(eb) - min(eb)))
