
Python ve Flask kullanarak geliştirdiğim bu kuaför randevu sistemi ile müşteriler kolayca online randevu alabilir, kuaförler ise kendi takvimlerini yönetebilir. Admin paneli ile tüm süreç kontrol altında! 💼

🛠 Kullandığım Teknolojiler:
Python 3.11+
Flask Framework
SQLite Veritabanı
HTML5 & CSS3 (Bootstrap 5)
Jinja2 Template Engine
python-dateutil (Tarih & Saat İşlemleri)
Werkzeug Security (Parola Hashleme & Doğrulama)

🔒 Güvenlik Katmanları:
Şifreler güvenli şekilde hashleniyor (Werkzeug kullanıldı)
Parametrik sorgularla SQL Injection önlendi
Session tabanlı kimlik doğrulama ve rol bazlı erişim kontrolü
Form ve giriş-çıkış doğrulamalarıyla hatalara karşı önlem

🛠 Kurulum
Gerekli paketleri yükleyin:
-bash pip install -r requirements.txt
-bash python init_db.py #Veritabanını başlatın:
-bash python app.py #Uygulamayı başlatın:
