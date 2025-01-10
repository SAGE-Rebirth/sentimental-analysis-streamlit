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

import random
import time
import urllib.parse
import httpx
from bs4 import BeautifulSoup

def scrape_google_news(query):
    """
    Scrape Google News results for a given query until no more results are found.
    """
    results = []
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
    ]

    accept_headers = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=1.0,*/*;q=0.9"
    ]

    accept_language_headers = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-US,en,fr;q=0.8",
        "en-US,en-GB;q=0.9",
        "en-US,en;q=0.9,fr;q=0.8"
    ]

    referer_headers = [
        "https://www.google.com/",
        "https://www.bing.com/",
        "https://www.yahoo.com/",
        "https://news.google.com/",
        "https://www.reddit.com/"
    ]

    connection_headers = [
        "keep-alive",
        "close",
        "keep-alive, Upgrade",
        "Upgrade, keep-alive"
    ]

    page = 0
    while True:
        try:
            # Build the Google News URL
            params = {"q": query, "start": page * 10, "hl": "en"}
            url = f"https://www.google.com/search?{urllib.parse.urlencode(params)}"
            logger.info(f"Fetching: {url}")

            # Select random headers
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": random.choice(accept_headers),
                "Accept-Language": random.choice(accept_language_headers),
                "Referer": random.choice(referer_headers),
                "DNT": "1",
                "Connection": random.choice(connection_headers),
                "Upgrade-Insecure-Requests": "1",
                "TE": "Trailers"
            }

            # Fetch the page
            response = httpx.get(url, headers=headers)
            response.raise_for_status()
            html = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')

            # Extract news results
            page_results = []
            # for result in soup.select("div.yuRUbf a"):
            for result in soup.select("div#search a"):    
                title = result.select_one("h3").get_text(strip=True) if result.select_one('h3') else "No Title"
                link = result.get("href") or None
                source = result.select_one("span.VuuXrf").get_text(strip=True) if result.select_one("span.VuuXrf") else "Unknown Source"
                snippet = result.select_one("div.VwiC3b").get_text(strip=True) if result.select_one("div.VwiC3b") else "No Snippet"

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
                            page_results.append(result_data)
                            yield result_data  # Yield results for streaming

            # If no results are found on the page, break the loop
            if not page_results:
                logger.info("No more results found. Stopping.")
                break

            # Add the page results to the overall results
            results.extend(page_results)

            # Increment the page number
            page += 1

            # Add delay between page requests
            time.sleep(random.randint(5, 15))
        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")
            break
        
    # Save results to JSON file (optional, for backup)
    safe_query = "".join([c if c.isalnum() else "_" for c in query])
    output_file = f"{safe_query}.json"
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to file: {e}")