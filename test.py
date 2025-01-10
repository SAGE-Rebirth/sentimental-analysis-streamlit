# Function to scrape Google search results using httpx and analyze sentiment
def scrape_and_analyze(query, num_pages=1):
    """
    Scrape Google search results using httpx, analyze sentiment, and save results to a JSON file.
    
    Args:
        query (str): The search query.
        num_pages (int): Number of pages to scrape.
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
            # Build the URL
            params = {"q": query, "start": page * 10, "hl": "en"}
            url = f"https://www.google.com/search?{urllib.parse.urlencode(params)}"
            logging.info(f"Fetching: {url}")

            # Rotate user agent
            headers = {"User-Agent": random.choice(user_agents)}

            # Fetch the page
            response = httpx.get(url, headers=headers)
            response.raise_for_status()
            html = response.text

            if response.status_code == 429:
                logging.warning("Received 429 Too Many Requests. Sleeping for a while...")
                time.sleep(60)  # Sleep for 60 seconds before retrying
                response = httpx.get(url, headers=headers)
                response.raise_for_status()
                html = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')

            # Extract search result links
            for result in soup.select("div.yuRUbf a"):
                link = result.get('href')
                if link:
                    logging.info(f"Found link: {link}")
                    # Extract text from the URL
                    text = extract_text_from_url(link)
                    if text:
                        logging.info(f"Extracted text from {link}")
                        # Perform sentiment analysis
                        star_rating, sentiment_label, _ = analyze_sentiment_with_stars(text)
                        if star_rating:
                            logging.info(f"Analyzed sentiment for {link}: {star_rating} stars, {sentiment_label}")
                            results.append({
                                "search_result": text,
                                "sentiment": f"{star_rating} ({sentiment_label})",
                                "search_result_link": link
                            })

            # Add delay between page requests
            time.sleep(random.randint(5, 10))
        except Exception as e:
            logging.error(f"Error scraping page {page}: {e}")