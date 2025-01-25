from flask import request, jsonify, Response, stream_with_context
from scraper.scraper import scrape_google_news
import threading
import json
import os
import logging
from itertools import chain

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_routes(app):
    @app.route('/start_scraping', methods=['POST'])
    def start_scraping():
        """
        Endpoint to start the scraping process with keyword looping and duplicate removal.
        """
        data = request.get_json()
        base_query = data.get("base_query", "")
        extra_keywords = data.get("extra_keywords", [])
        # num_pages = data.get("num_pages", 1)
        
        if not base_query and not extra_keywords:
            return jsonify({"error": "No base query or keywords provided"}), 400
        
        # If no extra keywords, just use the base query
        if not extra_keywords:
            search_queries = [base_query]
        else:
            # Combine base query with each keyword
            search_queries = [f"{base_query} {keyword}" for keyword in extra_keywords]
        
        # Log the search queries
        logger.info(f"Starting scraping for queries: {search_queries}")

        # Start the scraping process in a separate thread
        try:
            threading.Thread(
                target=scrape_multiple_queries,
                args=(search_queries)
            ).start()
            return jsonify({
                "message": "Scraping started",
                "base_query": base_query,
                "extra_keywords": extra_keywords,
                "search_queries": search_queries,
            }), 200
        except Exception as e:
            logger.error(f"Error starting scraping: {e}")
            return jsonify({"error": f"Failed to start scraping: {e}"}), 500

    @app.route('/stream_results', methods=['GET'])
    def stream_results():
        """
        Endpoint to stream the compiled results of all keyword searches with duplicate removal.
        """
        base_query = request.args.get('base_query', "")
        extra_keywords = request.args.getlist('extra_keywords')
        # num_pages = request.args.get('num_pages', 1, type=int)
        
        if not base_query and not extra_keywords:
            return jsonify({"error": "No base query or keywords provided"}), 400

        # Create search queries
        if not extra_keywords:
            search_queries = [base_query]
        else:
            search_queries = [f"{base_query} {keyword}" for keyword in extra_keywords]

        logger.info(f"Streaming results for queries: {search_queries}")

        def generate():
            seen_urls = set()  # Track seen URLs to avoid duplicates
            try:
                for query in search_queries:
                    logger.info(f"Starting scraping for query: {query}")
                    for result in scrape_google_news(query):
                        # Skip if we've already seen this URL
                        if result.get('link') in seen_urls:
                            continue
                        
                        # Add the URL to our seen set
                        seen_urls.add(result.get('link'))
                        
                        # Add metadata about the search
                        keyword = query.replace(base_query, "").strip()
                        result['base_query'] = base_query
                        result['keyword'] = keyword
                        
                        yield json.dumps(result) + "\n"
            except Exception as e:
                logger.error(f"Error streaming results: {e}")
                yield json.dumps({"error": f"Failed to stream results: {e}"}) + "\n"

        return Response(stream_with_context(generate()), mimetype='application/json')

def scrape_multiple_queries(search_queries):
    """
    Helper function to scrape multiple queries and store results.
    """
    seen_urls = set()  # Track seen URLs across all queries
    for query in search_queries:
        try:
            logger.info(f"Scraping query: {query}")
            for result in scrape_google_news(query):
                if result.get('link') not in seen_urls:
                    seen_urls.add(result.get('link'))
                    # Process or store the unique result here
        except Exception as e:
            logger.error(f"Error scraping query {query}: {e}")