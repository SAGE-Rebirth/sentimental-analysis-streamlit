import httpx
from bs4 import BeautifulSoup
import random
import time
import json
import os
import logging
import urllib.parse
from models.text_extraction import extract_text_from_url
from models.sentiment_analysis import analyze_sentiment_with_stars

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_google_news(query, num_pages=1):
    """
    Scrape Google News results for a given query.
    """
    results = []
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    ]

    for page in range(num_pages):
        try:
            # Build the Google News URL
            params = {"q": query, "tbm": "nws", "start": page * 10, "hl": "en"}
            url = f"https://www.google.com/search?{urllib.parse.urlencode(params)}"
            logger.info(f"Fetching: {url}")

            # Rotate user agent
            headers = {"User-Agent": random.choice(user_agents)}

            # Fetch the page
            response = httpx.get(url, headers=headers)
            response.raise_for_status()
            html = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')

            # Extract news results
            for result in soup.select("div.SoaBEf"):
                title = result.select_one("div.MBeuO").get_text(strip=True) if result.select_one("div.MBeuO") else "No Title"
                link = result.find("a")["href"] if result.find("a") else None
                source = result.select_one("div.MgUUmf.NUnG9d").get_text(strip=True) if result.select_one("div.MgUUmf.NUnG9d") else "Unknown Source"
                snippet = result.select_one("div.GI74Re.nDgy9d").get_text(strip=True) if result.select_one("div.GI74Re.nDgy9d") else "No Snippet"

                if link:
                    logger.info(f"Found news article: {title} from {source}")
                    # Extract text from the URL
                    text = extract_text_from_url(link)
                    if text:
                        # Perform sentiment analysis
                        star_rating, sentiment_label, _ = analyze_sentiment_with_stars(text)
                        if star_rating:
                            result_data = {
                                "title": title,
                                "source": source,
                                "snippet": snippet,
                                "sentiment": f"{star_rating} ({sentiment_label})",
                                "link": link
                            }
                            results.append(result_data)
                            yield result_data  # Yield results for streaming

            # Add delay between page requests
            time.sleep(random.randint(5, 10))
        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")

    # Save results to JSON file (optional, for backup)
    safe_query = "".join([c if c.isalnum() else "_" for c in query])
    output_file = f"{safe_query}.json"
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to file: {e}")