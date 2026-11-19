"""urfagap.com RSS -> X ve Instagram otomatik paylaşım.

Kurallar:
- Metin sitedeki haberin başlığı/özetidir; değiştirilmez, uydurma içerik eklenmez.
- Yalnızca urfagap.com bağlantıları ve site görsel sunucusundaki görseller kullanılır.
- Her haber her platforma en fazla bir kez gider (durum: docs/paylasilan.json).
- İlk çalıştırmada mevcut haberler paylaşılmaz, yalnızca "görüldü" işaretlenir.
- Varsayılan KURU ÇALIŞTIRMADIR: PAYLAS_GERCEK=1 olmadıkça hiçbir şey gönderilmez.
- Anahtarı olmayan platform atlanır.
"""
import json, os, sys, time, datetime, email.utils, re
import xml.etree.ElementTree as ET
import requests

RSS = "https://www.urfagap.com/rss"
DURUM = sys.argv[1] if len(sys.argv) > 1 else "docs/paylasilan.json"
GERCEK = os.environ.get("PAYLAS_GERCEK") == "1"
MAX_ADET = int(os.environ.get("PAYLAS_MAX_ADET", "3"))        # bir çalışmada en fazla haber
MAX_YAS_SA = float(os.environ.get("PAYLAS_MAX_YAS_SAAT", "12"))  # bundan eski haber paylaşılmaz
MAX_DENEME = 3                                                  # platform başına en fazla deneme
IZIN_LINK = "https://www.urfagap.com/"
IZIN_GORSEL = "https://urfagapcom.teimg.com/"
PLATFORMLAR = ("x", "instagram")
KATEGORI_ETIKET = {  # kategoriye göre ek etiket (yoksa yalnızca genel etiketler)
    "GÜNDEM": "#Gündem", "EKONOMİ": "#Ekonomi", "SPOR": "#Spor", "ASAYİŞ": "#Asayiş",
    "TARIM": "#Tarım", "SAĞLIK": "#Sağlık", "EĞİTİM": "#Eğitim", "KÜLTÜR SANAT": "#Kültür",
}
S = requests.Session()
S.headers["User-Agent"] = "urfagap-haber-paylas/1.0"


def haberleri_oku():
    r = S.get(RSS, timeout=30)
    r.raise_for_status()
    kok = ET.fromstring(r.content)
    out = []
    for it in kok.iter("item"):
        g = lambda t: (it.findtext(t) or "").strip()
        link = g("link")
        if not link.startswith(IZIN_LINK):
            continue
        enc = it.find("enclosure")
        gorsel = enc.get("url") if enc is not None else ""
        if not gorsel.startswith(IZIN_GORSEL):
            gorsel = ""
        try:
            zaman = email.utils.parsedate_to_datetime(g("pubDate"))
        except Exception:
            continue  # tarihi okunamayan haber paylaşılmaz
        out.append({"baslik": g("title"), "ozet": g("description"), "link": link,
                    "kategori": g("category"), "gorsel": gorsel, "zaman": zaman})
    return out


def etiketler(h):
    e = ["#Şanlıurfa", "#Urfa"]
    k = KATEGORI_ETIKET.get(h["kategori"].upper())
    if k:
        e.append(k)
    return e


def x_metni(h):
    """X: link 23 karakter sayılır. Başlık + etiketler + link, en çok 280."""
    etiket = " ".join(etiketler(h)[:3])
    ayrac = f"\n\n{etiket}\n{h['link']}"
    kalan = 280 - 23 - len(f"\n\n{etiket}\n")
    b = h["baslik"]
    if len(b) > kalan:
        b = b[:kalan - 1].rstrip() + "…"
    return b + ayrac


def ig_metni(h):
    """Instagram'da link tıklanmaz; siteye yönlendirme metni eklenir. En çok 2200."""
    parca = [h["baslik"], "", h["ozet"], "", "Haberin devamı: urfagap.com (profildeki bağlantı)", "",
             " ".join(etiketler(h) + ["#UrfaGAP", "#Haber"])]
    return "\n".join(parca)[:2200]


