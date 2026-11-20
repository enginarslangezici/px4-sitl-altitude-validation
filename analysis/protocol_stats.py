import pandas as pd, numpy as np
d = pd.read_csv("reports/summary.csv")
p = d[d["log"].str.startswith("protocol_")].copy()
p["sp_eksi_tahmin_m"] = p["sp_hover_m"] - p["tahmin_hover_m"]
p["gt_hata_m"] = p["gt_hover_m"] - 2.5
p["ref_farki_m"] = p["ima_edilen_ref_m"] - p["ref_tahmin_m"]
cols = ["bekleme_s","ref_tahmin_m","sp_hover_m","gt_hover_m","tahmin_eksi_gt_m","sp_eksi_tahmin_m","gt_hata_m","ref_farki_m"]
print(p[["log"]+cols].round(3).to_string(index=False))
print()
print(p[cols].agg(["mean","std","min","max"]).round(3).to_string())
x, y = p["ref_tahmin_m"], p["tahmin_eksi_gt_m"]
print()
print("n = %d ucus" % len(p))
print("korelasyon (ref_tahmin, tahmin-gt): %.3f" % x.corr(y))
print("egim: %.3f" % np.polyfit(x, y, 1)[0])
p.to_csv("reports/protocol_summary.csv", index=False)
