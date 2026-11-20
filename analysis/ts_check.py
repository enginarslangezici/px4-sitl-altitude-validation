from pyulog import ULog
import glob
print("%-24s %s" % ("log", "gt_ilk - tahmin_ilk (s)"))
for p in sorted(glob.glob("logs/*.ulg")):
    u = ULog(p)
    e = int(u.get_dataset("vehicle_local_position").data["timestamp"][0])
    g = int(u.get_dataset("vehicle_local_position_groundtruth").data["timestamp"][0])
    print("%-24s %+.3f" % (p.split("/")[-1], (g - e) / 1e6))
