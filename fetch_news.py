import json
import warnings
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Suppress unnecessary parsing warnings
warnings.filterwarnings("ignore")

def fetch_ticker_news(search_query: str, ticker_symbol: str) -> list:
    """
    Fetches the latest news headlines from the Google News RSS feed for India.
    Bypasses Yahoo Finance network blocks entirely for clean, instant data.
    """
    # Querying Google News specifically for Indian financial market context
    url = f"https://news.google.com/rss/search?q={search_query}&hl=en-IN&gl=IN&ceid=IN:en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Querying Google News RSS for: '{search_query}'...")

    try:
        # timeout=10 prevents the script from ever freezing up if the connection drops
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error: Failed to fetch data. HTTP Status {response.status_code}")
            return []
    except Exception as e:
        print(f"Network connection failed: {e}")
        return []

    # Parse using the high-performance 'xml' engine we set up earlier
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    if not items:
        print("No articles found matching the search query.")
        return []

    news_records = []
    # Cap it at the top 15 latest news items to keep the prototype payload tight
    for item in items[:15]:
        title = item.find("title").text if item.find("title") else ""
        link = item.find("link").text if item.find("link") else ""
        pub_date_raw = item.find("pubDate").text if item.find("pubDate") else ""

        # Google News titles append the publisher name at the end (e.g., "Headline - Moneycontrol")
        # This split strips that out to give you just the pure headline string
        if " - " in title:
            title = title.rsplit(" - ", 1)[0]

        clean_date = None
        if pub_date_raw:
            try:
                # Formats Google's standard timestamp string into our pipeline's uniform YYYY-MM-DD format
                date_segment = pub_date_raw[:25].strip()
                clean_date = datetime.strptime(date_segment, "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
            except Exception:
                clean_date = None

        if title:
            record = {
                "ticker": ticker_symbol,
                "headline": title.strip(),
                "date": clean_date,
                "link": link.strip()
            }
            news_records.append(record)

    return news_records

if __name__ == "__main__":
    TARGET_TICKER = "RELIANCE.NS"

    # URL-encoded search term to keep headlines tightly focused on the company's equity
    SEARCH_TERM = "RELIANCE+stock"

    news_payload = fetch_ticker_news(SEARCH_TERM, TARGET_TICKER)

    if news_payload:
        print(f"\nSUCCESS: Extracted {len(news_payload)} latest news entries.")
        print("--- Sample News JSON Payload Structure ---")
        print(json.dumps(news_payload[0], indent=4))
