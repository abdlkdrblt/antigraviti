# PDF Ölçü ve Porsiyon Hesaplama Güncelleme Planı

Bu belge, diyet planı PDF'inde yer alan besin miktarlarının daha anlaşılır hale getirilmesi için porsiyon çarpanı ile birim miktarının otomatik çarpılmasına yönelik teknik planı içerir.

## 1. Mevcut Durum (Problem)
Şu an besinler PDF'te şu şekilde görünüyor:
- **Örnek:** 2 Porsiyon Badem (1 Porsiyonu: 10 orta boy)
- **Alt Bilgi:** HATIRLATMA: 2 ölçü porsiyon miktarının 2 katıdır.
- **Sıkıntı:** Danışan "kaç tane yiyeceğim?" sorusuna cevap bulmak için zihninden çarpma işlemi yapmak zorunda kalıyor.

## 2. Hedeflenen Durum (Çözüm)
Besinlerin PDF'te otomatik hesaplanmış net değerlerle görünmesi:
- **Yeni Görünüm:** 2 Porsiyon Badem **(20 Orta Boy)**
- **Kural:** `Diyetteki Miktar (Örn: 2)` X `Besin Özütündeki Birim (Örn: 10)` = `Sonuç (20)`

## 3. Uygulama Adımları

### A. Mantıksal Değişiklik
`pdf_generator.py` içerisindeki `MealFood` döngüsünde şu değişiklik yapılacak:
- Mevcut `val_g` (diyetteki porsiyon sayısı) alınacak.
- Besinin `measure_value` (özütteki 1 porsiyonluk miktar) değeri alınacak.
- Bu iki değer çarpılarak `net_miktar` bulunacak.
- `HATIRLATMA` yazısı tamamen kaldırılarak bu bilgi ana parantez içine dahil edilecek.

### B. Kod Güncellemesi (Örnek Mantık)
```python
# Eski hali:
# ref_info = (1 Porsiyonu: 10 orta boy)

# Yeni hali:
net_val = float(mf.measure_value) * float(mf.food.measure_value)
net_unit = mf.food.measure_unit.name
ref_info = f" ({net_val:g} {net_unit})"
```

## 4. Faydalar
1. **Basitlik:** Danışan tek seferde ne kadar tüketeceğini görür.
2. **Hata Payı:** Diyetisyenin notlara "2 katını ye" yazmasına gerek kalmaz, sistem otomatik hesaplar.
3. **Estetik:** Gereksiz "Hatırlatma" satırları silineceği için diyet listesi çok daha temiz görünür.

---
**Onayınızla bu değişikliği `pdf_generator.py` dosyasına uygulayabilirim.**
