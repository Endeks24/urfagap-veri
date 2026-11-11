import json,html,datetime,sys,os
VERI=sys.argv[1] if len(sys.argv)>1 else "docs/veri.json"
OUT=sys.argv[2] if len(sys.argv)>2 else "docs/sosyal"
E=html.escape
AY=["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
def trt(iso):
    d=datetime.date.fromisoformat(iso);return f"{d.day} {AY[d.month-1]} {d.year}"
def tl(x): return f"{x:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def tr0(x): return f"{abs(round(x)):,}".replace(",",".")
d=json.load(open(VERI,encoding="utf-8"));ik,br=d["borsa_ikincil"],d["borsa"]
t_ik=ik["satirlar"][0]["tarih"];t_br=br["son_bulten_tarihi"]
get=lambda rows,n:next(s for s in rows if s["urun"]==n)
ICP={"pamuk":'<circle cx="8.5" cy="9.5" r="3.6"/><circle cx="15.5" cy="9.5" r="3.6"/><circle cx="12" cy="6.3" r="3.3"/><path d="M7.5 14.2 12 21l4.5-6.8M12 12v9"/>',
"preseli":'<rect x="3.5" y="7" width="17" height="11" rx="2.2"/><path d="M9 7v11M15 7v11M3.5 12.5h17"/><path d="M8 4.5h8"/>',
"bugday":'<path d="M12 21V8"/><path d="M12 8c-2.6 0-4-1.6-4-4 2.6 0 4 1.6 4 4zM12 8c2.6 0 4-1.6 4-4-2.6 0-4 1.6-4 4z"/><path d="M12 14c-2.6 0-4-1.6-4-4 2.6 0 4 1.6 4 4zM12 14c2.6 0 4-1.6 4-4-2.6 0-4 1.6-4 4z"/><path d="M12 20c-2.6 0-4-1.6-4-4 2.6 0 4 1.6 4 4zM12 20c2.6 0 4-1.6 4-4-2.6 0-4 1.6-4 4z"/>',
"misir":'<ellipse cx="12" cy="9.5" rx="3.6" ry="6.5"/><path d="M10 6h4M9.5 9.5h5M10 13h4M12 3v13"/><path d="M12 21c-4 0-6-3-6-6 3 0 5 1 6 3 1-2 3-3 6-3 0 3-2 6-6 6z"/>',
"aycicegi":'<circle cx="12" cy="12" r="3.2"/><path d="M12 3v3.2M12 17.8V21M3 12h3.2M17.8 12H21M5.6 5.6l2.3 2.3M16.1 16.1l2.3 2.3M18.4 5.6l-2.3 2.3M7.9 16.1l-2.3 2.3"/>',
"fistik":'<path d="M12 3c4.5 0 7 4 7 8.5S16 21 12 21 5 16 5 11.5 7.5 3 12 3z"/><path d="M12 3c-1.6 3-1.6 15 0 18"/><path d="M8 9c1.2.8 2.4 1.2 4 1.2M16 9c-1.2.8-2.4 1.2-4 1.2"/>',
"mercimek":'<ellipse cx="8" cy="9" rx="3.6" ry="2.6" transform="rotate(-25 8 9)"/><ellipse cx="16" cy="10" rx="3.6" ry="2.6" transform="rotate(20 16 10)"/><ellipse cx="11.5" cy="16" rx="3.6" ry="2.6" transform="rotate(-8 11.5 16)"/>'}
def ic(k): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICP[k]}</svg>'
P=[("pamuk","Kütlü pamuk","Kütlü Pamuk"),("preseli","Preseli pamuk","Preseli Pamuk St.1 Beyaz"),("bugday","Buğday","Buğday"),("misir","Mısır","Mısır"),("aycicegi","Ayçiçeği","Ayçiçeği")]
rows=[(k,n,get(ik["satirlar"],u)) for k,n,u in P]
CROPS=[("pamuk","Kütlü pamuk",get(ik["satirlar"],"Kütlü Pamuk")["ortalama"],520,[2250,3100,2150,2450],1250),
("mercimek","Kırmızı mercimek",get(br["satirlar"],"Kırmızı Kabuklu Mercimek")["ortalama"],185,[1320,1650,1280,1150],400),
("bugday","Buğday",get(ik["satirlar"],"Buğday")["ortalama"],480,[1680,2350,1420,1180],780),
("misir","Mısır",get(ik["satirlar"],"Mısır")["ortalama"],1150,[2100,3450,2200,1950],1450),
("fistik","Boz kavlak fıstık",get(br["satirlar"],"Fıstık Boz Kavlak")["ortalama"],140,[2850,4100,4950,11200],1100)]
rad=sorted([(k,n,v*f-(sum(dg)+ds)) for k,n,f,v,dg,ds in CROPS],key=lambda x:-x[2])
CSS='''*{box-sizing:border-box;margin:0}body{width:%(W)spx;height:%(H)spx;font-family:Inter,system-ui,sans-serif;color:#fff;overflow:hidden;background:#071426;position:relative}
.bg{position:absolute;inset:0;background:radial-gradient(70%% 50%% at 100%% 0%%,rgba(246,196,83,.28),transparent 62%%),radial-gradient(70%% 60%% at 0%% 100%%,rgba(46,144,250,.3),transparent 62%%),linear-gradient(150deg,#071426,#0b1f36 50%%,#10335a)}
.grid{position:absolute;inset:0;opacity:.5;background:repeating-linear-gradient(0deg,rgba(255,255,255,.04) 0 1px,transparent 1px 54px),repeating-linear-gradient(90deg,rgba(255,255,255,.04) 0 1px,transparent 1px 54px);-webkit-mask-image:linear-gradient(180deg,#000,transparent 80%%)}
.wrap{position:relative;height:100%%;padding:%(PT)spx 70px %(PB)spx;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center}
.brand{font-weight:900;font-size:33px;letter-spacing:.04em}.brand b{color:#f6c453}
.live{display:flex;align-items:center;gap:12px;font-weight:800;font-size:20px;letter-spacing:.16em;color:#f6c453}.live i{width:14px;height:14px;border-radius:50%%;background:#12b76a;box-shadow:0 0 0 8px rgba(18,183,106,.25)}
h1{margin-top:%(HT)spx;font-weight:900;font-size:%(HS)spx;line-height:1.04;letter-spacing:-.02em}
.chip{width:fit-content;align-self:flex-start;margin-top:20px;padding:12px 26px;border-radius:99px;background:rgba(255,255,255,.1);border:1.5px solid rgba(255,255,255,.22);font-weight:700;font-size:28px}
.list{margin-top:%(LT)spx;display:flex;flex-direction:column;gap:%(GAP)spx;flex:1}
.r{display:grid;grid-template-columns:84px 1fr auto;align-items:center;gap:0 24px;padding:%(RP)spx 28px;border-radius:26px;background:linear-gradient(160deg,rgba(255,255,255,.13),rgba(255,255,255,.04));border:1.5px solid rgba(255,255,255,.16)}
.ib{width:84px;height:84px;border-radius:24px;display:grid;place-items:center;background:linear-gradient(145deg,rgba(246,196,83,.26),rgba(246,196,83,.06));border:2px solid rgba(246,196,83,.5);color:#f6c453}.ib svg{width:48px;height:48px}
.nm{font-weight:800;font-size:34px}.rg{position:relative;height:9px;margin:14px 4px 10px;border-radius:9px;background:linear-gradient(90deg,rgba(18,183,106,.6),rgba(246,196,83,.6),rgba(240,68,56,.6))}.rg i{position:absolute;top:50%%;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%%;background:#fff;box-shadow:0 0 0 5px rgba(255,255,255,.28)}
.mm{font-weight:600;font-size:23px;color:rgba(255,255,255,.65)}
.pr{font-weight:900;font-size:58px;color:#f6c453;font-variant-numeric:tabular-nums;text-align:right;line-height:1}.pr small{display:block;margin-top:6px;font-size:22px;font-weight:700;color:rgba(255,255,255,.6)}
.bar{display:grid;grid-template-columns:96px 1fr;align-items:center;gap:0 26px}
.bt{height:26px;border-radius:13px;background:rgba(255,255,255,.1);overflow:hidden;margin-top:12px}.bt i{display:block;height:100%%;border-radius:13px;background:linear-gradient(90deg,#12b76a,#6ce9a6)}
.val{font-weight:900;font-size:50px;color:#6ce9a6;text-align:right}
.foot{margin-top:22px}.src{font-weight:600;font-size:21px;line-height:1.45;color:rgba(255,255,255,.7)}
.cta{margin-top:16px;display:flex;justify-content:space-between;align-items:center;padding:20px 30px;border-radius:20px;background:linear-gradient(90deg,#f6c453,#e8a317);color:#0b1f36;font-weight:900;font-size:28px}'''
def page(W,H,body,PT=56,PB=48,HT=30,HS=66,LT=26,GAP=14,RP=14): return "<!doctype html><meta charset=utf-8><style>"+CSS%dict(W=W,H=H,PT=PT,PB=PB,HT=HT,HS=HS,LT=LT,GAP=GAP,RP=RP)+"</style><body><div class=bg></div><div class=grid></div><div class=wrap>"+body+"</div>"
def top(label): return f'<div class=top><div class=brand>URFA <b>GAP</b> VERİ MERKEZİ</div><div class=live><i></i>{label}</div></div>'
def cta(src): return f'<div class=foot><div class=src>{src}</div><div class=cta><span>Tüm veriler ve simülatör</span><span>urfagap.com/gap-veri-merkezi</span></div></div>'
def borsa(W,H,rows=rows,tarih=t_ik,kaynak="Kaynak: Şanlıurfa Ticaret Borsası bülteni. Ortalama fiyat; çubuk en düşük–en yüksek aralığı gösterir.",baslik="Şanlıurfa<br>borsa fiyatları",**k):
    L=""
    for key,n,r in rows:
        lo,av,hi=r["en_dusuk"],r["ortalama"],r["en_yuksek"];p=50 if hi<=lo else max(4,min(96,(av-lo)/(hi-lo)*100))
        L+=f'<div class=r><div class=ib>{ic(key)}</div><div><div class=nm>{n}</div><div class=rg><i style="left:{p:.0f}%"></i></div><div class=mm>{tl(lo)} – {tl(hi)} ₺</div></div><div class=pr>{tl(av)}<small>₺/kg</small></div></div>'
    b=top("BORSA VERİSİ · ŞANLIURFA")+f'<h1>{baslik}</h1>'+f'<div class=chip>{trt(tarih)} itibarıyla</div><div class=list>{L}</div>'+cta(kaynak)
    return page(W,H,b,**k)
