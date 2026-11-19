"""urfagap.com RSS -> docs/paylas/haberler.json

"URFA GAP Paylaş" sayfası (docs/paylas/index.html) bu dosyayı okur. RSS tarayıcıdan doğrudan okunamaz (CORS yok),
bu yüzden haberler Actions ile burada hazırlanır. Harici API, anahtar ya da şifre yoktur.
- Metin sitedeki başlık/özettir; uydurma içerik eklenmez. Yalnızca kategoriye göre etiket eklenir.
- Yalnızca urfagap.com bağlantıları ve site görsel sunucusundaki görseller alınır.
- RSS okunamazsa ya da boşsa eski dosya korunur (betik hata koduyla çıkar).
"""
import datetime, email.utils, hashlib, json, re, sys, html
import xml.etree.ElementTree as ET
from urllib.parse import quote
import requests

RSS = "https://www.urfagap.com/rss"
CIKTI = sys.argv[1] if len(sys.argv) > 1 else "docs/paylas/haberler.json"
ADET = 40
IZIN_LINK = "https://www.urfagap.com/"
IZIN_GORSEL = "https://urfagapcom.teimg.com/"
ETIKET = {  # kategori (büyük harf) -> etiket
    "GÜNDEM": "#Gündem", "SİYASET": "#Siyaset", "EĞİTİM": "#Eğitim", "YAŞAM": "#Yaşam", "DÜNYA": "#Dünya",
    "MEDYA": "#Medya", "SPOR": "#Spor", "ASAYİŞ": "#Asayiş", "EKONOMİ": "#Ekonomi", "TARIM": "#Tarım",
    "SAĞLIK": "#Sağlık", "KÜLTÜR SANAT": "#Kültür",
}


def buyuk(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def ilk_buyuk(s):
    """'EĞİTİM' -> 'Eğitim' (Türkçe i/ı kurallarıyla; str.title() Türkçede bozuk çıktı verir)."""
    k = lambda x: x.replace("İ", "i").replace("I", "ı").lower()
    b = lambda c: "İ" if c == "i" else "I" if c == "ı" else c.upper()
    return " ".join((b(k(w)[0]) + k(w)[1:]) if w else w for w in s.split())


def kirp(s, n):
    return s if len(s) <= n else re.sub(r"\s+\S*$", "", s[: n - 1]) + "…"


def duz(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def gorsel_adresi(u, boyut):
    """Görsel sunucusunda crop/GENxYUK yolunu değiştirir (örn. crop/1080x1350)."""
    return re.sub(r"/crop/\d+x\d+/", f"/crop/{boyut}/", u, count=1) if "/crop/" in u else u


def haberleri_oku():
    r = requests.get(RSS, timeout=30, headers={"User-Agent": "urfagap-paylas-hazirla/1.0"})
    r.raise_for_status()
    out = []
    for it in ET.fromstring(r.content).iter("item"):
        g = lambda t: (it.findtext(t) or "").strip()
        link = g("link")
        if not link.startswith(IZIN_LINK):
            continue
        try:
            zaman = email.utils.parsedate_to_datetime(g("pubDate"))
        except Exception:
            continue
        enc = it.find("enclosure")
        gorsel = enc.get("url") if enc is not None else ""
        if not gorsel.startswith(IZIN_GORSEL):
            gorsel = ""
        out.append({"baslik": duz(g("title")), "ozet": kirp(duz(g("description")), 200), "link": link,
                    "kat": g("category"), "gorsel": gorsel, "zaman": zaman})
    out.sort(key=lambda h: h["zaman"], reverse=True)
    return out[:ADET]


def hazirla(h):
    kat_etiket = ETIKET.get(buyuk(h["kat"]))
    etiketler = ["#Şanlıurfa", "#Urfa"] + ([kat_etiket] if kat_etiket else [])
    x_metin = kirp(h["baslik"], 200) + "\n\n" + " ".join(etiketler)
    caption = "\n\n".join(p for p in [h["baslik"], h["ozet"], "Haberin devamı: urfagap.com (profildeki bağlantı)",
                                      " ".join(etiketler + ["#UrfaGAP", "#Haber"])] if p)[:2200]
    return {
        "id": hashlib.sha1(h["link"].encode()).hexdigest()[:10],
        "baslik": h["baslik"], "url": h["link"], "kat": ilk_buyuk(h["kat"]) if h["kat"] != "News" else "",
        "zaman": h["zaman"].astimezone(datetime.timezone.utc).isoformat(),
        "kucuk": gorsel_adresi(h["gorsel"], "200x200") if h["gorsel"] else "",
        "ig_gorsel": gorsel_adresi(h["gorsel"], "1080x1350") if h["gorsel"] else "",
        "ig_yedek": h["gorsel"],
        "x": f"https://x.com/intent/post?text={quote(x_metin)}&url={quote(h['link'], safe='')}",
        "caption": caption,
    }


def main():
    haberler = haberleri_oku()
    if not haberler:
        print("RSS'te haber yok; eski dosya korunuyor."); return 1
    veri = {"guncellendi": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"),
            "haberler": [hazirla(h) for h in haberler]}
    # Yalnızca haber içeriği değiştiyse yaz (gereksiz commit olmasın)
    try:
        eski = json.load(open(CIKTI, encoding="utf-8"))
        if eski.get("haberler") == veri["haberler"]:
            print("Değişiklik yok."); return 0
    except Exception:
        pass
    import os
    os.makedirs(os.path.dirname(CIKTI) or ".", exist_ok=True)
    json.dump(veri, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(veri['haberler'])} haber yazıldı -> {CIKTI}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
