from pyulog import ULog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else "logs/baseline_x500_01.ulg"
TARGET = 2.5  # m, log'daki varsayılan kalkış irtifası

ulog = ULog(LOG)
df = pd.DataFrame(ulog.get_dataset("vehicle_local_position").data)
t = ((df["timestamp"] - df["timestamp"].iloc[0]) / 1e6).to_numpy()
alt = (-df["z"]).to_numpy()

# Uçuş penceresi: irtifa 0.3 m'yi aştığı bölge, 5 s pay ile
fly = np.where(alt > 0.3)[0]
t0, t1 = t[fly[0]] - 5, t[fly[-1]] + 5
m = (t >= t0) & (t <= t1)
tt, aa = t[m] - t0, alt[m]

# Metrikler
hover = aa[aa > 0.9 * aa.max()]
hover_mean, hover_std = hover.mean(), hover.std()
t_10 = tt[np.argmax(aa >= 0.1 * TARGET)]
t_90 = tt[np.argmax(aa >= 0.9 * TARGET)]
overshoot = (aa.max() - TARGET) / TARGET * 100
ground = alt[t < t[fly[0]] - 10]

print("Dosya:", LOG)
print("Toplam log süresi: %.0f s | Uçuş penceresi: %.0f s" % (t[-1], t1 - t0))
print("Zemin gürültüsü (std): %.3f m" % ground.std())
print("Maks irtifa: %.3f m" % aa.max())
print("Hover ortalama: %.3f m (std %.3f m)" % (hover_mean, hover_std))
print("Kalıcı durum hatası: %.3f m" % (TARGET - hover_mean))
print("Yükselme süresi (%%10-%%90): %.2f s" % (t_90 - t_10))
print("Aşım: %.1f %%" % overshoot)

plt.figure(figsize=(9, 4))
plt.plot(tt, aa, label="İrtifa tahmini")
plt.axhline(TARGET, color="r", linestyle="--", label="Hedef (2.5 m)")
plt.xlabel("Zaman (s)")
plt.ylabel("İrtifa (m)")
plt.title("Baseline x500: uçuş penceresi")
plt.legend()
plt.grid(True)
plt.savefig("reports/baseline_x500_01_flight_window.png", dpi=150)
