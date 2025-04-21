import requests
from bs4 import BeautifulSoup
import re

def requestOfUrl(url):
    try:
        content = requests.get(url, timeout=10)  # 10 saniye zaman aşımı
        getemail(content.text, url)
    except Exception as e:
        print(f"Hata oluştu: {e}")

def getemail(content, anawebsayfasi):
    emailset = set()
    emailcounter = 0
    pure_emails = []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    x = re.split(r"\s", content)
    y = "  ".join(x)

    emails = re.findall(email_pattern, y)
    cleaned_emails = [re.sub(r'[a-zA-Z]+\d+([a-zA-Z]*)', r'\1', email) for email in emails]

    for email in cleaned_emails:
        pure_emails.append(email)

    for i in pure_emails:
        if "info" in i or "bilgi" in i or "iletisim" in i:
            emailset.add(i)
            emailcounter += 1

    if emailcounter >= 10:
        for i in pure_emails:
            emailset.add(i)
            print(i)
    else:
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a'):
            urls = str(link.get('href'))
            index = urls.find(".com")
            if index > 0:
                newurls = urls[:index+4]
                if newurls not in anawebsayfasi:
                    try:
                        context = requests.get(urls, timeout=10)
                        emails = re.findall(email_pattern, context.text)
                        for i in emails:
                            emailset.add(i)
                            print(i)
                    except Exception as e:
                        print(f"Bağlantı hatası: {e}")

    with open("emails.txt", 'a') as file:  # Emailleri bir dosyaya kaydet
        for email in emailset:
            file.write(email + "\n")

# URL'leri sırayla işlemek için çağır
urls = [
    "https://odtuteknokent.com.tr/tr/firmalar/tum-firmalar.php",
    "https://asoteknopark.com.tr/?page_id=1606",
    "https://ankarateknokent.com/firmalar-portfolio/",
    "https://www.gaziteknopark.com.tr/allcompany",
    "https://www.teknoparkankara.com.tr/Firmalar.html",
    "https://ostimteknopark.com.tr/tr/firmalar-119",
    "https://www.hacettepeteknokent.com.tr/tr/firma_rehberi/bilgisayar_ve_iletisim_teknolojileri-16",
    "https://www.hacettepeteknokent.com.tr/tr/firma_rehberi/elektronik-17",
    "https://www.cyberpark.com.tr/firma-arsiv"
]

for url in urls:
    requestOfUrl(url)
