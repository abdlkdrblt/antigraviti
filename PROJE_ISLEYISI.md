# 🥗 Diyetisyen Otomasyon Sistemi - "Akıllı Klinik Asistanı" İşleyiş Dokümantasyonu

Bu doküman, **Diyetisyen Aylin Balkan** için geliştirilen, saniyeler içinde analiz yapabilen ve premium raporlar sunan "Akıllı Klinik Asistanı" sisteminin teknik ve işlevsel çalışma prensiplerini açıklamaktadır.

---

## 🏗️ 1. Genel Mimari ve Teknoloji

Sistem, modern tıbbi beslenme ilkeleri ile yazılım otomasyonunu birleştiren **Django 5.x** tabanlı bir yapıdır. 

- **Akıllı Backend:** Python 3 & Django
- **Gerçek Zamanlı Motor:** jQuery & Select2 (Django Admin Entegrasyonu)
- **Klinik Hesaplamalar:** Mifflin-St Jeor Bazal Metabolizma Hızı (BMR) algoritması.
- **Premium PDF Motoru:** ReportLab (Platypus & Graphics) - Özelleştirilmiş Donut Chart ve Card-Layout yapısı.
- **Tasarım Dili:** Orman Yeşili (#1A3C34), Altın (#C5A059) ve Yumuşak Krem (#F9FBF9) paleti.

---

## 📊 2. Akıllı Veri Modelleri (Models)

Sistemin "Zekası" şu üç temel modelin entegrasyonundan gelir:

1.  **Danışan Paneli (`Patient`):** Sadece bir isim değil; boy, kilo, yaş, cinsiyet ve aktivite katsayısı verilerini tutar. Sistem bu verileri kullanarak saniyeler içinde **BMR** ve **Önerilen Günlük Kalori** değerlerini hesaplar.
2.  **Gelişmiş Diyet Planı (`DietPlan`):** Hedef kalori ve makro yüzdeler (% Karb/Prot/Yağ) bu modelde saklanır. Logo yüklenmezse, diyetisyen profil logosu saniyeler içinde varsayılan olarak atanır.
3.  **Klinik Tarif Kitapçığı (`Recipe`):** Hazırlanış metinleri, YouTube video rehberleri ve porsiyon başına saniyeler içinde hesaplanmış makro değerlerini içerir.

---

## ⚡ 3. Canlı Klinik Dashboard (Live Engine)

Admin panelindeki "Diyet Planı Ekle/Düzenle" ekranı, saniyeler içinde tepki veren bir **akıllı asistan** gibi çalışır:

1.  **Otomatik Hesaplama:** Bir danışan seçtiğiniz an; yaşına, kilosuna ve boyuna göre bazal hızı (BMR) ve önerilen klinik kalori hedefi ekrana saniyeler içinde yansır.
2.  **Anlık Makro Takibi:** Siz öğünlere besin veya tarif ekledikçe, sayfanın altındaki **Klinik Analiz Paneli** saniyeler içinde güncellenir.
3.  **Görsel Uyarılar:** Hedeflenen kalori veya proteinin üzerine çıktığınızda veya altında kaldığınızda; ilerleme çubukları (progress bars) saniyeler içinde renk değiştirerek sizi uyarır.
4.  **Nested Management:** İç içe geçmiş (Nested) öğün yapısı sayesinde saniyeler içinde sınırsız öğün ve besin ekleyebilirsiniz.

---

## 💎 4. Premium PDF Raporlama Sistemi

Sıradan "Excel çıktıları" yerine, dergi kalitesinde **"Klinik Yaşam Rehberi"** saniyeler içinde üretilir:

*   **Donut Summary:** Raporun başında, merkeze toplam kaloriyi alan şık bir Donut Grafik (Makro Dağılımı) bulunur.
*   **İlerleme Çubukları:** Hedef vs. Alınan değerler, klinik seviyede ince progress bar'lar ile gösterilir.
*   **Bölünmez Kart Yapısı (Card Layout):**
    *   Öğünler bağımsız kartlar halindedir.
    *   `NOSPLIT` ve `KeepTogether` algoritmaları sayesinde; bir öğün başlığı sayfa sonunda tek başına kalmaz, tarif kartları saniyeler içinde sayfa ortasında bölünmez.
*   **Tarif Kitapçığı:** Raporun sonunda, diyet listesindeki tüm tariflerin görsel, malzeme ve yapılış detaylarını içeren lüks bir bölüm saniyeler içinde oluşturulur.

---

## 🛠️ 5. Teknik Notlar

*   **Font Desteği:** `static/fonts/DejaVuSans.ttf` ile saniyeler içinde pürüzsüz Türkçe karakter desteği sağlanır.
*   **Otomatik Logolama:** `DietPlan.save()` metodu, logo boş bırakıldığında diyetisyenin kurumsal kimliğini saniyeler içinde plana işler.
*   **API Entegrasyonu:** `views.py` altındaki `/api/food-data/` uç noktası, tüm besin kütüphanesini saniyeler içinde JS motoruna besler.

---

> **Sonuç:** Bu sistem, diyetisyene veri girişi hamallığı yaptırmak yerine, klinik kararlarında saniyeler içinde rehberlik eden profesyonel bir asistan görevi görür.
