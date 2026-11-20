from pyulog import ULog
import numpy as np, sys
for LOG in sys.argv[1:]:
    u = ULog(LOG)
    print("==", LOG)
    print("groundtruth topic'leri:", [(d.name, d.multi_id, len(d.data["timestamp"])) for d in u.data_list if "groundtruth" in d.name and "local_position" in d.name])
    d = u.get_dataset("vehicle_local_position_groundtruth")
    t, z = d.data["timestamp"], -d.data["z"]
    dt = np.diff(t.astype(np.int64))
    print("ornek sayisi:", len(t), "| zaman artan mi:", bool(np.all(dt > 0)), "| geri giden adim sayisi:", int(np.sum(dt <= 0)))
    print("irtifa min/max: %.3f / %.3f" % (z.min(), z.max()))
    print(">5 m ornek sayisi:", int(np.sum(z > 5)), "| |irtifa|<0.5 ornek sayisi:", int(np.sum(np.abs(z) < 0.5)))
