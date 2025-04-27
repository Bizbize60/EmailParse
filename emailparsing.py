import requests
from bs4 import BeautifulSoup
import re
from typing import Set, List
import logging
from urllib.parse import urljoin

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('email_scraper.log'), logging.StreamHandler()]
)

class EmailScraper:
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    TIMEOUT = 10
    KEYWORDS = ["info", "bilgi", "iletisim"]
    MAX_EMAILS_THRESHOLD = 10

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.email_set: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page_content(self, url: str) -> str:
        """URL'den içerik çeker"""
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Request error for {url}: {str(e)}")
            return ""

    def extract_emails(self, text: str) -> List[str]:
        """Metinden email adreslerini çıkarır"""
        return re.findall(self.EMAIL_PATTERN, text)

    def clean_emails(self, emails: List[str]) -> List[str]:
        """Email adreslerini temizler"""
        return [re.sub(r'[a-zA-Z]+\d+([a-zA-Z]*)', r'\1', email) for email in emails]

    def process_page(self, url: str):
        """Tek bir sayfayı işler"""
        content = self.fetch_page_content(url)
        if not content:
            return

        emails = self.extract_emails(content)
        cleaned_emails = self.clean_emails(emails)

        # Anahtar kelime kontrolü
        if any(keyword in email for email in cleaned_emails for keyword in self.KEYWORDS):
            self.email_set.update(cleaned_emails)

        # E-posta sayısı eşiği
        if len(cleaned_emails) >= self.MAX_EMAILS_THRESHOLD:
            self.email_set.update(cleaned_emails)
        else:
            self.scrape_links(content)

    def scrape_links(self, content: str):
        """Sayfadaki linkleri tarar"""
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
            url = urljoin(self.base_url, link['href'])
            if url != self.base_url and self.base_url in url:
                self.process_page(url)

    def save_emails(self, filename: str = "emails.txt"):
        """Emailleri dosyaya kaydeder"""
        with open(filename, 'w', encoding='utf-8') as f:
            for email in sorted(self.email_set):
                f.write(f"{email}\n")
        logging.info(f"Toplam {len(self.email_set)} email kaydedildi.")

def main():
    # Örnek kullanım
    scraper = EmailScraper("https://example.com")
    scraper.process_page(scraper.base_url)
    scraper.save_emails()

if __name__ == "__main__":
    main()
