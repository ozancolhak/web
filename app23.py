from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "kuafor_secret"
DB_PATH = "randevular.db"
ADMIN_PASSWORD = "admin123"

def init_db():
    # Veritabanı ve tabloyu oluşturan fonksiyon
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE randevular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                tarih TEXT NOT NULL,
                saat TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Form gönderildiğinde (Randevu alma işlemi)
    if request.method == "POST":
        ad = request.form["ad"].strip()
        tarih = request.form["tarih"]
        saat = request.form["saat"]

        # Tarih ve saat formatlarını kontrol et
        try:
            secilen_tarih = datetime.strptime(tarih, '%Y-%m-%d')
            secilen_saat = datetime.strptime(saat, '%H:%M').time()
        except ValueError:
            flash("Geçersiz tarih veya saat formatı.", "danger")
            return redirect(url_for("index"))

        # Pazar günleri randevu alınamaz (Pazar = 6)
        if secilen_tarih.weekday() == 6:
            flash("Pazar günleri randevu alınamaz, lütfen başka bir gün seçin.", "danger")
            return redirect(url_for("index"))

        # Geçmiş tarihe randevu alınamaz
        bugun = datetime.today().date()
        if secilen_tarih.date() < bugun:
            flash("Geçmiş tarihe randevu alınamaz.", "danger")
            return redirect(url_for("index"))

        # Eğer tarih bugünkü ise, geçmiş saate randevu alınamaz
        if secilen_tarih.date() == bugun:
            simdi = datetime.now().time()
            if secilen_saat <= simdi:
                flash("Geçmiş saate randevu alınamaz.", "danger")
                return redirect(url_for("index"))

        # Alanların boş olup olmadığını kontrol et
        if not ad or not tarih or not saat:
            flash("Lütfen tüm alanları doldurun.", "danger")
            return redirect(url_for("index"))

        # İsim geçerliliğini kontrol et
        if len(ad) > 50 or not ad.replace(" ", "").isalpha():
            flash("Geçerli bir isim girin (sadece harf, 50 karaktere kadar).", "danger")
            return redirect(url_for("index"))

        # Aynı tarih ve saate başka randevu var mı kontrol et
        c.execute("SELECT * FROM randevular WHERE tarih = ? AND saat = ?", (tarih, saat))
        if c.fetchone():
            flash(f"{tarih} - {saat} saatinde başka bir randevu var.", "warning")
            return redirect(url_for("index"))

        # Randevuyu veritabanına ekle
        c.execute("INSERT INTO randevular (ad, tarih, saat) VALUES (?, ?, ?)", (ad, tarih, saat))
        conn.commit()
        flash("Randevunuz başarıyla kaydedildi!", "success")
        return redirect(url_for("index"))

    # --- Sayfa ilk yüklendiğinde veya tarih değiştirildiğinde (GET isteği) ---

    # Bugünün ve seçilen tarihin belirlenmesi
    today = datetime.today().strftime('%Y-%m-%d')
    selected_date = request.args.get('tarih', today)

    # URL'den gelen tarihin geçerli olup olmadığını ve geçmiş bir tarih olup olmadığını kontrol et
    try:
        if datetime.strptime(selected_date, '%Y-%m-%d').date() < datetime.today().date():
            flash("Geçmiş tarihler görüntülenemez, bugün seçildi.", "warning")
            selected_date = today
    except ValueError:
        selected_date = today # Geçersiz formatta ise bugünü kullan

    # Mevcut tüm randevu saatleri
    saatler = ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
               '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
               '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30',
               '22:00', '22:30', '23:00']

    # Seçilen tarihteki dolu saatleri veritabanından al
    c.execute("SELECT saat FROM randevular WHERE tarih = ?", (selected_date,))
    dolu_saatler = [row[0] for row in c.fetchall()]
    
    # Boş saatleri hesapla
    tum_bos_saatler = [s for s in saatler if s not in dolu_saatler]

    # Eğer seçilen tarih bugünse, geçmiş saatleri boş saatler listesinden çıkar
    bos_saatler = []
    if selected_date == today:
        simdi = datetime.now().time()
        bos_saatler = [s for s in tum_bos_saatler if datetime.strptime(s, '%H:%M').time() > simdi]
    else:
        bos_saatler = tum_bos_saatler

    conn.close()
    
    # Gerekli değişkenleri şablona gönder
    return render_template("index.html", bos_saatler=bos_saatler, dolu_saatler=dolu_saatler, saatler=saatler, selected_date=selected_date, today=today)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form["password"]
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            flash("Hatalı şifre!", "danger")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Çıkış yapıldı.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, ad, tarih, saat FROM randevular ORDER BY tarih, saat")
    randevular = c.fetchall()
    conn.close()
    return render_template("admin.html", randevular=randevular)

@app.route("/sil/<int:id>")
def sil(id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM randevular WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Randevu silindi.", "success")
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
