# URFAGAP Veri Merkezi – veri deposu

Bu depo, urfagap.com **GAP Veri Merkezi** sayfasını besleyen veriyi her gün otomatik üretir.

## Nasıl çalışır
1. **GitHub Actions** (`.github/workflows/guncelle.yml`) hafta içi her gün çalışır.
2. `urfagap_veri_botu.py` (yapay zekâ içermez, kural tabanlı) şu kaynakları okur:
   - Şanlıurfa Ticaret Borsası resmî sitesi (son yayımlanan bülten)
   - tarimfiyatlari.com.tr (borsanın son seansı; **ikincil kaynak**, ayrı tutulur)
   - Resmî Gazete (güncel sayı başlıkları, Şanlıurfa/GAP havzası taraması)
3. Veri `docs/veri.json` olarak yazılır. Her kayıtta **kaynak ve tarih** vardır.
4. Hiçbir kaynak okunamazsa bot hata verir, **eski dosya korunur**; sabit/uydurma rakam yazılmaz.
5. `docs/` klasörü **GitHub Pages** ile yayınlanır. Site bu JSON'u okur:
   `https://KULLANICI_ADI.github.io/urfagap-veri/veri.json`

## Kurulum (bir kez, ~5 dk)
1. Bu klasörü **herkese açık (public)** bir depo olarak GitHub'a yükleyin (ör. `urfagap-veri`). Veride gizli bilgi yoktur.
2. Depo → **Settings → Pages** → *Source: Deploy from a branch* → Branch: `main`, Folder: `/docs` → Save.
3. Depo → **Settings → Actions → General** → *Workflow permissions: Read and write permissions* → Save.
4. **Actions** sekmesi → *Veri güncelle* → **Run workflow** ile ilk çalıştırmayı elle yapıp yeşil tik görün.
5. Birkaç dakika sonra adres açılmalı: `https://KULLANICI_ADI.github.io/urfagap-veri/veri.json`

## Dosya sınırı
Bot ve iş akışı **yalnızca** şu dosyalara yazar: `docs/veri.json` ve `docs/gecmis/*.json`. Depodaki diğer dosyalara dokunmaz.

## Güvenlik notları
- Depoya **hiçbir anahtar/şifre** koymayın. Bot yalnızca herkese açık sayfaları okur.
- Site tarafı bu JSON'u yalnızca `textContent` ile yazar (HTML olarak yorumlamaz); depo ele geçirilse bile siteye betik enjekte edilemez.
- GitHub Actions zamanlamaları birkaç dakika gecikebilir; 60 gün hareketsiz depolarda zamanlama otomatik durur (README'ye commit atarak yeniden başlar).

## Yerelde deneme
```
pip install -r requirements.txt
python urfagap_veri_botu.py veri.json
```


## Eklenen çıktılar

| Dosya | Ne işe yarar |
|---|---|
| `docs/veri.json` | Son borsa ve Resmî Gazete verisi (sayfa ve haber kutuları bunu okur) |
| `docs/gecmis/AAAA-AA-GG.json` | Günlük arşiv |
| `docs/seri.json` | Ürün bazlı fiyat geçmişi; sitedeki "Fiyat geçmişi" grafiği bunu okur (en az 3 veri günü birikince görünür) |
| `docs/sosyal/*.png` | Paylaşıma hazır görseller: borsa (gönderi, hikâye, X/Facebook), çiftçi kâr radarı, ŞUTB bülteni (bülten 7 günden eskiyse üretilmez) |

Görseller her güncellemede aynı adla üzerine yazılır. Yayın adresi: `https://KULLANICI.github.io/urfagap-veri/sosyal/borsa_gonderi_1080x1350.png`
