from pyulog import ULog
import pandas as pd
import numpy as np
import glob, os

rows = []
for path in sorted(glob.glob("logs/*.ulg")):
    u = ULog(path)
    est = pd.DataFrame(u.get_dataset("vehicle_local_position").data)
    sp = pd.DataFrame(u.get_dataset("vehicle_local_position_setpoint").data)
    gt = pd.DataFrame(u.get_dataset("vehicle_local_position_groundtruth").data)
    cmd = float(u.initial_parameters.get("MIS_TAKEOFF_ALT", 2.5))

    t0 = est["timestamp"].iloc[0]
    sec = lambda d: ((d["timestamp"] - t0) / 1e6).to_numpy()
    te, ae = sec(est), (-est["z"]).to_numpy()
    ts, asp = sec(sp), (-sp["z"]).to_numpy()
    tg, ag = sec(gt), (-gt["z"]).to_numpy()
    ok = ~np.isnan(asp)
    ts, asp = ts[ok], asp[ok]

    f0 = te[np.where(ae > 0.3)[0][0]]
    ag = ag - ag[tg < f0 - 10].mean()          # zemin ofsetini cikar
    peak = asp.max()
    hv = ts[asp >= peak - 0.05]
    h0, h1 = hv.min() + 5, hv.max() - 5
    mean_in = lambda t, a: a[(t >= h0) & (t <= h1)].mean()

    ref = ae[(te >= ts[0] - 3) & (te <= ts[0])].mean()
    rows.append({
        "log": os.path.basename(path).replace(".ulg", ""),
        "bekleme_s": round(f0),
        "ref_tahmin_m": round(ref, 3),
        "ima_edilen_ref_m": round(peak - cmd, 3),
        "sp_hover_m": round(mean_in(ts, asp), 3),
        "tahmin_hover_m": round(mean_in(te, ae), 3),
        "gt_hover_m": round(mean_in(tg, ag), 3),
        "tahmin_eksi_gt_m": round(mean_in(te, ae) - mean_in(tg, ag), 3),
        "hover_s": round(h1 - h0, 1),
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv("reports/summary.csv", index=False)
print("Kaydedildi: reports/summary.csv")
