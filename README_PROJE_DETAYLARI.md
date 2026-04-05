# Smart Dietitian Assistant (Akıllı Diyetisyen Asistanı)

Gelişmiş, diyetisyenlere özel klinik yönetim ve diyet planlama sistemi. Bu uygulama, diyetisyenlerin hasta takibi yapmasını, gerçek zamanlı makro besin hesabı yapmasını ve yüksek kalitede, görsel odaklı PDF diyet raporları oluşturmasını sağlar.

## 🚀 Temel Özellikler

### 👥 Danışan Yönetimi
*   **Klinik Bilgiler:** Danışanların yaş, boy, kilo, cinsiyet ve aktivite düzeyi bilgilerinin saklanması.
*   **BMR Hesaplama:** Mifflin-St Jeor formülü ile bazal metabolizma hızı ve günlük kalori ihtiyacı hesaplaması.
*   **Birebir Takip:** Her danışana özel birden fazla diyet planı oluşturma geçmişi.

### 🍱 Diyet Planlama ve Akıllı Asistan
*   **Gerçek Zamanlı Makro Takibi:** Diyet ekleme ekranında siz besinleri seçerken sayfanın en üstünde anlık olarak Kalori, CHO (Karbonhidrat), Protein ve Yağ değerlerinin hedefe göre doluluk oranlarını gösteren canlı panel.
*   **Akıllı Asistan Önerileri:** Bir besin seçildiğinde, sistem o besinin ait olduğu **Değişim Grubu**'nu (Meyve, Et, Süt vb.) tanır ve size anında "🍎 Portakal", "🍎 Muz" gibi diyet dışı kalmadan kullanılabilecek eşdeğer meyveleri/tarifleri önerir.
*   **Hızlı Seçim:** Önerilen besine tek tıklama ile diyet planına alternatif olarak otomatik ekleme özelliği.

### 🍳 Besin ve Tarif Veritabanı
*   **Otomatik Besin Değerleri:** Besinlerin 100g veya adet bazlı makro değerlerinin girilmesi.
*   **Gelişmiş Tarif Sistemi:** Tariflerin içindeki malzemelere göre kalori ve makro değerlerinin sistem tarafından otomatik hesaplanması.
*   **Hazırlanış Metinleri:** Tariflere özel hazırlama talimatları ve YouTube video linkleri.

### 📄 Premium PDF Raporlama
*   **Luxury Clinic Aesthetic:** "Modern Premium" tasarımlı, zümrüt yeşili (Emerald) tonlarında, görsel ağırlıklı profesyonel PDF raporları.
*   **Görsel Destek:** Öğün görselleri ve her öğüne özel tarif kartları.
*   **DANIŞAN REHBERİ:** Raporun sonunda otomatik olarak eklenen, diyetisyen tarafında belirlenen genel Değişim/Alternatif listeleri (Ekmek Grubu Değişimleri vb.).
*   **Diyetisyen Logosu:** Antetli kağıt düzeninde logo ve diyetisyen iletişim bilgilerinin otomatik entegrasyonu.

## 🏛️ Veri Modelleri (DB Yapısı)

*   **Patient (Danışan):** Kimlik ve klinik ölçüm bilgileri.
*   **Food (Besin):** Besin adı, porsiyon değeri (g, ml, adet vb.) ve makrolar.
*   **Recipe (Tarif):** Malzemelerden hesaplanan toplam makro değerleri ve tarif detayları.
*   **DietPlan:** Danışan bazlı genel hedefler ve plana özel ayarlar.
*   **Meal (Öğün):** Kahvaltı, Öğle, Akşam ve Ara Öğünler (Ordering ile sıralı).
*   **MealFood / MealRecipe:** Bir öğüne eklenen asıl besinler/tarifler.
*   **MealAlternative:** Bir besin/tarif için kullanıcı tarafından manuel eklenen "Özel Alternatifler".
*   **ExchangeList (Değişim Listesi):** Klinik olarak eşdeğer sayılan (Muz - Elma gibi) besinleri gruplayan yapı.

## 🛠️ Teknik Altyapı
*   **Backend:** Python 3.11+, Django 5.0
*   **Frontend:** JavaScript (Live Dashboard logic), jQuery, Select2, CSS (Vanilla Modern)
*   **PDF Engine:** ReportLab (Yüksek performanslı, vektörel PDF üretimi)
*   **Database:** SQLite3 (Geliştirme için), PostgreSQL uyumlu yapı.
*   **Media:** Görsel yönetimi için Pillow.

## 💻 Kurulum ve Çalıştırma

1.  **Gerekli Kütüphaneleri Kurun:**
    ```bash
    pip install django reportlab pillow django-nested-admin
    ```
2.  **Veritabanını Hazırlayın:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
3.  **Sunucuyu Başlatın:**
    ```bash
    python manage.py runserver 8000
    ```
4.  **Admin Paneli:** `http://127.0.0.1:8000/admin/` üzerinden giriş yapabilirsiniz.

---
*Geliştiren: Antigravity AI Assistant*
