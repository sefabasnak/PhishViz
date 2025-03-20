import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from weasyprint import HTML
import io
import os
import re
import requests
import pandas as pd
from zipfile import ZipFile
from io import BytesIO
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import base64

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = "secret_key_for_session"

app.config['APPLICATION_TITLE'] = 'PhishViz - Phishing Saldırı Raporlama Aracı'

# Klasör ayarları
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['LOGO_FOLDER'] = './static/logos'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['LOGO_FOLDER'], exist_ok=True)

# Veritabanı ayarları
db_path = os.path.abspath(os.path.join(app.root_path, 'phishing_reports.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

################################################
# MODELLER
################################################

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    scenario = db.Column(db.String(200))
    domain = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    # Cascade delete ekledik
    tests = db.relationship('Test', backref='customer', lazy=True, cascade="all, delete-orphan")

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Toplu veriler
    data_leaks = db.Column(db.Integer, default=0)
    mail_sent = db.Column(db.Integer, default=0)
    mail_read = db.Column(db.Integer, default=0)
    link_clicked = db.Column(db.Integer, default=0)
    exec_count = db.Column(db.Integer, default=0)

    # test -> report ilişkisi
    # Cascade delete ekledik
    reports = db.relationship('Report', backref='test', lazy=True, cascade="all, delete-orphan")

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

    ip_address = db.Column(db.String(15), index=True)
    location = db.Column(db.String(100), index=True)
    coords_lat = db.Column(db.Float, default=0.0)
    coords_lon = db.Column(db.Float, default=0.0)

    data_leak = db.Column(db.Boolean, default=False)
    data_leak_user = db.Column(db.String(200))  # Veri ihlali yapan kişi
    mail_read_time = db.Column(db.DateTime)     # Mail okuma zamanı
    exec_count = db.Column(db.Integer, default=0)  # satır bazında exec count

class PhishingTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pages = db.relationship('TemplatePage', backref='template', cascade="all, delete-orphan", lazy=True)

class TemplatePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('phishing_template.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    content_html = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

################################################
# GENEL FONKSİYONLAR
################################################

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now(timezone.utc).year}

ip_pattern = re.compile(
    r"^((25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(25[0-5]|2[0-4]\d|[01]?\d?\d)$"
)
ip_cache = {}

def get_ip_info(ip):
    ip_str = str(ip).replace('\xa0','').replace('\u00a0','').strip()
    if ip_str.lower() == 'nan' or ip_str.count('.') != 3 or not ip_pattern.match(ip_str):
        return {"location": "Unknown", "coords": (0,0)}
    if ip_str in ip_cache:
        return ip_cache[ip_str]

    info = {"location": "Unknown", "coords": (0,0)}
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip_str}", timeout=3)
        data = resp.json()
        if data.get('status') == 'success':
            country = data.get('country','Unknown')
            city = data.get('city','Unknown')
            lat = data.get('lat',0)
            lon = data.get('lon',0)
            info["location"] = f"{country}, {city}"
            info["coords"] = [lat, lon]
        else:
            print(f"Geolokasyon başarısız: {ip_str}, Durum: {data.get('status')}")
    except Exception as e:
        print(f"Geolokasyon API çağrısı sırasında hata: {e}")

    ip_cache[ip_str] = info
    return info

def parse_read_time(dt_str):
    if pd.isna(dt_str):
        return None
    dt_str = str(dt_str).strip()
    if not dt_str or dt_str.lower() == 'nan':
        return None
    try:
        return datetime.strptime(dt_str, "%d.%m.%Y - %H:%M:%S")
    except:
        return None

def is_filled(cell):
    if pd.isna(cell):
        return False
    s = str(cell).strip()
    if not s or s.lower() == 'nan':
        return False
    return True

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Dosya uzantısını kontrol eden fonksiyon."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Sanitizasyonu tamamen kaldırmak için sanitize_html fonksiyonunu aşağıdaki gibi tanımlayabilirsiniz:
def sanitize_html(content):
    return content  # İçeriği değiştirmeden geri döndürür

################################################
# ROUTES
################################################

@app.route('/')
def index():
    customers = Customer.query.all()

    total_customers = len(customers)
    total_tests = Test.query.count()
    total_data_leaks = Report.query.filter_by(data_leak=True).count()

    all_reports = Report.query.all()
    all_coords = [[r.coords_lat, r.coords_lon] for r in all_reports if r.coords_lat and r.coords_lon]
    location_labels = [r.location for r in all_reports if r.location != "Unknown"]

    return render_template(
        'index.html',
        customers=customers,
        total_customers=total_customers,
        total_tests=total_tests,
        total_data_leaks=total_data_leaks,
        all_coords=all_coords,
        location_labels=location_labels
    )

@app.route('/new_customer')
def new_customer():
    return render_template('new_customer.html')

@app.route('/add_customer', methods=['POST'])
def add_customer():
    customer_name = request.form.get('customer_name', '').strip()
    scenario = request.form.get('scenario', '').strip()
    domain = request.form.get('domain', '').strip()
    logo_file = request.files.get('logo')

    if not customer_name:
        flash("Müşteri adı gereklidir!", "danger")
        return redirect(url_for('new_customer'))

    existing_customer = Customer.query.filter_by(name=customer_name).first()
    if existing_customer:
        flash("Bu müşteri zaten var!", "warning")
        return redirect(url_for('new_customer'))

    logo_path = ""
    if logo_file and logo_file.filename and allowed_file(logo_file.filename):
        filename = secure_filename(logo_file.filename)
        save_path = os.path.join(app.config['LOGO_FOLDER'], filename)
        logo_file.save(save_path)
        logo_path = f"logos/{filename}"

    try:
        new_customer = Customer(
            name=customer_name,
            scenario=scenario,
            domain=domain,
            logo=logo_path
        )
        db.session.add(new_customer)
        db.session.commit()
        flash(f"Müşteri '{customer_name}' başarıyla eklendi.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Bir hata oluştu: {e}", "danger")
    
    return redirect(url_for('index'))


@app.route('/upload/<int:customer_id>', methods=['GET', 'POST'])
def upload(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        flash("Böyle bir müşteri yok!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                data = pd.read_excel(file_path)
                print(f"Excel dosyası başarıyla yüklendi. Satır sayısı: {len(data)}")
            except Exception as e:
                flash("Yüklenen dosya okunamadı. Lütfen geçerli bir Excel dosyası yükleyin.", "danger")
                print(f"Excel okuma hatası: {e}")
                return redirect(url_for('upload', customer_id=customer_id))

            try:
                new_test = Test(
                    customer_id=customer.id,
                    mail_sent=int(data['Mail Gönderilen Kişiler'].notnull().sum()),
                    mail_read=int(data['Maili Okuyan Kişiler'].notnull().sum()),
                    link_clicked=int(data['Linke Tıklayan Kişiler'].notnull().sum()),
                    data_leaks=int(data['Veri İhlali Yapan Kişiler'].notnull().sum()),
                    exec_count=int(data['Kaç Kere Çalıştırıldığı'].fillna(0).astype(int).sum())
                )
                db.session.add(new_test)
                db.session.commit()
                print(f"Yeni test oluşturuldu: {new_test.id}")
            except Exception as e:
                db.session.rollback()
                flash(f"Bir hata oluştu: {e}", "danger")
                print(f"Test oluşturma hatası: {e}")
                return redirect(url_for('upload', customer_id=customer_id))

            # Report nesnelerini oluşturma
            try:
                for index, row in data.iterrows():
                    print(f"İşlenen satır {index}: {row.to_dict()}")
                    
                    # Linke Tıklayan Kişiler (IP adresi)
                    link_clicker = row.get('Linke Tıklayan Kişiler', '')
                    if pd.isna(link_clicker):
                        ip = ''
                    else:
                        ip = str(link_clicker).strip()
                        if ip.lower() == 'nan':
                            ip = ''

                    geo_info = get_ip_info(ip) if ip else {"location": "Unknown", "coords": (0,0)}
                    
                    # Veri İhlali Yapan Kişiler
                    veri_ihlali = row.get('Veri İhlali Yapan Kişiler', '')
                    if pd.isna(veri_ihlali):
                        veri_ihlali_user = ''
                    else:
                        veri_ihlali_user = str(veri_ihlali).strip()
                        if veri_ihlali_user.lower() == 'nan':
                            veri_ihlali_user = ''

                    data_leak = bool(veri_ihlali_user)

                    # Mail Okuma Tarih ve Saati
                    mail_read_time = parse_read_time(row.get('Mail Okuma Tarih ve Saati'))

                    # Kaç Kere Çalıştırıldığı
                    exec_count = row.get('Kaç Kere Çalıştırıldığı', 0)
                    if pd.isna(exec_count):
                        exec_count = 0
                    else:
                        try:
                            exec_count = int(exec_count)
                        except:
                            exec_count = 0

                    report = Report(
                        test_id=new_test.id,
                        ip_address=ip,
                        location=geo_info["location"],
                        coords_lat=geo_info["coords"][0],
                        coords_lon=geo_info["coords"][1],
                        data_leak=data_leak,
                        data_leak_user=veri_ihlali_user,
                        mail_read_time=mail_read_time,
                        exec_count=exec_count
                    )
                    db.session.add(report)
                    print(f"Report oluşturuldu: {report.id}")
                db.session.commit()
                print("Tüm reportlar başarıyla kaydedildi.")
            except Exception as e:
                db.session.rollback()
                flash(f"Report oluşturulurken bir hata oluştu: {e}", "danger")
                print(f"Report oluşturma hatası: {e}")
                return redirect(url_for('upload', customer_id=customer_id))

            flash("Dosya başarıyla yüklendi ve işleme alındı.", "success")
            return redirect(url_for('dashboard', customer_id=customer.id))
        else:
            flash("Geçersiz dosya türü! Sadece .xlsx veya .xls dosyaları kabul edilmektedir.", "danger")
            return redirect(url_for('upload', customer_id=customer_id))

    return render_template('upload.html', customer=customer)

from collections import defaultdict

@app.route('/dashboard/<int:customer_id>')
def dashboard(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        flash("Böyle bir müşteri yok!", "danger")
        return redirect(url_for('index'))

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    metric = request.args.get('metric')

    tests_query = Test.query.filter_by(customer_id=customer.id)
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            tests_query = tests_query.filter(Test.upload_time >= start_date_obj)
        except ValueError:
            flash("Başlangıç tarihi geçersiz formatta.", "warning")
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            tests_query = tests_query.filter(Test.upload_time <= end_date_obj)
        except ValueError:
            flash("Bitiş tarihi geçersiz formatta.", "warning")
    tests = tests_query.all()

    location_data = []
    read_hour_count = {}
    data_leak_exec = {}
    
    # Hiyerarşik sayım için nested defaultdict kullanımı
    location_hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for test in tests:
        reports = Report.query.filter_by(test_id=test.id).all()
        for report in reports:
            # Sadece ip_address ve koordinatlar dolu olan raporları ekle
            if report.ip_address and report.coords_lat and report.coords_lon:
                location = report.location if report.location != "Unknown" else None
                if not location:
                    continue  # 'Unknown' olanları dahil etme

                # Lokasyon bilgilerini ayrıştırma
                parts = [part.strip() for part in location.split(",")]
                country = parts[0] if len(parts) > 0 else "Unknown"
                city = parts[1] if len(parts) > 1 else "Unknown"
                district = parts[2] if len(parts) > 2 else "Unknown"

                if country == "Unknown" or city == "Unknown":
                    continue  # 'Unknown' olanları dahil etme

                # Hiyerarşik sayımı artırma
                location_hierarchy[country][city][district] += 1

                # IP koordinatlarını ekleme
                location_data.append({
                    "coords": [report.coords_lat, report.coords_lon],
                    "location": f"{country}, {city}, {district}"
                })

            if report.mail_read_time:
                hour_str = report.mail_read_time.strftime("%H:00")
                read_hour_count[hour_str] = read_hour_count.get(hour_str, 0) + 1

            if report.data_leak:
                user_key = report.data_leak_user or report.ip_address or "Bilinmiyor"
                data_leak_exec[user_key] = data_leak_exec.get(user_key, 0) + report.exec_count

    # Grafikler için verileri hazırlama
    # Read Hour grafiği için verileri hazırlama
    read_hour_labels = sorted(read_hour_count.keys())
    read_hour_values = [read_hour_count[h] for h in read_hour_labels]

    # Veri İhlali grafiği için verileri hazırlama
    leak_labels = list(data_leak_exec.keys())
    leak_values = list(data_leak_exec.values())

    # IP Lokasyon Dağılımı için sadece il bazında veri hazırlama
    # Ülke dağılımını kaldırdık

    # İl dağılımı (Ülke - İl şeklinde)
    city_distribution = {}
    for country, cities in location_hierarchy.items():
        for city, districts in cities.items():
            city_key = f"{country} - {city}"
            city_sum = sum(districts.values())
            city_distribution[city_key] = city_sum

    # Grafikler için veri setlerini JSON formatına çevirme
    # Ülke dağılımını kaldırdık, sadece il dağılımını kullanıyoruz

    # İllerin sayısı çok fazla olabilir, en çok IP alan ilk 10 ili gösterelim
    sorted_cities = sorted(city_distribution.items(), key=lambda item: item[1], reverse=True)[:10]
    city_labels = [item[0] for item in sorted_cities]
    city_values = [item[1] for item in sorted_cities]

    stats = {
        "mail_gonderilen_count": sum(int(t.mail_sent) for t in tests),
        "mail_okuyan_count": sum(int(t.mail_read) for t in tests),
        "linke_tiklayan_count": sum(int(t.link_clicked) for t in tests),
        "veri_ihlali_count": sum(int(t.data_leaks) for t in tests),
        "kac_kere_calistirildi_sum": sum(int(t.exec_count) for t in tests)
    }

    # Debug: Verilerin doğru şekilde oluşturulduğunu kontrol et
    print("City Labels:", city_labels)
    print("City Values:", city_values)
    print("Read Hour Labels:", read_hour_labels)
    print("Read Hour Values:", read_hour_values)
    print("Leak Labels:", leak_labels)
    print("Leak Values:", leak_values)

    return render_template(
        'dashboard.html',
        customer=customer,
        stats=stats,
        location_data=location_data,  # Harita için
        read_hour_labels=read_hour_labels,
        read_hour_values=read_hour_values,
        leak_labels=leak_labels,
        leak_values=leak_values,
        city_labels=city_labels,        # Sadece il bazında pie chart için
        city_values=city_values
    )


import os
import base64

@app.route('/export_pdf/<int:customer_id>')
def export_pdf(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        flash("Böyle bir müşteri yok!", "danger")
        return redirect(url_for('index'))

    tests = Test.query.filter_by(customer_id=customer.id).all()
    reports = []
    for t in tests:
        # Yalnızca geçerli raporları dahil edin
        valid_reports = Report.query.filter_by(test_id=t.id).filter(
            Report.location != "Unknown",
            Report.coords_lat != 0.0,
            Report.coords_lon != 0.0
        ).all()
        reports.extend(valid_reports)

    # Genel Özet Verilerini Hesapla
    total_mail_sent = sum(test.mail_sent for test in tests)
    total_mail_read = sum(test.mail_read for test in tests)
    total_link_clicked = sum(test.link_clicked for test in tests)
    total_data_leaks = sum(test.data_leaks for test in tests)
    total_exec_count = sum(test.exec_count for test in tests)

    # Grafikler için Verileri Hazırla
    from collections import defaultdict
    city_counts = defaultdict(int)
    for report in reports:
        city = report.location if report.location else "Unknown"
        city_counts[city] += 1

    city_labels = list(city_counts.keys())[:10]  # İlk 10 şehir
    city_values = list(city_counts.values())[:10]

    # Mail Okuma Saat Dağılımı için
    read_hour_counts = defaultdict(int)
    for report in reports:
        if report.mail_read_time:
            hour = report.mail_read_time.hour
            read_hour_counts[hour] += 1
    read_hour_labels = list(range(24))
    read_hour_values = [read_hour_counts.get(hour, 0) for hour in read_hour_labels]

    # Veri İhlali ve Kaç Kere Çalıştırıldı için
    data_leak_counts = defaultdict(int)
    exec_counts = defaultdict(int)
    for report in reports:
        if report.data_leak:
            data_leak_counts[report.data_leak_user] += 1
        exec_counts[report.exec_count] += 1

    leak_labels = list(data_leak_counts.keys())
    leak_values = list(data_leak_counts.values())

    # Grafikleri Oluştur
    import matplotlib.pyplot as plt

    # İl Bazında IP Dağılımı Grafiği
    plt.figure(figsize=(6,6))
    plt.pie(city_values, labels=city_labels, autopct='%1.1f%%', colors=plt.cm.tab10.colors)
    plt.title('İl Bazında IP Dağılımı')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    city_pie_chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Mail Okuma Saat Dağılımı Grafiği
    plt.figure(figsize=(10,6))
    plt.bar(read_hour_labels, read_hour_values, color='skyblue')
    plt.xlabel('Saat')
    plt.ylabel('Okuma Sayısı')
    plt.title('Mail Okuma Saat Dağılımı')
    plt.xticks(read_hour_labels)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    read_time_chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Veri İhlali & Kaç Kere Çalıştırıldı Grafiği
    plt.figure(figsize=(10,6))
    plt.bar(leak_labels, leak_values, color='salmon')
    plt.xlabel('Veri İhlali Yapan Kişi')
    plt.ylabel('Kaç Kere Çalıştırıldı')
    plt.title('Veri İhlali & Kaç Kere Çalıştırıldı')
    plt.xticks(rotation=45, ha='right')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    data_leak_chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Logo'yu Base64 formatına dönüştür
    if customer.logo:
        try:
            logo_path = os.path.join(app.root_path, 'static', customer.logo)
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Logo yüklenirken hata oluştu: {e}")
            encoded_logo = None
    else:
        encoded_logo = None

    rendered = render_template(
        'pdf_report.html',
        customer=customer,
        tests=tests,
        reports=reports,
        total_mail_sent=total_mail_sent,
        total_mail_read=total_mail_read,
        total_link_clicked=total_link_clicked,
        total_data_leaks=total_data_leaks,
        total_exec_count=total_exec_count,
        city_pie_chart=city_pie_chart,
        read_time_chart=read_time_chart,
        data_leak_chart=data_leak_chart,
        encoded_logo=encoded_logo,
        datetime=datetime
    )

    try:
        pdf = HTML(string=rendered, base_url=request.base_url).write_pdf()
    except Exception as e:
        print(f"PDF oluşturma hatası: {e}")
        flash("PDF oluşturulurken bir hata oluştu.", "danger")
        return redirect(url_for('dashboard', customer_id=customer_id))

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{customer.name}_raporu.pdf"
    )

@app.route('/export_excel/<int:customer_id>')
def export_excel(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        flash("Böyle bir müşteri yok!", "danger")
        return redirect(url_for('index'))

    tests = Test.query.filter_by(customer_id=customer.id).all()
    reports_data = []
    for t in tests:
        test_reports = Report.query.filter_by(test_id=t.id).all()
        for r in test_reports:
            reports_data.append({
                'Test ID': r.test_id,
                'IP Adresi': r.ip_address,
                'Konum': r.location,
                'Enlem': r.coords_lat,
                'Boylam': r.coords_lon,
                'Veri İhlali': 'Evet' if r.data_leak else 'Hayır',
                'Veri İhlali Yapan Kişi': r.data_leak_user or '',
                'Mail Okuma Saati': r.mail_read_time.strftime('%d.%m.%Y - %H:%M:%S') if r.mail_read_time else '',
                'Satır Bazında Exec Count': r.exec_count
            })

    df = pd.DataFrame(reports_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Raporlar')
        writer.save()
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"{customer.name}_raporu.xlsx"
    )

@app.route('/docs')
def docs():
    return render_template('docs.html')

################################################
# ŞABLON YÖNETİM ROTASI (GET VE POST)
################################################

@app.route('/templates_page', methods=['GET', 'POST'])
def templates_page():
    templates_list = PhishingTemplate.query.all()

    if request.method == 'POST':
        try:
            template_name = request.form.get('template_name', '').strip()
            if not template_name:
                flash("Şablon adı boş olamaz.", "danger")
                return redirect(url_for('templates_page'))

            existing_template = PhishingTemplate.query.filter_by(template_name=template_name).first()
            if existing_template:
                flash("Bu şablon adı zaten kullanılıyor.", "danger")
                return redirect(url_for('templates_page'))

            # Yeni şablon oluştur
            new_template = PhishingTemplate(template_name=template_name)
            db.session.add(new_template)
            db.session.commit()

            # Sayfaları ekle
            page_contents = request.form.getlist('page_content[]')
            for idx, content in enumerate(page_contents, start=1):
                content_html = sanitize_html(content)  # Sanitizasyonu uygula
                if content_html.strip():
                    page = TemplatePage(
                        template_id=new_template.id,
                        page_number=idx,
                        content_html=content_html
                    )
                    db.session.add(page)

            db.session.commit()
            flash("Yeni şablon başarıyla oluşturuldu.", "success")
            return redirect(url_for('templates_page'))

        except Exception as e:
            app.logger.error(f"Error while saving template: {e}")
            db.session.rollback()
            flash("Şablon kaydedilirken bir hata oluştu.", "danger")
            return redirect(url_for('templates_page'))

    return render_template('templates_page.html', templates_list=templates_list)

@app.route('/edit_template/<int:template_id>', methods=['GET', 'POST'])
def edit_template(template_id):
    template = PhishingTemplate.query.get_or_404(template_id)
    if request.method == 'POST':
        try:
            template_name = request.form.get('template_name', '').strip()
            app.logger.debug(f"Received Template Name for Editing: {template_name}")

            if not template_name:
                flash("Şablon adı boş olamaz.", "danger")
                return redirect(url_for('edit_template', template_id=template_id))

            existing_template = PhishingTemplate.query.filter_by(template_name=template_name).first()
            if existing_template and existing_template.id != template_id:
                flash("Bu şablon adı başka bir şablon tarafından kullanılıyor.", "danger")
                return redirect(url_for('edit_template', template_id=template_id))

            template.template_name = template_name

            # Mevcut sayfaları silip yenilerini ekliyoruz
            TemplatePage.query.filter_by(template_id=template.id).delete()
            db.session.commit()
            app.logger.debug(f"Deleted existing pages for template ID: {template.id}")

            # Yeni sayfaları ekle
            page_contents = request.form.getlist('page_content[]')
            app.logger.debug(f"Page contents received for editing: {len(page_contents)} pages")

            for idx, content in enumerate(page_contents, start=1):
                content_html = sanitize_html(content)  # Sanitizasyonu kaldırdık, artık içerik değiştirilmeden ekleniyor
                app.logger.debug(f"Processing Page {idx} for Editing: {content_html[:50]}...")
                if content_html.strip():
                    page = TemplatePage(
                        template_id=template.id,
                        page_number=idx,
                        content_html=content_html
                    )
                    db.session.add(page)
                    app.logger.debug(f"Added page {idx} to template {template.id}")
                else:
                    app.logger.debug(f"Skipped empty page content for page {idx}")

            db.session.commit()
            app.logger.debug("All pages updated and committed successfully.")

            flash("Şablon başarıyla güncellendi.", "success")
            return redirect(url_for('templates_page'))

        except Exception as e:
            app.logger.error(f"Error while updating template: {e}")
            db.session.rollback()
            flash("Şablon güncellenirken bir hata oluştu.", "danger")
            return redirect(url_for('edit_template', template_id=template_id))

    return render_template('edit_template.html', template=template)

################################################
# ŞABLON ÖNİZLEME ROTASI
################################################

@app.route('/phishing_template_preview/<int:template_id>')
def phishing_template_preview(template_id):
    phish_tmp = PhishingTemplate.query.get_or_404(template_id)
    pages = TemplatePage.query.filter_by(template_id=phish_tmp.id).order_by(TemplatePage.page_number).all()
    return render_template('phishing_template_preview.html', phish_tmp=phish_tmp, pages=pages)

################################################
# ŞABLON SİLME ROTASI
################################################

@app.route('/delete_template/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    template = PhishingTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash("Şablon başarıyla silindi.", "success")
    return redirect(url_for('templates_page'))

################################################
# ŞABLON İNDİRME ROTASI
################################################

@app.route('/download_template/<int:template_id>')
def download_template(template_id):
    template = PhishingTemplate.query.get_or_404(template_id)
    pages = TemplatePage.query.filter_by(template_id=template.id).order_by(TemplatePage.page_number).all()

    # Şablon sayfalarını zip dosyası olarak paketleyelim
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for page in pages:
            filename = f"{template.template_name}_sayfa_{page.page_number}.html"
            zip_file.writestr(filename, page.content_html)
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{template.template_name}_templates.zip"
    )


@app.route('/example_data')
def example_data():
    try:
        # Excel dosyasının tam yolu
        file_path = os.path.join(app.root_path, 'static', 'excel', 'example.xlsx')

        # Dosyanın varlığını kontrol edin
        if not os.path.exists(file_path):
            flash("Örnek veri dosyası bulunamadı.", "danger")
            return redirect(url_for('index'))

        # Excel dosyasını oku ve HTML tabloya dönüştür
        df = pd.read_excel(file_path)
        table_html = df.to_html(
            classes='table table-striped table-bordered table-dark', 
            index=False, 
            justify='center'
        )

        # HTML şablonunu render et
        excel_filename = 'excel/example.xlsx'  # Statik dosya yolu
        return render_template('example_data.html', excel_filename=excel_filename, table_html=table_html)
    except Exception as e:
        flash(f"Bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    # Müşteriye bağlı tüm logoları silmek için dosya sisteminden de temizleme yapabilirsiniz
    if customer.logo:
        logo_path = os.path.join(app.root_path, 'static', customer.logo)
        if os.path.exists(logo_path):
            os.remove(logo_path)
    
    db.session.delete(customer)
    db.session.commit()
    
    flash(f"Müşteri '{customer.name}' başarıyla silindi.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)