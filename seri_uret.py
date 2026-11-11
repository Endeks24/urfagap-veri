"""docs/gecmis/*.json arşivinden fiyat geçmişi serisi (docs/seri.json) üretir.
Her (ürün, veri tarihi) çifti bir kez yazılır; böylece bülten değişmediği günlerde nokta tekrarlanmaz."""
import glob, json, os, sys
GECMIS = sys.argv[1] if len(sys.argv) > 1 else "docs/gecmis"
CIKTI = sys.argv[2] if len(sys.argv) > 2 else "docs/seri.json"
GORUNEN = {  # grafikte gösterilecek ürünler (kaynak anahtarı, ürün adı)
    "borsa_ikincil": ["Kütlü Pamuk", "Preseli Pamuk St.1 Beyaz", "Buğday", "Mısır", "Ayçiçeği"],
    "borsa": ["Fıstık Boz Kavlak", "Kırmızı Kabuklu Mercimek"],
}
seri = {}
for yol in sorted(glob.glob(os.path.join(GECMIS, "*.json"))):
    try:
        d = json.load(open(yol, encoding="utf-8"))
    except Exception:
        continue
    for kaynak, adlar in GORUNEN.items():
        for s in (d.get(kaynak) or {}).get("satirlar", []):
            if s.get("urun") in adlar and s.get("tarih") and s.get("ortalama") is not None:
                seri.setdefault(s["urun"], {})[s["tarih"]] = s["ortalama"]
cikti = {"guncellendi": max((t for v in seri.values() for t in v), default=None),
         "kaynak": "Şanlıurfa Ticaret Borsası (URFA GAP Veri Merkezi arşivi)",
         "seri": {u: sorted([[t, v] for t, v in noktalar.items()]) for u, noktalar in seri.items()}}
json.dump(cikti, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("Seri:", {u: len(v) for u, v in cikti["seri"].items()})
