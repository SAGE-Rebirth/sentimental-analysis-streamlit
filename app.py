import streamlit as st
import requests
import json
import pandas as pd
import os

st.title("Web Results Sentiment Analysis")
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL") or "http://localhost:5000"

# Sample search queries
sample_queries = [
    "Maha Kumbh Prayagraj 2025 scam fraud threat theft attack mis-management",
    "Climate change impact on agriculture",
    "Latest technology trends 2023",
    "COVID-19 vaccine effectiveness",
    "Artificial intelligence in healthcare"
]

# Dropdown for sample search queries
query = st.selectbox("Select a sample search query or enter your own:", [""] + sample_queries)

# Input box for user input search query
user_query = st.text_input("Or enter your own search query:")

# Use the user input if provided
if user_query:
    query = user_query

# Input box for number of pages to scrape
num_pages = st.number_input("Enter the number of pages to scrape:", min_value=1, max_value=100, value=1)

# Button to start scraping
if st.button("Start Scraping"):
    if not query:
        st.error("Please enter a search query.")
    else:
        with st.spinner('Scraping in progress...'):
            try:
                # Start the scraping process
                response = requests.post(f"{FLASK_BASE_URL}/start_scraping", json={"query": query, "num_pages": num_pages})
                response.raise_for_status()
                st.success("Scraping started. Streaming results...")

                # Initialize an empty DataFrame to store results
                results_df = pd.DataFrame(columns=["Title", "Source", "Snippet", "Sentiment", "Link"])

                # Create a placeholder for the table
                table_placeholder = st.empty()

                # Stream results in real-time
                response = requests.get(f"{FLASK_BASE_URL}/stream_results?query={query}", stream=True)
                for line in response.iter_lines():
                    if line:
                        result = json.loads(line)
                        # Append the result to the DataFrame
                        new_row = {
                            "Title": result.get("title", "No Title"),
                            "Source": result.get("source", "Unknown Source"),
                            "Snippet": result.get("snippet", "No Snippet")[:100] + "..." if result.get("snippet") else "No Snippet",  # Truncate snippet
                            "Sentiment": result.get("sentiment", "No Sentiment"),
                            "Link": result.get("link", "No Link")[:50] + "..." if result.get("link") else "No Link"  # Truncate link
                        }
                        results_df = results_df._append(new_row, ignore_index=True)
                        # Update the table in place
                        table_placeholder.dataframe(results_df, width=1000)  # Adjust width as needed

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")