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
from duckduckgo_search import DDGS
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

    try:
        # Fetch the news results using DuckDuckGo Search
        ddgs = DDGS(proxy='socks5://127.0.0.1:9050', timeout=20)  # "tb" is an alias for "socks5://127.0.0.1:9150"
        ddgs_results = ddgs.text(query, region='wt-wt',safesearch='off',backend='html', max_results=350)

        for result in ddgs_results:
            title = result.get("title", "No Title")
            link = result.get("href", None)
            snippet = result.get("body", "No Snippet")

            if link:
                logger.info(f"Found news article: {title}")
                # Extract text from the URL
                text = extract_text_from_url(link)
                if text:
                    # Perform sentiment analysis
                    star_rating, sentiment_label, _ = analyze_sentiment_with_stars(text)
                    if star_rating:
                        result_data = {
                            "title": title,
                            "snippet": snippet,
                            "sentiment": f"{star_rating} ({sentiment_label})",
                            "link": link
                        }
                        results.append(result_data)
                        yield result_data  # Yield results for streaming
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        
    # Save results to JSON file (optional, for backup)
    safe_query = "".join([c if c.isalnum() else "_" for c in query])
    output_file = f"{safe_query}.json"
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to file: {e}")