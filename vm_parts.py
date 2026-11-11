"""URFA GAP Veri Merkezi: veri.json'dan sayfa parçalarını (HTML) üretir.
Hem sitedeki sabit sayfa derlemesi hem de botun docs/parcalar.json çıktısı bu modülü kullanır.
Eksik kaynak/ürün olursa ilgili parça atlanır; hiçbir rakam uydurulmaz."""
import html, datetime
E = html.escape
AY = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
def trt(iso):
    d = datetime.date.fromisoformat(iso); return f"{d.day} {AY[d.month-1]} {d.year}"
def tl(x): return f"{x:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def pct(x): return f"%{x:,.1f}".replace(",","X").replace(".",",").replace("X",".")
def get(rows, n): return next((s for s in rows if s["urun"] == n), None)
def rng(lo, hi, av):
    p = 50 if hi <= lo else (av-lo)/(hi-lo)*100
    return f'<span class="vm-rng"><i></i><b style="left:{p:.0f}%"></b></span>'
def kat(n):
    n = n.lower()
    if "pamuk" in n or "çiğit" in n or "çigit" in n: return ("pamuk","Pamuk ve çiğit")
    if "buğday" in n or n in ("mısır","arpa"): return ("hububat","Hububat")
    if "fıstık" in n: return ("fistik","Fıstık")
    if "mercimek" in n: return ("bakliyat","Bakliyat")
    if "ayçiçeği" in n or "soya" in n: return ("yag","Yağlı tohumlar")
    return ("diger","Diğer")
def kartlar(satirlar):
    gr = {}
    for s in satirlar: gr.setdefault(kat(s["urun"]), []).append(s)
    o = []
    for (k, ad), rows in gr.items():
        c = "".join(f'<article class="vm-card"><h4>{E(s["urun"])}</h4><div class="vm-avg">{tl(s["ortalama"])}<small>₺/kg</small></div>{rng(s["en_dusuk"],s["en_yuksek"],s["ortalama"])}<div class="vm-mm"><span>{tl(s["en_dusuk"])}</span><span>{tl(s["en_yuksek"])}</span></div></article>' for s in rows)
        o.append(f'<div class="vm-grp vm-k-{k}"><h3><i></i>{ad}</h3><div class="vm-cards">{c}</div></div>')
    return "".join(o)
def tablo(satirlar, tid):
    r = "".join(f'<tr data-urun="{E(s["urun"])}"><th scope="row">{E(s["urun"])}</th><td class="n">{tl(s["en_dusuk"])}</td><td class="n a">{tl(s["ortalama"])}</td><td class="n">{tl(s["en_yuksek"])}</td></tr>' for s in satirlar)
    return f'<details class="vm-tabledet"><summary>Tablo olarak göster</summary><div class="vm-scroll"><table class="ug-vm-tbl" id="{tid}"><caption class="ug-vm-sr">Ürün fiyatları, TL/kg</caption><thead><tr><th scope="col">Ürün</th><th scope="col" class="n">En düşük</th><th scope="col" class="n">Ortalama</th><th scope="col" class="n">En yüksek</th></tr></thead><tbody>{r}</tbody></table></div></details>'
def kpi(s, t, e): return f'<div class="vm-kpi"><span class="vm-kl">{E(e)}</span><b>{tl(s["ortalama"])}<small>₺/kg</small></b>{rng(s["en_dusuk"],s["en_yuksek"],s["ortalama"])}<span class="vm-km">{tl(s["en_dusuk"])} – {tl(s["en_yuksek"])} · {trt(t)}</span></div>'
def chg(e, y, ad, note):
    c = (y-e)/e*100; cls = "up" if c >= 0 else "dn"
    return f'<div class="vm-chg {cls}"><span>{ad}</span><b>{"▲" if c >= 0 else "▼"} {pct(abs(c))}</b><small>{tl(e)} → {tl(y)} ₺/kg{note}</small></div>'
def nt(label, txt): return f'<aside class="vm-calcnote"><span class="vm-cn-l">URFA GAP · {label}</span><p>{txt}</p></aside>'

