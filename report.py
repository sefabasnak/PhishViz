import sys
import requests
import xlsxwriter
import json
from datetime import datetime

API_URL = "https://gophish-server:3333/api/campaigns/?api_key=API_KEY"

def format_timestamp(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.rstrip("Z"))
        return dt.strftime("%d.%m.%Y - %H:%M:%S")
    except Exception:
        return iso_str

def get_campaign_by_id(campaigns, target_id):
    for camp in campaigns:
        if camp.get("id") == target_id:
            return camp
    return None

def process_campaign(campaign):
    timeline = campaign.get("timeline", [])
    
    groups = {}
    for event in timeline:
        email = event.get("email")
        
        if not email:
            continue
        if email not in groups:
            groups[email] = {"opens": [], "clicks": [], "submits": [], "total": 0}
        
        groups[email]["total"] += 1

        message = event.get("message", "")
        event_time = event.get("time", "")
        if message == "Email Opened":
            groups[email]["opens"].append(event_time)
        elif message == "Clicked Link":
            
            try:
                details = json.loads(event.get("details", ""))
                ip = details.get("browser", {}).get("address", "")
            except Exception:
                ip = ""
            groups[email]["clicks"].append(ip)
        elif message == "Submitted Data":
            groups[email]["submits"].append(email)
    return groups

def generate_excel_report(groups, campaign_id, output_filename=None):
    
    if not output_filename:
        output_filename = f"Campaign_Report_ID_{campaign_id}.xlsx"
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet("Rapor")

    
    headers = [
        "Mail Gönderilen Kişiler",
        "Maili Okuyan Kişiler",
        "Mail Okuma Tarih ve Saati",
        "Linke Tıklayan Kişiler",
        "Veri İhlali Yapan Kişiler",
        "Kaç Kere Çalıştırıldığı"
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    row = 1
    for email, data in groups.items():
        mail_gonderilen = email
        mail_okuyan = email if data["opens"] else ""
        mail_okuma_tarihi = format_timestamp(data["opens"][0]) if data["opens"] else ""
        linke_tiklayan = data["clicks"][0] if data["clicks"] else ""
        veri_ihlali = email if data["submits"] else ""
        calistirilma = data["total"]
        values = [mail_gonderilen, mail_okuyan, mail_okuma_tarihi, linke_tiklayan, veri_ihlali, calistirilma]
        for col, val in enumerate(values):
            worksheet.write(row, col, val)
        row += 1

    workbook.close()
    print(f"Excel raporu '{output_filename}' (Kampanya ID: {campaign_id}) olarak başarıyla oluşturuldu.")

def main():
    
    print("API'den kampanyalar çekiliyor...")
    response = requests.get(API_URL, verify=False)
    if response.status_code != 200:
        print(f"API isteği başarısız oldu: {response.status_code}")
        sys.exit(1)
    campaigns = response.json()

    if not campaigns:
        print("Hiç kampanya bulunamadı.")
        sys.exit(1)

    
    print("Mevcut kampanyalar:")
    for camp in campaigns:
        print(f"ID: {camp.get('id')} - İsim: {camp.get('name')}")

    
    try:
        target_id = int(input("Raporlamak istediğiniz kampanya ID'sini giriniz: "))
    except ValueError:
        print("Geçerli bir sayı girmediniz.")
        sys.exit(1)

    campaign = get_campaign_by_id(campaigns, target_id)
    if not campaign:
        print(f"ID {target_id} olan kampanya bulunamadı.")
        sys.exit(1)

    groups = process_campaign(campaign)
    generate_excel_report(groups, target_id)

if __name__ == "__main__":
    main()
