

# PhishViz

## Proje Hakkında
PhishViz, GoPhish sonuçlarını grafiksel sonuçlara çevirip raporlamaya yardımcı olmak için geliştirilmiş bir sosyal mühendislik raporlama uygulamasıdır. Bu proje, güvenlik testlerinde kullanılan phishing şablonlarının oluşturulmasını, düzenlenmesini ve raporlanmasını kolaylaştırmayı amaçlar. Kullanıcılar, müşteri bilgilerini ekleyebilir, hazır şablonlar üzerinde çalışabilir ve verileri Excel formatında indirebilir.

**Önemli Not:**  
report.py içerisinde 7. satırı güncellemeniz gerekmektedir 
GoPhish API URL’si projenizde aşağıdaki gibi kullanılmaktadır:  
`API_URL = "https://gophish-server:3333/api/campaigns/?api_key=api_key"`

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
	1. **Sanal Ortam Oluşturma:**
   	
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux/MacOS için
   # veya
   venv\Scripts\activate       # Windows için

	2.	Gereksinimlerin Yüklenmesi:
	Projeyi çalıştırmak için gerekli bağımlılıklar requirements.txt dosyasında belirtilmiştir. Aşağıdaki komut ile bağımlılıkları yükleyin:

	pip install -r requirements.txt


	3.	Uygulamayı Başlatma:
	Uygulamanın ana arayüzünü başlatmak için:

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

report.py aracı, GoPhish API’sinden kampanya verilerini çekerek kullanıcıya mevcut kampanyaların ID ve isimlerini listeler. Kullanıcı, listeden raporlamak istediği kampanya ID’sini seçer. Seçilen kampanyanın timeline verileri aşağıdaki sütunlara göre Excel dosyasına aktarılır:
	•	Mail Gönderilen Kişiler
	•	Maili Okuyan Kişiler
	•	Mail Okuma Tarih ve Saati
	•	Linke Tıklayan Kişiler
	•	Veri İhlali Yapan Kişiler
	•	Kaç Kere Çalıştırıldığı

Kullanım Adımları:
	1.	Terminalde sanal ortamınızı aktive edin ve ardından:

python3 report.py


	2.	Script çalıştığında ekrana mevcut kampanyaların ID ve isimleri listelenecektir. Örneğin:

Mevcut kampanyalar:
ID: 15 - İsim: Copy of test
ID: 17 - İsim: Test3
ID: 18 - İsim: Copy of Test3
...


	3.	Sizden raporlamak istediğiniz kampanya ID’sini girmeniz istenecek. İlgili kampanya seçildikten sonra, rapor dosyası Campaign_Report_ID_<secilen_id>.xlsx olarak oluşturulacaktır. Konsol çıktısında da hangi kampanya ID’sinin işlendiği belirtilecektir.

Videolu Dökümantasyon

Proje ve report.py kullanımına dair detaylı açıklamaları içeren videoyu GitHub deposunda izleyebilirsiniz:
PhishViz Örnek Videosu

Teknik Detaylar
	•	Dil & Framework: Python 3.13, Flask
	•	Veritabanı: Flask-SQLAlchemy (opsiyonel kullanım)
	•	Excel Desteği: Pandas, xlsxwriter (ve/veya openpyxl)
	•	Şablon Düzenleme: CKEditor entegrasyonu
	•	Grafik: Matplotlib (grafiksel raporlama için)
	•	Modern & Responsive Arayüz: Bootstrap

© 2025 PhishViz. Tüm Hakları Saklıdır.
