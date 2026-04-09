# PDF Raporlarında Türkçe Karakter (Büyük Harf) Sorunu Çözümü

## Sorun Tespiti
Gönderdiğiniz görseli ve kodları incelediğimde sorunun temel kaynağının Python'ın yerleşik `.upper()` fonksiyonunun Türkçe dil yapısına uygun çalışmaması olduğunu tespit ettim. 

Python'da küçük "i" harfi `.upper()` ile büyütüldüğünde İngilizce standardına göre noktasız büyük "I" şekline dönüşür. 
Bunun sonucunda görselde de görüldüğü gibi:
*   "Abdulkadir" -> "ABDULKADIR"
*   "Öğle Öncesi" -> "ÖĞLE ÖNCESI"
*   "Akşam Yemeği" -> "AKŞAM YEMEĞI"

gibi noktasız, İngilizce "I" harfleri oluşmaktadır. Ayrıca bazı özel durumlarda font uyumsuzluğu da sırıtmasına sebep olur.

## Çözüm Planı
Bu sorunu kökten ve en sağlıklı şekilde çözmek için `diet/pdf_generator.py` dosyasında bir Türkçe büyük harf dönüştürme fonksiyonu (yardımcı fonksiyon) tanımlayacağız. 

**Önerilen Kod Eklenmesi:**
```python
def turkish_upper(text):
    if not isinstance(text, str):
        return text
    # "i" harfini "İ", "ı" harfini "I" ile öncelikli olarak yer değiştir, sonra büyüt.
    return text.replace('i', 'İ').replace('ı', 'I').upper()
```

**Dosyadaki Güncellemeler (Uygulanacak Yerler):**
Bu fonksiyonu `pdf_generator.py` içerisine ekleyip; sistemin `.upper()` kullandığı şu satırları bu fonksiyonla değiştireceğim:
1. Öğün başlıkları: `m.get_meal_type_display().upper()` -> `turkish_upper(m.get_meal_type_display())`
2. Danışan Ad Sayod: `p.first_name.upper()` -> `turkish_upper(p.first_name)`
3. Diyetisyen Unvanı (varsa): `title.upper()` -> `turkish_upper(title)`
4. Tarif Adları: `r.name.upper()` -> `turkish_upper(r.name)`

Bu işlem sonucunda sayfadaki tüm başlıklar gerçek Türkçe karakterle (İ, I) büyüyecek ve görsel bozulmalar ortadan kalkacaktır.

Eğer bu çözüm planını ve oluşturduğum detaylı md belgesini onaylarsanız, hemen kodunuzdaki bu düzenlemeleri yapıp kaydedebilirim.
