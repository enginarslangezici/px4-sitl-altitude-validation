from pyulog import ULog
import numpy as np, glob
files = sorted(glob.glob("logs/protocol_x500_0*.ulg")) + sorted(glob.glob("logs/vtol_protocol_0*.ulg"))
print("%-22s %8s %7s %8s %14s %15s" % ("log", "yerde(s)", "ornek", "fused_%", "olcum_yavas_cm", "yenilik_yavas_cm"))
first = True
for p in files:
    u = ULog(p)
    est = u.get_dataset("vehicle_local_position")
    t0 = int(est.data["timestamp"][0])
    te = (est.data["timestamp"].astype("int64") - t0) / 1e6
    f0 = te[np.where(-est.data["z"] > 0.3)[0][0]]
    try:
        g = u.get_dataset("estimator_aid_src_gnss_hgt", 0)
    except Exception as e:
        print(p, "estimator_aid_src_gnss_hgt yok:", type(e).__name__)
        continue
    if first:
        print("alanlar:", list(g.data.keys()))
        first = False
    if "observation" not in g.data or "innovation" not in g.data:
        print(p, "observation/innovation alani yok")
        continue
    tg = (g.data["timestamp"].astype("int64") - t0) / 1e6
    m = (tg > 10) & (tg < f0 - 5)
    if m.sum() < 10:
        print(p, "yerde yeterli ornek yok:", int(m.sum()))
        continue
    tt = tg[m]
    obs = g.data["observation"][m].astype("float64") * 100
    inn = g.data["innovation"][m].astype("float64") * 100
    fu = g.data["fused"][m].astype("float64").mean() * 100 if "fused" in g.data else float("nan")
    def slow(x):
        b = [x[(tt >= s) & (tt < s + 5)].mean() for s in np.arange(tt.min(), tt.max() - 5, 5) if np.any((tt >= s) & (tt < s + 5))]
        return max(b) - min(b)
    print("%-22s %8.0f %7d %8.0f %14.1f %15.1f" % (p.split("/")[-1], f0 - 15, int(m.sum()), fu, slow(obs), slow(inn)))