# Simülatör ürünleri: (id, ad, kaynak, ürün adı, verim, destek, [diğer maliyetler], DSİ sulama, derin kuyu)
SIMP = [("pamuk","Kütlü Pamuk","ik","Kütlü Pamuk",520,1850,[2250,3100,2150,2450],1250,6900),
        ("mercimek","Kırmızı Kabuklu Mercimek","br","Kırmızı Kabuklu Mercimek",185,1100,[1320,1650,1280,1150],400,1350),
        ("bugday","Buğday","ik","Buğday",480,1450,[1680,2350,1420,1180],780,2950),
        ("misir","Mısır","ik","Mısır",1150,1250,[2100,3450,2200,1950],1450,7400),
        ("fistik","Boz Kavlak Fıstık","br","Fıstık Boz Kavlak",140,1500,[2850,4100,4950,11200],1100,3600)]

def parcalar(d):
    ik, br, rg = d.get("borsa_ikincil"), d.get("borsa"), d.get("resmi_gazete")
    ikr = ik["satirlar"] if ik and ik.get("satirlar") else []
    brr = br["satirlar"] if br and br.get("satirlar") else []
    t_ik = ikr[0]["tarih"] if ikr else None
    t_br = br.get("son_bulten_tarihi") if brr else None
    P = {"meta": {"ik": t_ik, "br": t_br, "rg": (rg or {}).get("sayi"), "uretildi": d.get("olusturuldu")}}
    # KPI
    kp = []
    for r, t, e in [(get(ikr,"Kütlü Pamuk"),t_ik,"Kütlü pamuk"),(get(ikr,"Preseli Pamuk St.1 Beyaz"),t_ik,"Preseli pamuk"),(get(ikr,"Buğday"),t_ik,"Buğday"),(get(ikr,"Mısır"),t_ik,"Mısır"),(get(brr,"Fıstık Boz Kavlak"),t_br,"Boz kavlak fıstık")]:
        if r: kp.append(kpi(r, t, e))
    if kp: P["kpis"] = "".join(kp)
    # şerit
    tk = [(s["urun"], s["ortalama"], t_ik) for s in ikr[:8]] + [(s["urun"], s["ortalama"], t_br) for s in brr if s["urun"] in ("Fıstık Boz Kavlak","Kırmızı Kabuklu Mercimek","Arpa")]
    if tk:
        tki = "".join(f'<span class="vm-ti"><em>{E(n)}</em><b>{tl(v)} ₺</b><small>{trt(t)}</small></span>' for n, v, t in tk)
        P["ticker"] = f'<div class="vm-ticker" aria-label="Borsa fiyat şeridi"><span class="vm-live"><i></i>BORSA</span><div class="vm-tk"><div class="vm-tkin">{tki}{tki}</div></div></div>'
    if t_ik: P["asof_ik"] = f"{trt(t_ik)} itibarıyla"
    if t_br: P["asof_br"] = f"{trt(t_br)} itibarıyla"
    if ikr: P["borsa_ik"] = kartlar(ikr) + tablo(ikr, "vm-tbl-ik")
    if brr: P["borsa_br"] = kartlar(brr) + tablo(brr, "vm-tbl-br")
    # analiz
    alln = [(s["urun"], s, t_ik) for s in ikr if s["ortalama"] > 0 and s["en_yuksek"] > s["en_dusuk"]] + [(s["urun"], s, t_br) for s in brr if s["ortalama"] > 0 and s["en_yuksek"] > s["en_dusuk"]]
    an = []
    if alln:
        yay = sorted([(n, (s["en_yuksek"]-s["en_dusuk"])/s["ortalama"]*100, t) for n, s, t in alln], key=lambda x: -x[1])[:8]
        mx = max(v for _, v, _ in yay) or 1
        yay_h = "".join(f'<li><span class="vm-bl">{E(n)}<small>{trt(t)}</small></span><span class="vm-bar"><i style="width:{v/mx*100:.0f}%"></i></span><b>{pct(v)}</b></li>' for n, v, t in yay)
        an.append(f'<div class="vm-anc"><h3>Fiyat dalgalanma aralığı</h3><p>(en yüksek − en düşük) ÷ ortalama. Aralık genişse ürünün kalitesine göre fiyat farkı büyüktür.</p><ul class="vm-bars">{yay_h}</ul></div>')
    hub = [(n, get(ikr, u)["ortalama"]) for n, u in [("Buğday","Buğday"),("Mısır","Mısır"),("Kütlü pamuk","Kütlü Pamuk"),("Ayçiçeği","Ayçiçeği"),("Arpa","Arpa")] if get(ikr, u)][:4]
    if len(hub) >= 2:
        hm = max(v for _, v in hub)
        hub_h = "".join(f'<li><span class="vm-bl">{n}</span><span class="vm-bar"><i style="width:{v/hm*100:.0f}%"></i></span><b>{tl(v)} ₺</b></li>' for n, v in hub)
        an.append(f'<div class="vm-anc"><h3>Ürünlerin ortalama fiyatı</h3><p>{trt(t_ik)} seansı, TL/kg.</p><ul class="vm-bars vm-bars2">{hub_h}</ul></div>')
    kut, pre = get(ikr, "Kütlü Pamuk"), get(ikr, "Preseli Pamuk St.1 Beyaz")
    if kut and pre:
        an.append(f'<div class="vm-anc vm-ratio"><h3>Preseli / kütlü pamuk oranı</h3><div class="vm-big">{pre["ortalama"]/kut["ortalama"]:.2f}<small>kat</small></div><p>Preseli pamuk {tl(pre["ortalama"])} ₺, kütlü pamuk {tl(kut["ortalama"])} ₺. Farklı işlem aşamaları olduğu için doğrudan kıyaslanamaz; çırçır ve işleme katma değerini gösterir.</p></div>')
    ch = []
    for ad, e, y, note in [("Mısır", get(brr,"Mısır"), get(ikr,"Mısır"), ""), ("Buğday", get(brr,"Ekmeklik Buğday"), get(ikr,"Buğday"), " · sınıf farkı olabilir")]:
        if e and y and e["ortalama"] > 0 and t_br != t_ik: ch.append(chg(e["ortalama"], y["ortalama"], ad, note))
    if ch:
        an.append(f'<div class="vm-anc"><h3>ŞUTB bülteninden bu yana değişim</h3><p>ŞUTB resmî bülteni ({trt(t_br)}) ile son seans ({trt(t_ik)}) arasında.</p><div class="vm-chgs">{"".join(ch)}</div></div>')
    if an: P["analiz"] = "".join(an)
    # notlar
    if t_ik and t_br:
        P["nb"] = nt("Veri notu", f"Bu fiyatlar kaynaklarından olduğu gibi aktarılır; URFA GAP Veri Merkezi rakamlara müdahale etmez. Son seans: {trt(t_ik)} (borsa bülteni), {trt(t_br)} (ŞUTB resmî bülteni).")
    if t_ik:
        P["na"] = nt("Hesaplama notu", f"Dalgalanma aralığı = (en yüksek − en düşük) ÷ ortalama; oran = Preseli ÷ kütlü pamuk ortalaması. Tüm grafikler URFA GAP Veri Merkezi tarafından {trt(t_ik)} seansı verilerinden otomatik hesaplanır, ek varsayım içermez.")
        P["ns"] = nt("Hesaplama notu", f"Net kâr = (verim × satış fiyatı − dönüm başı maliyet) × alan. Satış fiyatı {trt(t_ik)} itibarıyla borsa verisidir; verim ve maliyet kalemleri URFA GAP model varsayımıdır ve düzenlenebilir. Sonuç tahmindir, garanti değildir.")
    # simülatör fiyatları
    sim = []
    for i, a, kay, u, v, ds, dg, dsi, ku in SIMP:
        r = get(ikr if kay == "ik" else brr, u); t = t_ik if kay == "ik" else t_br
        if r and t: sim.append({"id": i, "fiyat": r["ortalama"], "tarih": f"{trt(t)} itibarıyla"})
    if sim: P["sim"] = sim
    return P
