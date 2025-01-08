import httpx
from readability import Document
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    try:
        response = httpx.get(url)
        response.raise_for_status()
        doc = Document(response.text)
        soup = BeautifulSoup(doc.content(), 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from URL {url}: {e}")
        return None