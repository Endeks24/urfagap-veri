"""docs/veri.json -> docs/parcalar.json: sitedeki URFA GAP Veri Merkezi sayfasının canlı güncellenen HTML parçaları."""
import json, sys
from vm_parts import parcalar
VERI = sys.argv[1] if len(sys.argv) > 1 else "docs/veri.json"
CIKTI = sys.argv[2] if len(sys.argv) > 2 else "docs/parcalar.json"
d = json.load(open(VERI, encoding="utf-8"))
P = parcalar(d)
json.dump(P, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False)
print("Parçalar:", [k for k in P if k != "meta"], "| meta:", P["meta"])
