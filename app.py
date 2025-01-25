import streamlit as st
import requests
import json
import pandas as pd
import os

st.title("Web Results Sentiment Analysis")
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL") or "http://localhost:5000"

# Initialize session state for extra keywords
if 'extra_keywords' not in st.session_state:
    st.session_state.extra_keywords = []

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

# Extra keywords section
st.subheader("Additional Keywords")

# Input for new keyword
new_keyword = st.text_input("Enter an additional keyword:", key="new_keyword_input")

# Add keyword button
if st.button("Add Keyword"):
    if new_keyword.strip():
        st.session_state.extra_keywords.append(new_keyword.strip())
        # Clear the input by rerunning the app
        st.rerun()
    else:
        st.warning("Please enter a keyword before adding.")

# Display current keywords
if st.session_state.extra_keywords:
    st.write("**Added Keywords:**")
    for i, keyword in enumerate(st.session_state.extra_keywords):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {keyword}")
        with col2:
            if st.button(f"Remove", key=f"remove_{i}"):
                del st.session_state.extra_keywords[i]
                st.rerun()

    if st.button("Clear All Keywords"):
        st.session_state.extra_keywords = []
        st.rerun()

# Button to start scraping
if st.button("Start Scraping"):
    if not query and not st.session_state.extra_keywords:
        st.error("Please enter a search query or add keywords.")
    else:
        with st.spinner('Scraping in progress...'):
            try:
                # Combine main query and extra keywords
                full_query = query
                if st.session_state.extra_keywords:
                    full_query += " " + " ".join(st.session_state.extra_keywords)

                # Start the scraping process
                response = requests.post(
                    f"{FLASK_BASE_URL}/start_scraping",
                    json={
                        "query": full_query,
                        "base_query": query,
                        "extra_keywords": st.session_state.extra_keywords
                    }
                )
                response.raise_for_status()
                st.success("Scraping started. Streaming results...")

                # Initialize an empty DataFrame to store results
                results_df = pd.DataFrame(columns=["Title", "Snippet", "Sentiment", "Link", "Full_Link"])

                # Create a placeholder for the table
                table_placeholder = st.empty()

                # Stream results in real-time
                response = requests.get(
                    f"{FLASK_BASE_URL}/stream_results",
                    params={
                        "query": full_query,
                        "base_query": query,
                        "extra_keywords": st.session_state.extra_keywords
                    },
                    stream=True
                )
                
                for line in response.iter_lines():
                    if line:
                        result = json.loads(line)
                        # Append the result to the DataFrame
                        new_row = {
                            "Title": result.get("title", "No Title"),
                            "Snippet": result.get("snippet", "No Snippet")[:100] + "..." if result.get("snippet") else "No Snippet",
                            "Sentiment": result.get("sentiment", "No Sentiment"),
                            "Link": result.get("link", "No Link")[:50] + "..." if result.get("link") else "No Link",
                            "Full_Link": result.get("link", "No Link")
                        }
                        results_df = results_df._append(new_row, ignore_index=True)
                        # Update the table in place with truncated link
                        display_df = results_df.drop(columns=["Full_Link"])
                        table_placeholder.dataframe(display_df, width=1000)

                # Export the DataFrame with full links
                st.download_button(
                    label="Export Results",
                    data=results_df.to_csv(index=False).encode('utf-8'),
                    file_name='web_results.csv',
                    mime='text/csv',
                )

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")