# Render Veri ve Medya Saklama Araştırma Raporu (Güncel)

Görselde ilettiğiniz gibi `dietitian-db` (PostgreSQL) ve `dietitian-app` (Web Service) şeklinde iki ayrı yapınız var. Bu harika bir haber, çünkü yazılarınızın (verilerinizin) neden güvende olduğunu, ancak resimlerin neden kaybolduğunu tam olarak şöyle ayırabiliriz:

## 1. Yazılar Neden Kaybolmaz? (`dietitian-db`)
Görseldeki `PostgreSQL` sizin veritabanı sunucunuzdur.
- **Yazılar (Diyet planları, hasta isimleri, tarif içerikleri vb.)** bu sunucuda saklanır.
- Bu sunucu "Kalıcı" (Persistent) bir sunucudur. Uygulamanıza yeni bir kod gönderdiğinizde bu sunucu sıfırlanmaz.
- **Sonuç:** Yazılarınız her zaman güvendedir, asla kaybolmaz.

## 2. Görseller Neden Kayboluyor? (`dietitian-app`)
Resim dosyaları (jpeg, png vb.) veritabanında değil, `dietitian-app` isimli **Web Service** sunucusunun içinde ("media/" klasöründe) tutulur.
- Bu sunucu "Geçici" (Ephemeral) yapıdadır. 
- Her kod güncellediğimizde (Deploy), bu sunucu silinip GitHub'daki tertemiz haliyle yeniden kurulur.
- Sunucu silinince, o ana kadar admin panelinden yüklediğiniz tüm **fiziksel resim dosyaları** da diskten silinir. Veritabanındaki "resim yolu" (`/media/resim.jpg`) durur ama diskte dosya olmadığı için "Not Found" hatası alırsınız.

## 3. Kesin ve Kalıcı Çözüm: "Persistent Disk"

Resimlerin de yazılarınız gibi asla kaybolmamasını istiyorsanız izlemeniz gereken yol şudur:

1.  Render Dashboard'da `dietitian-app` hizmetinize tıklayın.
2.  Sol menüden **"Disks"** sekmesine gidin.
3.  **"Add Disk"** butonuna basın.
4.  Şu bilgileri girin:
    - **Name:** `media-storage`
    - **Mount Path:** `/opt/render/project/src/media` (Django'nun resimleri aradığı yer)
    - **Size:** `1 GB` (Başlangıç için fazlasıyla yeterli)
5.  Kaydedin.

**Bu neyi değiştirecek?**
Bu işlemi yaptığınızda, Render sizin sunucunuza **"asla silinmeyen bir harici disk"** takar. Artık biz ne kadar kod güncellersek güncelleyelim, o diskteki resim dosyalarına dokunulmaz. Resimleriniz de tıpkı yazılarınız gibi sonsuza kadar saklanır.

**Özet:** Yazılarınız (PostgreSQL sayesinde) zaten güvende. Sadece resimler için "Web Service" kısmına minik bir "Kalıcı Disk" bağlamanız gerekiyor.
