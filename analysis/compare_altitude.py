from pyulog import ULog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys

LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/baseline_x500_01.ulg"
name = os.path.splitext(os.path.basename(LOG))[0]
ulog = ULog(LOG)

est = pd.DataFrame(ulog.get_dataset("vehicle_local_position").data)
sp = pd.DataFrame(ulog.get_dataset("vehicle_local_position_setpoint").data)
gt = pd.DataFrame(ulog.get_dataset("vehicle_local_position_groundtruth").data)

t_start = est["timestamp"].iloc[0]
def tsec(df):
    return ((df["timestamp"].astype("int64") - int(t_start)) / 1e6).to_numpy()

t_e, a_e = tsec(est), (-est["z"]).to_numpy()
t_s, a_s = tsec(sp), (-sp["z"]).to_numpy()
t_g, a_g = tsec(gt), (-gt["z"]).to_numpy()

# Uçuş penceresi (tahmine göre)
fly = np.where(a_e > 0.3)[0]
f0, f1 = t_e[fly[0]], t_e[fly[-1]]
w0, w1 = f0 - 5, f1 + 5

# Groundtruth'u yerdeki (kalkış öncesi) ortalamaya göre sıfırla
pre = t_g < f0 - 10
gt_offset = a_g[pre].mean() if pre.any() else 0.0
a_g = a_g - gt_offset

# Hover penceresi: setpoint'in tepe değerine yakın bölge, kenarlardan 5 s içeride
valid = ~np.isnan(a_s)
target = np.nanmax(a_s[valid])
hv = t_s[valid & (a_s >= target - 0.05)]
h0, h1 = hv.min() + 5, hv.max() - 5

def hover_stats(t, a):
    m = (t >= h0) & (t <= h1) & ~np.isnan(a)
    return a[m].mean(), a[m].std()

sp_m, sp_s = hover_stats(t_s, a_s)
es_m, es_s = hover_stats(t_e, a_e)
gt_m, gt_s = hover_stats(t_g, a_g)

print("Dosya:", LOG)
print("Hover penceresi: %.1f - %.1f s (%.1f s)" % (h0, h1, h1 - h0))
print("Groundtruth zemin ofseti: %.3f m (çıkarıldı)" % gt_offset)
print("Setpoint   ort: %.3f m (std %.3f)" % (sp_m, sp_s))
print("Tahmin     ort: %.3f m (std %.3f)" % (es_m, es_s))
print("Gerçek(GT) ort: %.3f m (std %.3f)" % (gt_m, gt_s))
print("Hata  setpoint-tahmin : %.3f m" % (sp_m - es_m))
print("Hata  setpoint-gerçek : %.3f m" % (sp_m - gt_m))
print("Hata  tahmin-gerçek   : %.3f m" % (es_m - gt_m))

plt.figure(figsize=(9, 4))
plt.plot(t_s[valid] - w0, a_s[valid], "r--", label="Setpoint (hedef)")
plt.plot(t_e - w0, a_e, label="PX4 tahmini")
plt.plot(t_g - w0, a_g, label="Gerçek (groundtruth)")
plt.xlim(0, w1 - w0)
plt.xlabel("Zaman (s)")
plt.ylabel("İrtifa (m)")
plt.title(name + ": setpoint / tahmin / gerçek")
plt.legend()
plt.grid(True)
plt.savefig("reports/%s_compare.png" % name, dpi=150)
print("Grafik: reports/%s_compare.png" % name)
