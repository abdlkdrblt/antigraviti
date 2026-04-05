# 📄 Klinik Diyet Planı - PDF Tasarım ve Özellik Rehberi

Bu döküman, **Aylin Balkan Dijital Klinik** uygulaması için geliştirilen premium PDF raporlama sisteminin tasarım prensiplerini, klinik özelliklerini ve teknik detaylarını içermektedir.

---

## 🎨 1. Tasarım Estetiği ve Görsel Kimlik

Rapor, danışana "Lüks Klinik" deneyimini dijital ortamda da yaşatmak üzere **Zümrüt Yeşili (Emerald Green)** ve **Altın Sarısı (Gold)** paleti üzerine inşa edilmiştir.

- **Renk Paleti:**
  - `Primary (#1A3C34)`: Güven ve profesyonellik veren koyu orman yeşili.
  - `Accent (#C5A059)`: Vurgular ve çerçeveler için kullanılan prestij rengi.
  - `Background (#F9FBF9)`: Sayfa genelinde kullanılan, gözü yormayan çok açık yeşil/gri tonu.
- **Tipografi:**
  - **DejaVu Sans:** Türkçe karakter (ı, ş, ğ, vb.) desteği sağlayan, modern ve okunabilirliği yüksek font ailesi.
  - Başlıklarda `Bold`, içeriklerde `Regular` ağırlıklar kullanılarak hiyerarşi sağlanmıştır.
- **Sayfa Düzeni:**
  - Sayfa kenarlarında geniş boşluklar bırakılarak "ferah" bir görünüm elde edilmiştir.
  - Sayfa altlarında (footer) sayfa numarası ve klinik web sitesi bilgisi sabitlenmiştir.

---

## 🥗 2. Klinik Özellikler ve Akıllı Rehberler

Rapor, sadece bir yemek listesi değil, aynı zamanda danışan için interaktif bir uygulama rehberi niteliğindedir.

### A. "Değişim" Terminolojisi
- Klinik standartlara uygun olarak, tüm besin ve tarifler için 1 ve üzeri miktarlarda **"Değişim"** ifadesi kullanılmaktadır (Örn: 2 Değişim).

### B. Akıllı Porsiyon Notları (1 Porsiyon Referansı)
- Her besin ve tarifin yanında, 1 değişimin gerçek hayatta neye denk geldiği parantez içinde belirtilir.
- *Örnek:* **Tam Ceviz** (1 Porsiyonu: 2 tam adet)
- Redundant (gereksiz) sayısal "1" ifadeleri gizlenerek görsel temizlik sağlanmıştır.

### C. Otomatik Hatırlatma Mekanizması
- 1 değişimden fazla tüketilmesi gereken her öğe için, listenin hemen altına otomatik bir uyarı eklenir.
- **Format:** `HATIRLATMA: X değişim porsiyon miktarının X katıdır.`
- Bu not, danışanın porsiyon miktarını yanlış hesaplamasını engellemek için kalın başlık ve italik font ile vurgulanmıştır.

### D. Dinamik Alternatif Senkronizasyonu
- Her ana öğünün altında, diyetisyen tarafından belirlenen alternatifler klinik bir dille listelenir.
- Alternatifler de ana öğünle aynı porsiyon referans bilgilerini taşır.

---

## 🍽️ 3. Tarif Yönetimi ve Sunumu

Diyet listesinde yer alan tarifler (Recipe), raporun sonunda modern kartlar şeklinde sunulur.

- **Kapsamlı İçerik:** Sadece ana öğündeki tarifler değil, alternatif olarak sunulan tüm tarifler de bu bölüme otomatik dahil edilir.
- **Görsel Odak:** Tarifler, yüksek kaliteli görseller ve yuvarlatılmış köşeli kartlarla sunulur.
- **Sadeleştirilmiş İçerik:** Kullanıcı dostu bir yaklaşım için, tarif kartlarından ham kalori/makro değerleri ve karmaşık malzeme listeleri gizlenmiştir. Odak noktası doğrudan **"Klinik Hazırlanış"** metnidir.
- **Video Entegrasyonu:** Eğer tarifin bir YouTube videosu varsa, kartın altında doğrudan tıklanabilir bir video linki yer alır.

---

## 🛒 4. Akıllı ve Kompakt Alışveriş Listesi

Raporun sonunda yer alan alışveriş listesi, maksimum verimlilik için optimize edilmiştir.

- **3 Sütunlu Kompakt Yapı:** Sayfa yerleşimini korumak için liste 3 sütuna bölünmüş ve boşluklar daraltılmıştır.
- **Interaktif Kontroller:** Her ürünün başında baskı alındığında işaretlenebilir boş bir kutucuk (**☐**) bulunur.
- **Alternatif İşaretleme (*):** Sadece alternatif öğünlerden gelen malzemeler bir yıldız (`*`) ile işaretlenir.
- **Dipnot Sistemi:** Alışveriş listesinin altında, yıldız işaretli ürünlerin alternatifler için olduğu bilgisini veren klinik bir dipnot bulunur.

---

## 📝 5. Diyetisyen Tavsiyeleri

Özel klinik notlar ve tavsiyeler bölümü, profesyonel bir sunumla raporun sonunda yer alır.

- **Sayfa Bölünme Koruması (KeepTogether):** Tavsiye kutuları çok uzun olsa bile sayfa sonunda ikiye bölünmez; bir bütün olarak bir sonraki sayfaya aktarılır.

---

## 🛠️ 6. Teknik Altyapı Notları

- **Motor:** Python - `ReportLab` (Platypus katmanı).
- **Grafik Motoru:** Dinamik kaloriyi merkezde gösteren özel `DonutChart` ve progresif `ProgressBar` sınıfları.
- **Veri Verimliliği:** SQL sorgularında `prefetch_related` kullanılarak, alternatiflerin ve tarif içeriklerinin tek seferde çekilmesi sağlanmıştır.

---
*Bu rapor tasarımı, Aylin Balkan Dijital Klinik vizyonuna göre sürekli olarak geliştirilmektedir.*
