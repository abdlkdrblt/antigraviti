# PDF Ölçü ve Porsiyon Hesaplama Güncelleme Planı (V3 - Akıllı Birim Çözücü)

Veritabanı yapısını değiştirmek yerine, kodun içinde tüm senaryoları (tam sayı, aralık, kesir) anlayan "Akıllı Birim Çözücü" mantığına geçiyoruz. Bu sayede mevcut veri giriş alışkanlığınızı bozmadan en doğru sonucu alacağız.

## 1. Hedeflenen Akıllı Hesaplama Örnekleri

| Giriş Verisi | Porsiyon (Çarpan) | PDF'teki Net Sonuç | Mantık |
| :--- | :---: | :--- | :--- |
| **10** orta boy | 3 | **30** orta boy | Tam Sayı Çarpımı |
| **13-15** adet | 3 | **39-45** adet | Aralığı Ayrı Ayrı Çarpma |
| **1/4** kase | 3 | **3/4** kase | Kesiri Çarpma |
| **1.5** su bardağı | 2 | **3** su bardağı | Ondalık Çarpma |

## 2. Uygulama Planı

### A. Metin Parçalama Algoritması
Sisteme metin içerisindeki sayıları (sayı, tireli aralık veya bölü işaretli kesir) tespit eden bir yardımcı fonksiyon eklenecek.
1. Metnin başındaki sayısal ifadeyi bul.
2. Eğer bu bir aralıksa (`13-15`), her iki tarafı da porsiyon ile çarp.
3. Eğer bu bir kesirse (`1/4`), pay kısmını porsiyon ile çarp.
4. Çıkan sonucu metnin geri kalanıyla (birimle) birleştirip PDF'e bas.

### B. PDF Kod Güncellemesi
`pdf_generator.py` içindeki `MealFood` döngüsü bu akıllı fonksiyonu çağıracak. 

**Örnek Senaryo:**
`Diyanetteki Porsiyon: 3`   
`Besindeki Ölçü: "13-15 adet"`   
`Sistem Çıktısı: "39-45 adet"`

## 3. Faydalar
1. **Sıfır Veritabanı Değişikliği:** Mevcut verilerinizi bozmaz, yeni kutucuklar eklemez.
2. **Esneklik:** Her türlü yazım şeklini (kesir, tire, nokta) destekler.
3. **Okunabilirlik:** Danışan "3 porsiyon kuruyemiş, her porsiyon 13-15 ise kaç eder?" diye düşünmez, direkt "39-45 tane yiyeceğim" der.

---
**Onayınızla bu "Akıllı Birim Çözücü" algoritmasını `pdf_generator.py` dosyasına uygulayabilirim.**
