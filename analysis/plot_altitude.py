from pyulog import ULog
import pandas as pd
import matplotlib.pyplot as plt

ulog = ULog("logs/baseline_x500_01.ulg")
data = ulog.get_dataset("vehicle_local_position")
df = pd.DataFrame(data.data)

t = (df["timestamp"] - df["timestamp"].iloc[0]) / 1e6   # mikro saniye -> saniye
alt = -df["z"]                                          # NED'de z aşağı pozitif, o yüzden eksi

plt.figure(figsize=(9, 4))
plt.plot(t, alt)
plt.xlabel("Zaman (s)")
plt.ylabel("İrtifa (m)")
plt.title("Baseline x500 ilk uçuş: irtifa")
plt.grid(True)
plt.savefig("reports/baseline_x500_01_altitude.png", dpi=150)
print("Kaydedildi. Maks irtifa: %.2f m" % alt.max())
