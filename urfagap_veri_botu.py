#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URFAGAP Veri Merkezi - veri botu (yapay zekâ YOK, yalnızca kural tabanlı ayrıştırma)

Ne yapar:
  1) Şanlıurfa Ticaret Borsası ana sayfasındaki güncel ürün fiyatlarını (en düşük/en yüksek/ortalama + bülten tarihi) okur.
  2) Resmî Gazete'nin güncel sayısındaki başlıkları okur; Şanlıurfa/GAP havzası anahtar kelimeleriyle eşleşenleri işaretler.
  3) Her kaydı doğrular (sayı aralığı, tarih biçimi, ortalama min-max arasında mı) ve bayatlığı hesaplar.
  4) Sonucu veri.json olarak yazar. Hatalı/boş veri gelirse ESKİ dosyayı BOZMAZ (çıkış kodu != 0).

Çalıştırma:  python3 urfagap_veri_botu.py veri.json
Zamanlama:   cron örneği (her gün 18:30)  ->  30 18 * * *  python3 /yol/urfagap_veri_botu.py /yol/veri.json
Bağımlılık:  requests  (pip install requests)
"""
import sys, re, json, html, datetime, os, tempfile
import requests

UA = {"User-Agent": "UrfaGAP-VeriBotu/1.0 (+https://www.urfagap.com; iletisim@urfagap.com)"}
SUTB_URL = "https://www.sutb.org.tr"
RG_URL = "https://www.resmigazete.gov.tr/"
BOLGE = re.compile(r"(şanlıurfa|urfa|gaziantep|mardin|diyarbakır|adıyaman|batman|siirt|kilis|\bgap\b|fırat|dicle|atatürk baraj|harran|ceylanpınar|viranşehir|siverek|birecik|halfeti|bozova|suruç|akçakale)", re.I)
BUGUN = datetime.date.today()

def al(url, deneme=2):
    """Geçici ağ hatalarına karşı yeniden dener."""
    son = None
    for i in range(deneme):
        try:
            r = requests.get(url, headers=UA, timeout=(10, 40)); r.raise_for_status(); return r
        except requests.RequestException as e:
            son = e
    raise son

def temiz_metin(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))

def sayi(s):
    return float(s.replace(".", "").replace(",", "."))

def sutb_oku():
    r = al(SUTB_URL)
    t = temiz_metin(r.text)
    kalip = re.compile(r"(\d{2}\.\d{2}\.\d{4})\s*:\s*([^:]+?)\s*:\s*En Düşük:\s*([\d\.,]+)\s*En Yüksek:\s*([\d\.,]+)\s*Ortalama:\s*([\d\.,]+)")
    satirlar, gorulen = [], set()
    for tarih, urun, lo, hi, av in kalip.findall(t):
        urun = urun.strip()
        try:
            lo, hi, av = sayi(lo), sayi(hi), sayi(av)
            gun = datetime.datetime.strptime(tarih, "%d.%m.%Y").date()
        except ValueError:
            continue
        # doğrulama: pozitif, ortalama aralıkta, makul üst sınır
        if not (0 < lo <= av <= hi <= 5000) or (tarih, urun) in gorulen:
            continue
        gorulen.add((tarih, urun))
        satirlar.append({"urun": urun, "en_dusuk": lo, "ortalama": av, "en_yuksek": hi, "tarih": gun.isoformat(),
                         "gun_once": (BUGUN - gun).days})
    if len(satirlar) < 5:
        raise RuntimeError("ŞUTB: beklenenden az satır ayrıştırıldı (%d); sayfa yapısı değişmiş olabilir" % len(satirlar))
    return satirlar


TF_URL = "https://www.tarimfiyatlari.com.tr/borsa/sanliurfa"
KATEGORI = r"(?:Hububat|Pamuk|Yağlı tohumlar|Diğer|Baklagil|Sebze|Meyve|Bakliyat)"

def tarimfiyatlari_oku():
    """İKİNCİL kaynak: Şanlıurfa borsası son seans tablosu (ŞUTB bülteninden derlenmiş). Birincil veriyle SESSİZCE birleştirilmez."""
    r = al(TF_URL)
    t = temiz_metin(r.text)
    gun = re.search(r"(\d{1,2})\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+(20\d\d)\s+seansı", t)
    if not gun:
        raise RuntimeError("tarimfiyatlari: seans tarihi bulunamadı")
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    tarih = datetime.date(int(gun.group(3)), aylar.index(gun.group(2)) + 1, int(gun.group(1)))
    bolum = t[t.find("Ürün / çeşit"):t.find("Tabloyu yana")]
    kalip = re.compile(r"([A-ZÇĞİÖŞÜa-zçğıöşü\.\d ]+?)\s+" + KATEGORI + r"\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+TL/kg")
    satirlar = []
    for ad, lo, hi, av in kalip.findall(bolum):
        try:
            lo, hi, av = sayi(lo), sayi(hi), sayi(av)
        except ValueError:
            continue
        if 0 < lo <= av <= hi <= 5000:
            ad = re.split(r"(?:\bton|kg-adet|45 gün)\s+", ad)[-1].strip()  # önceki satırdan kalan artığı at
            satirlar.append({"urun": ad, "en_dusuk": lo, "ortalama": av, "en_yuksek": hi,
                             "tarih": tarih.isoformat(), "gun_once": (BUGUN - tarih).days})
    if len(satirlar) < 3:
        raise RuntimeError("tarimfiyatlari: beklenenden az satır")
    return satirlar

def resmi_gazete_oku():
    r = al(RG_URL)
    t = temiz_metin(r.text)
    m = re.search(r"(\d{1,2}\s+\w+\s+20\d\d)\s+Tarihli\s+ve\s+(\d+)\s+Sayılı", t)
    basliklar = []
    for href, b in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]{12,400}?)\s*</a>', r.text):
        b = re.sub(r"^[–—\-\s]+", "", html.unescape(b)).strip()
        if b and not b.lower().startswith(("arşiv", "tarih seçimi", "arama")):
            basliklar.append({"baslik": b, "baglanti": requests.compat.urljoin(RG_URL, href), "bolge_eslesmesi": bool(BOLGE.search(b))})
    if not m or not basliklar:
        raise RuntimeError("Resmî Gazete: sayı/başlık ayrıştırılamadı")
    return {"tarih_metni": m.group(1), "sayi": int(m.group(2)), "toplam_baslik": len(basliklar),
            "bolge_eslesmeleri": [x for x in basliklar if x["bolge_eslesmesi"]], "baslıklar": basliklar[:40]}

def main(cikti):
    """Her kaynak BAĞIMSIZ okunur; biri arızalansa diğerleri yazılır, arıza 'hatalar' altında açıkça belirtilir.
    Hiçbir kaynakta SABİT/ESKİ rakam uydurulmaz: veri alınamadıysa o bölüm yoktur."""
    veri, hatalar = {"olusturuldu": datetime.datetime.now().isoformat(timespec="seconds")}, {}
    kaynaklar = [("borsa", lambda: {"kaynak": "Şanlıurfa Ticaret Borsası (resmi site)", "kaynak_url": SUTB_URL, "satirlar": sutb_oku()}),
                 ("borsa_ikincil", lambda: {"kaynak": "tarimfiyatlari.com.tr (borsa bülteninden derlenmiş, ikincil)", "kaynak_url": TF_URL, "satirlar": tarimfiyatlari_oku()}),
                 ("resmi_gazete", lambda: dict(kaynak="Resmî Gazete", kaynak_url=RG_URL, **resmi_gazete_oku()))]
    for ad, fn in kaynaklar:
        try:
            veri[ad] = fn()
        except Exception as e:
            hatalar[ad] = str(e)[:200]
    if "borsa" in veri:
        en_yeni = max(s["tarih"] for s in veri["borsa"]["satirlar"])
        veri["borsa"]["son_bulten_tarihi"] = en_yeni
        veri["borsa"]["bayat_gun"] = (BUGUN - datetime.date.fromisoformat(en_yeni)).days
    veri["hatalar"] = hatalar
    if not any(k in veri for k in ("borsa", "borsa_ikincil", "resmi_gazete")):
        raise RuntimeError("hiçbir kaynak okunamadı: %s" % hatalar)
    fd, gecici = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(cikti)) or ".", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    os.replace(gecici, cikti)  # atomik yaz
    print("TAMAM:", cikti, "| okunan:", [k for k in ("borsa","borsa_ikincil","resmi_gazete") if k in veri], "| arıza:", hatalar or "yok")

if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "veri.json")
    except Exception as e:
        print("HATA (eski veri korunuyor):", e, file=sys.stderr); sys.exit(1)
