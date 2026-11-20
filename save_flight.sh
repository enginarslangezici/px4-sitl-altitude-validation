#!/bin/bash
NAME="$1"
if [ -z "$NAME" ]; then echo "Kullanim: bash save_flight.sh vtol_explore_01"; exit 1; fi
if pgrep -x px4 > /dev/null; then echo "DURDUM: PX4 hala calisiyor, once pxh> satirinda shutdown yaz"; exit 1; fi
DEST="$HOME/px4-vtol-validation/logs/$NAME.ulg"
LATEST=$(ls -t $HOME/PX4-Autopilot/build/px4_sitl_default/rootfs/fs/log/*/*.ulg | head -1)
if [ -e "$DEST" ]; then echo "DURDUM: $DEST zaten var"; exit 1; fi
for f in $HOME/px4-vtol-validation/logs/*.ulg; do
  if cmp -s "$LATEST" "$f"; then echo "DURDUM: bu log zaten kayitli: $f (yeni ucus yapmadin mi?)"; exit 1; fi
done
cp "$LATEST" "$DEST"
cd $HOME/px4-vtol-validation
.venv/bin/python3 analysis/summarize.py
git add .
git commit -m "Ucus kaydi: $NAME"
echo "TAMAM: $NAME kaydedildi"
