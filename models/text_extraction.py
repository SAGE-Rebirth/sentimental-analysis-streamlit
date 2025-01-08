import httpx
from readability import Document
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    """
    Extracts readable text content from a given URL.

    Args:
        url (str): The URL of the web page to extract text from.

    Returns:
        str: Extracted text content, or None if extraction fails.
    """
    try:
        # Fetch the web page
        response = httpx.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content using Readability
        doc = Document(response.text)
        readable_html = doc.summary()

        # Extract text from the readable HTML using BeautifulSoup
        soup = BeautifulSoup(readable_html, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])

        return text
    except Exception as e:
        print(f"Error extracting text from URL {url}: {e}")
        return None