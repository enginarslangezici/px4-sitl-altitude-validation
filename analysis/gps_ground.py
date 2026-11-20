from pyulog import ULog
import numpy as np, glob
files = sorted(glob.glob("logs/protocol_x500_0*.ulg")) + sorted(glob.glob("logs/vtol_protocol_0*.ulg"))
print("%-22s %8s %14s %12s %7s" % ("log", "yerde(s)", "gps_yavas_cm", "gps_std_cm", "ornek"))
for p in files:
    u = ULog(p)
    est = u.get_dataset("vehicle_local_position")
    t0 = int(est.data["timestamp"][0])
    te = (est.data["timestamp"].astype("int64") - t0) / 1e6
    f0 = te[np.where(-est.data["z"] > 0.3)[0][0]]
    try:
        g = u.get_dataset("sensor_gps", 0)
    except Exception:
        print(p, "sensor_gps yok; gps/gnss topic'leri:", sorted(set(d.name for d in u.data_list if "gps" in d.name or "gnss" in d.name)))
        continue
    if "altitude_msl_m" in g.data:
        alt = g.data["altitude_msl_m"].astype("float64") * 100.0
    elif "alt" in g.data:
        alt = g.data["alt"].astype("float64") / 10.0
    else:
        print(p, "yukseklik alani yok, alanlar:", list(g.data.keys()))
        continue
    tg = (g.data["timestamp"].astype("int64") - t0) / 1e6
    m = (tg > 10) & (tg < f0 - 5)
    if m.sum() < 10:
        print(p, "yerde yeterli GPS ornegi yok:", int(m.sum()))
        continue
    h, tt = alt[m], tg[m]
    blocks = [h[(tt >= s) & (tt < s + 5)].mean() for s in np.arange(tt.min(), tt.max() - 5, 5) if np.sum((tt >= s) & (tt < s + 5)) > 0]
    print("%-22s %8.0f %14.1f %12.1f %7d" % (p.split("/")[-1], f0 - 15, max(blocks) - min(blocks), h.std(), int(m.sum())))
