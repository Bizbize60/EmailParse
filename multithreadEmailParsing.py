import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# SSL uyarılarını bastır
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

visited_links = set()
visited_lock = threading.Lock()
file_lock = threading.Lock()
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def requestOfUrl(url):
    print(f"\n[+] Ana Sayfa İşleniyor: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        getemail(response.text, url)
    except Exception as e:
        print(f"[!] Hata oluştu (ana sayfa): {e}")


def getemail(content, base_url):
    emailset = set()

    soup = BeautifulSoup(content, 'html.parser')

    # mailto linklerini çıkar
    for link in soup.find_all('a', href=True):
        href = link['href'].strip()
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").strip()
            emailset.add(email)
            print(f"[✓] Mailto: {email}")

    # sayfa içinden direkt mailler
    emails = re.findall(email_pattern, content)
    for email in emails:
        emailset.add(email)

    # Eğer az mail varsa alt linklere geç
    if len(emailset) < 10:
        links = [
            urljoin(base_url, link['href'])
            for link in soup.find_all('a', href=True)
            if not link['href'].startswith("mailto:")
        ]
        # çoklu iş parçacığı ile alt sayfalardaki mailleri al
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_sub_emails, url) for url in links]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    emailset.update(result)

    # Dosyaya kaydet
    with file_lock:
        with open("tryemails.txt", 'a', encoding='utf-8') as f:
            for email in emailset:
                f.write(email + '\n')

    print(f"[✔] Toplam {len(emailset)} e-posta kaydedildi.")


def fetch_sub_emails(url):
    with visited_lock:
        if url in visited_links:
            return None
        visited_links.add(url)

    try:
        print(f"→ Alt Sayfa: {url}")
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        sub_emails = set(re.findall(email_pattern, response.text))
        for mail in sub_emails:
            print(f"    [✓] {mail}")
        return sub_emails
    except Exception as e:
        print(f"    [!] Alt sayfa bağlantı hatası: {e}")
        return None


# Ana URL listesi
urls = [
    "https://www.sasad.org.tr/uyelerimiz",
    "https://www.ostimsavunma.org/firma-arsiv",
    "https://www.hukd.org.tr/uyelerimiz",
    "https://www.htk.org.tr/firma-arsiv",
    "https://www.medikalkume.com/firma-arsiv?search=&companycategory=4",
    "https://basdec.org/kume-uyeleri.html"
]

for url in urls:
    requestOfUrl(url)
