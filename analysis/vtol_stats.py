import pandas as pd, numpy as np
d = pd.read_csv("reports/summary.csv")
v = d[d["log"].str.startswith("vtol_protocol_")].copy()
v["sp_eksi_tahmin_m"] = v["sp_hover_m"] - v["tahmin_hover_m"]
v["gt_hata_m"] = v["gt_hover_m"] - 10.0
v["ref_farki_m"] = v["ima_edilen_ref_m"] - v["ref_tahmin_m"]
cols = ["bekleme_s","hover_s","ref_tahmin_m","sp_hover_m","tahmin_hover_m","gt_hover_m","sp_eksi_tahmin_m","tahmin_eksi_gt_m","gt_hata_m","ref_farki_m"]
print(v[["log"]+cols].round(3).to_string(index=False))
print()
print(v[cols].agg(["mean","std","min","max"]).round(3).to_string())
x, y = v["ref_tahmin_m"], v["tahmin_eksi_gt_m"]
print()
print("n = %d" % len(v))
print("korelasyon: %.3f | egim: %.3f" % (x.corr(y), np.polyfit(x, y, 1)[0]))
w = v[v["log"] != "vtol_protocol_03"]
print("protocol_03 haric: korelasyon %.3f | egim %.3f" % (w["ref_tahmin_m"].corr(w["tahmin_eksi_gt_m"]), np.polyfit(w["ref_tahmin_m"], w["tahmin_eksi_gt_m"], 1)[0]))
v.to_csv("reports/vtol_protocol_summary.csv", index=False)
