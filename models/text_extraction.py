import httpx
from readabilipy import simple_json_from_html_string

def extract_text_from_url(url):
    """
    Extracts readable text content from a given URL using ReadabiliPy.

    Args:
        url (str): The URL of the web page to extract text from.

    Returns:
        str: Extracted text content as a single string, or None if extraction fails.
    """
    try:
        # Fetch the web page
        response = httpx.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Extract readable content using ReadabiliPy
        article = simple_json_from_html_string(response.text, use_readability=True)

        # Extract text from the readable content
        if article and "plain_text" in article:
            # Combine all text into a single string
            combined_text = " ".join([item["text"] for item in article["plain_text"] if isinstance(item, dict) and "text" in item])
            return combined_text
        else:
            print(f"No readable content found for URL {url}")
            return None
    except Exception as e:
        print(f"Error extracting text from URL {url}: {e}")
        return None