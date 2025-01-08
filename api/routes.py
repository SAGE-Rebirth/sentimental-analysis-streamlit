from flask import request, jsonify, Response, stream_with_context
from scraper.scraper import scrape_google_news
import threading
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_routes(app):
    @app.route('/start_scraping', methods=['POST'])
    def start_scraping():
        """
        Endpoint to start the scraping process.
        """
        data = request.get_json()
        query = data.get("query")
        num_pages = data.get("num_pages", 1)
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
        
        # Start the scraping process in a separate thread
        try:
            threading.Thread(target=scrape_google_news, args=(query, num_pages)).start()
            logger.info(f"Scraping started for query: {query}")
            return jsonify({"message": "Scraping started", "query": query, "num_pages": num_pages}), 200
        except Exception as e:
            logger.error(f"Error starting scraping: {e}")
            return jsonify({"error": f"Failed to start scraping: {e}"}), 500

    @app.route('/stream_results', methods=['GET'])
    def stream_results():
        """
        Endpoint to stream the results of the scraping process.
        """
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "No search query provided"}), 400
        
        # Create a safe filename from the query
        safe_query = "".join([c if c.isalnum() else "_" for c in query])
        output_file = f"{safe_query}.json"

        def generate():
            try:
                # Stream results as they are scraped
                for result in scrape_google_news(query):
                    yield json.dumps(result) + "\n"
            except Exception as e:
                logger.error(f"Error streaming results for query {query}: {e}")
                yield json.dumps({"error": f"Failed to stream results: {e}"}) + "\n"

        return Response(stream_with_context(generate()), mimetype='application/json')