def radar(W,H,**k):
    mx=max(abs(x[2]) for x in rad);L=""
    for key,n,v in rad:
        w=max(3,abs(v)/mx*100)
        L+=f'<div class=r style="grid-template-columns:84px 1fr"><div class=ib>{ic(key)}</div><div><div style="display:flex;justify-content:space-between;align-items:baseline"><div class=nm>{n}</div><div class=val style="color:{"#6ce9a6" if v>=0 else "#fda29b"}">{"+" if v>=0 else "−"}{tr0(v)} ₺</div></div><div class=bt><i style="width:{w:.1f}%"></i></div></div></div>'
    b=top("SİMÜLASYON")+'<h1>Çiftçi kâr radarı<br>dönüm başına net</h1>'+f'<div class=chip>{trt(t_ik)} borsa fiyatlarıyla · DSİ sulama</div><div class=list>{L}</div>'+cta("Satış fiyatı borsa verisidir"+(f" (fıstık ve mercimek: ŞUTB {trt(t_br)} bülteni)" if t_br!=t_ik else "")+"; verim ve maliyetler URFA GAP model varsayımıdır. Tahmindir, garanti değildir.")
    return page(W,H,b,**k)
def wide():
    L="".join(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-bottom:1.5px solid rgba(255,255,255,.14)"><span style="display:flex;align-items:center;gap:16px;font-weight:800;font-size:30px"><span class=ib style="width:52px;height:52px;border-radius:15px"><span style="display:block;width:30px;height:30px">{ic(key)}</span></span>{n}</span><span style="font-weight:900;font-size:38px;color:#f6c453">{tl(r["ortalama"])} <small style="font-size:20px;color:rgba(255,255,255,.6)">₺/kg</small></span></div>' for key,n,r in rows)
    b=f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:50px;height:100%"><div style="display:flex;flex-direction:column;justify-content:space-between"><div class=brand style="font-size:30px">URFA <b>GAP</b> VERİ MERKEZİ</div><div><h1 style="margin:0;font-size:68px">Şanlıurfa<br>borsa fiyatları</h1><div class=chip style="font-size:24px">{trt(t_ik)} itibarıyla</div></div><div class=src style="font-size:21px">urfagap.com/gap-veri-merkezi<br>Kaynak: Şanlıurfa Ticaret Borsası</div></div><div style="display:flex;flex-direction:column;justify-content:center">{L}</div></div>'
    return page(1200,630,b,PT=48,PB=44)
out=OUT
os.makedirs(out,exist_ok=True)
SUTB=[("fistik","Boz kavlak fıstık","Fıstık Boz Kavlak"),("fistik","Kırmızı kabuklu fıstık","Fıstık Kırmızı Kabuklu"),("mercimek","Kırmızı mercimek","Kırmızı Kabuklu Mercimek"),("bugday","Makarnalık buğday","Makarnalık Buğday"),("preseli","Preseli pamuk","Preseli Pamuk 51 Renk")]
srows=[(k,n,get(br["satirlar"],u)) for k,n,u in SUTB]
files={"borsa_gonderi_1080x1350":borsa(1080,1350),"borsa_hikaye_1080x1920":borsa(1080,1920,PT=120,PB=120,HT=60,HS=84,LT=50,GAP=30,RP=44),
"kar_radari_gonderi_1080x1350":radar(1080,1350,RP=14),"borsa_x_facebook_1200x630":wide()}
if (datetime.date.today()-datetime.date.fromisoformat(t_br)).days<=7:  # eski bülteni paylaşılabilir görsele çevirme
    files["sutb_gonderi_1080x1350"]=borsa(1080,1350,rows=srows,tarih=t_br,baslik="ŞUTB resmî<br>bülten fiyatları",kaynak="Kaynak: Şanlıurfa Ticaret Borsası (sutb.org.tr) resmî bülteni. Ortalama fiyat; çubuk aralığı gösterir.")
for n,h in files.items(): open(f"{out}/{n}.html","w",encoding="utf-8").write(h)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    for n,h in files.items():
        W,H=map(int,n.split("_")[-1].split("x"));pg=b.new_page(viewport={"width":W,"height":H});pg.goto(f"file://{os.path.abspath(out)}/{n}.html");pg.wait_for_timeout(300);pg.screenshot(path=f"{out}/{n}.png");pg.close();os.remove(f"{out}/{n}.html")
    b.close()
print(os.listdir(out))