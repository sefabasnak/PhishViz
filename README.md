

# PhishViz

## Proje Hakkında
PhishViz, GoPhish sonuçlarını grafiksel sonuçlara çevirip raporlamaya yardımcı olmak için geliştirilmiş bir sosyal mühendislik raporlama uygulamasıdır. Bu proje, güvenlik testlerinde kullanılan phishing şablonlarının oluşturulmasını, düzenlenmesini ve raporlanmasını kolaylaştırmayı amaçlar. Kullanıcılar, müşteri bilgilerini ekleyebilir, hazır şablonlar üzerinde çalışabilir ve verileri Excel formatında indirebilir.

**Önemli Not:**  
`report.py` içerisindeki 7. satırda bulunan API URL’sini projenize uygun şekilde güncellemeniz gerekmektedir. Örnek kullanım:

API_URL = “https://gophish-server:3333/api/campaigns/?api_key=api_key”

## Özellikler
- **Phishing Şablonları Yönetimi:**  
  - Phishing şablonlarını ekleme, düzenleme ve silme.
  - CKEditor ile dinamik şablon düzenleme.
- **Örnek Veri:**  
  - Oluşturulan veriyi tablo olarak görüntüleme.
  - Excel formatında örnek veri oluşturma ve indirme.
- **Müşteri Bilgileri:**  
  - Müşteri bilgilerini girme ve saklama.
- **GoPhish Sonuçları Raporlama:**  
  - GoPhish API'sinden kampanya verilerini çekme.
  - Kampanya timeline verilerini belirli sütunlar halinde Excel raporuna aktarma.
  - Rapor dosyası adında ve konsol çıktısında hangi kampanya ID'sinin işlendiğini belirtme.
- **Grafiksel Raporlama:**  
  - GoPhish sonuçlarının grafiksel çıktılarıyla raporlanması (Matplotlib ile).

## Nasıl Yüklenir?

### 1. Sanal Ortam Oluşturma

```bash
python3 -m venv venv
source venv/bin/activate    # Linux/MacOS için
# veya
venv\Scripts\activate       # Windows için

2. Gereksinimlerin Yüklenmesi

Projeyi çalıştırmak için gerekli bağımlılıklar requirements.txt dosyasında belirtilmiştir. Aşağıdaki komutu kullanarak tüm bağımlılıkları yükleyin:

pip install -r requirements.txt

3. Uygulamayı Başlatma

Ana arayüzü çalıştırmak için:

python3 app.py
```


Nasıl Kullanılır?

Phishing Şablonları Yönetimi
	1.	PhishViz arayüzüne giriş yapın ve Phishing Şablonları sayfasına gidin.
	2.	“Yeni Şablon Ekle” butonunu kullanarak şablon oluşturun.
	3.	Mevcut şablonlar üzerinde düzenleme yapabilir veya şablonları silebilirsiniz.

Örnek Veri
	1.	Örnek Veri sayfasında verileri tablo olarak görüntüleyin.
	2.	Excel dosyasını indirmek için “İndir” bağlantısını kullanın.

GoPhish Sonuçlarını Raporlama (report.py)

report.py aracı, GoPhish API’sinden kampanya verilerini çekerek mevcut kampanyaların ID ve isimlerini listeler. Kullanıcı, listeden raporlamak istediği kampanya ID’sini seçer. Seçilen kampanyanın timeline verileri, aşağıdaki sütunlar halinde Excel raporuna aktarılır:
	•	Mail Gönderilen Kişiler
	•	Maili Okuyan Kişiler
	•	Mail Okuma Tarih ve Saati
	•	Linke Tıklayan Kişiler
	•	Veri İhlali Yapan Kişiler
	•	Kaç Kere Çalıştırıldığı

Kullanım Adımları:
	1.	Aşağıdaki komutu çalıştırın:

python3 report.py


	3.	Script çalıştığında ekrana mevcut kampanyaların ID ve isimleri listelenecektir. Örneğin:

Mevcut kampanyalar:
ID: 15 - İsim: Test1
ID: 17 - İsim: Test2
ID: 18 - İsim: Test3
...


	4.	Raporlamak istediğiniz kampanya ID’sini girin. Seçilen kampanyanın timeline verileri, Campaign_Report_ID_<secilen_id>.xlsx dosyası olarak oluşturulacaktır. Konsol çıktısında hangi kampanya ID’sinin işlendiği belirtilecektir.

Kullanım Videosu

Proje kullanımına dair detaylı açıklamaları içeren videoyu aşağıdaki bağlantıdan izleyebilirsiniz:

https://www.linkedin.com/feed/update/urn:li:activity:7289951322726916096/

PhishViz Örnek Videosu

Teknik Detaylar
	•	Dil & Framework: Python 3.13, Flask
	•	Veritabanı: Flask-SQLAlchemy 
	•	Excel Desteği: Pandas, xlsxwriter 
	•	Şablon Düzenleme: CKEditor entegrasyonu
	•	Grafik: Matplotlib (grafiksel raporlama için)
	•	Modern & Responsive Arayüz: Bootstrap

Destek

Eğer bir sorun yaşarsanız, aşağıdaki kanallardan yardım alabilirsiniz:
- **Twitter:** [sefabasnak](https://twitter.com/sefabasnak)
- **LinkedIn:** [linkedin/in/sefabasnak](https://www.linkedin.com/in/sefabasnak)

© 2025 PhishViz. Tüm Hakları Saklıdır.