def x_gonder(h):
    from requests_oauthlib import OAuth1
    a = OAuth1(os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
               os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_SECRET"])
    r = S.post("https://api.x.com/2/tweets", json={"text": x_metni(h)}, auth=a, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"X {r.status_code}: {r.text[:300]}")
    return r.json()["data"]["id"]


def ig_gonder(h):
    if not h["gorsel"]:
        raise RuntimeError("Instagram için görsel yok")
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]
    base = f"https://graph.facebook.com/v21.0/{uid}"
    r = S.post(f"{base}/media", data={"image_url": h["gorsel"], "caption": ig_metni(h),
                                       "access_token": tok}, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"IG medya {r.status_code}: {r.text[:300]}")
    cid = r.json()["id"]
    for _ in range(12):  # kapsayıcının hazır olmasını bekle (en çok ~60 sn)
        d = S.get(f"https://graph.facebook.com/v21.0/{cid}",
                  params={"fields": "status_code", "access_token": tok}, timeout=30).json()
        if d.get("status_code") == "FINISHED":
            break
        if d.get("status_code") == "ERROR":
            raise RuntimeError(f"IG kapsayıcı hatası: {d}")
        time.sleep(5)
    else:
        raise RuntimeError("IG kapsayıcı zamanında hazır olmadı")
    r = S.post(f"{base}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"IG yayın {r.status_code}: {r.text[:300]}")
    return r.json()["id"]


GONDER = {"x": (x_gonder, ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")),
          "instagram": (ig_gonder, ("IG_USER_ID", "IG_ACCESS_TOKEN"))}


def main():
    haberler = haberleri_oku()
    if not haberler:
        print("RSS'te haber yok; durum korunuyor."); return 1
    ilk_kurulum = not os.path.exists(DURUM)
    durum = {"gonderilen": {}} if ilk_kurulum else json.load(open(DURUM, encoding="utf-8"))
    kayit = durum["gonderilen"]
    simdi = datetime.datetime.now(datetime.timezone.utc)

    if ilk_kurulum:
        for h in haberler:
            kayit[h["link"]] = {"ilk_kurulum": True}
        print(f"İlk kurulum: {len(haberler)} mevcut haber 'görüldü' işaretlendi, paylaşım yapılmadı.")
    else:
        bekleyen = []
        for h in sorted(haberler, key=lambda x: x["zaman"]):  # eskiden yeniye
            yas = (simdi - h["zaman"]).total_seconds() / 3600
            k = kayit.get(h["link"], {})
            if k.get("ilk_kurulum") or yas > MAX_YAS_SA:
                continue
            if any(p not in k and k.get(p + "_deneme", 0) < MAX_DENEME for p in PLATFORMLAR):
                bekleyen.append(h)
        if len(bekleyen) > MAX_ADET:
            print(f"{len(bekleyen)} haber bekliyor; bu turda en yeni {MAX_ADET} tanesi paylaşılır.")
            bekleyen = bekleyen[-MAX_ADET:]
        for h in bekleyen:
            k = kayit.setdefault(h["link"], {})
            for p in PLATFORMLAR:
                fn, anahtarlar = GONDER[p]
                if p in k or k.get(p + "_deneme", 0) >= MAX_DENEME:
                    continue
                if not all(os.environ.get(a) for a in anahtarlar):
                    print(f"[{p}] anahtar yok, atlandı."); continue
                if not GERCEK:
                    print(f"[KURU][{p}] {h['link']}\n" + (x_metni(h) if p == "x" else ig_metni(h)) + "\n---")
                    continue
                try:
                    k[p] = fn(h)
                    print(f"[{p}] gönderildi: {h['baslik']}")
                except Exception as e:
                    k[p + "_deneme"] = k.get(p + "_deneme", 0) + 1
                    print(f"[{p}] HATA ({k[p + '_deneme']}/{MAX_DENEME}): {e}")
            k["zaman"] = h["zaman"].isoformat()

    # durum dosyası şişmesin: en yeni 300 kayıt
    if len(kayit) > 300:
        for l in list(kayit)[:len(kayit) - 300]:
            del kayit[l]
    if GERCEK or ilk_kurulum:
        os.makedirs(os.path.dirname(DURUM) or ".", exist_ok=True)
        json.dump(durum, open(DURUM, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
