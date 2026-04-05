# PythonAnywhere Canlı Sunucu Yayına Alma Rehberi

Bu rehber, projenizi PythonAnywhere üzerinde yayına alırken izlemeniz gereken adımları ve yerel çalışma (local) ile canlı ortamı (production) nasıl senkronize tutacağınızı açıklar.

## 1. Hazırlık ve .env Sistemi

Canlı sunucuda şifrelerinizin ve gizli anahtarlarınızın güvende olması için `.env` sistemine geçiyoruz.

### env.example Dosyası Oluşturun
Proje ana dizinine bir `env.example` dosyası ekleddim. Bu dosyadaki değişkenleri kendi bilgilerinizle doldurup `.env` olarak kaydetmelisiniz.

---

## 2. PythonAnywhere Kurulum Adımları

### Projeyi Sunucuya Yükleme
PythonAnywhere panelinden **Bash Console** açın ve projenizi Git üzerinden çekin veya dosyaları yükleyin.
```bash
git clone https://github.com/kullanici_adiniz/proje_adiniz.git
cd proje_adiniz
```

### Sanal Ortam (Virtualenv) Oluşturma
Sunucuda projeye özel bir sanal ortam oluşturun:
```bash
mkvirtualenv --python=/usr/bin/python3.10 dietitian_venv
pip install -r requirements.txt
```

### Statik Dosyaları Toplama
```bash
python manage.py collectstatic
```

---

## 3. Web App Yapılandırması (PythonAnywhere Paneli)

1.  **Web** sekmesine gidin ve "Add a new web app" butonuna tıklayın.
2.  "Manual Configuration" seçeneğini ve uygun Python sürümünü (3.10) seçin.
3.  **Code** kısmında:
    -   `Source code`: `/home/kullanici_adiniz/proje_adiniz`
    -   `Working directory`: `/home/kullanici_adiniz/proje_adiniz`
    -   `WSGI configuration file`: Bu dosyayı açın ve içeriğini aşağıdakine benzer şekilde düzenleyin.

#### WSGI Dosyası İçeriği:
```python
import os
import sys

# Proje dizinini ekleyin
path = '/home/kullanici_adiniz/proje_adiniz'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4.  **Virtualenv** kısmına sanal ortam adını yazın: `dietitian_venv`
5.  **Static Files** kısmına şunları ekleyin:
    -   `URL`: `/static/` -> `Directory`: `/home/kullanici_adiniz/proje_adiniz/staticfiles`
    -   `URL`: `/media/` -> `Directory`: `/home/kullanici_adiniz/proje_adiniz/media`

---

## 4. Yerel (Local) ve Canlı (Production) Arasında Geçiş

Sistemi her iki tarafta da sorunsuz çalıştırmak için tek yapmanız gereken `.env` dosyasını yönetmektir.

-   **Local:** `.env` dosyanızda `DEBUG=True` ve `DATABASE_URL` (SQLite) kalsın.
-   **Canlı:** `.env` dosyanızda `DEBUG=False` yapın ve gerçek domaininizi `ALLOWED_HOSTS` listesine ekleyin.

> **ÖNEMLİ:** `.env` dosyanızı asla Git gibi platformlara yüklemeyin! (gitignore dosyanıza `.env` eklediğinizden emin olun).

---

## 5. Veritabanı ve Admin
PythonAnywhere bash terminalinde:
```bash
python manage.py migrate
python manage.py createsuperuser
```

Artık siteniz yayında! Domain üzerinden admin panelinize giriş yapıp verileri girmeye başlayabilirsiniz.
