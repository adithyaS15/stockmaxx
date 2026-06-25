import json
from datetime import datetime
import requests
from bs4 import BeautifulSoul

def fetch_ticker_news(ticker: str) -> list:
    url = f"https://finance.yahoo.com/rss/headline?s={ticker}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Scraping Yahoo Finances for headlines regarding {ticker}...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch the news. HTTP status code is {response.status_code}")
        return

    soup = BeautifulSoul(response.content, "html.parser")
    items = soup.find_all("item")

    news_records = []
    for item in items:
        title = item.find("title").text if item.find("title") else "nothing"
        pub_date_raw = item.find("pubdate").text if item.find("pubdate") else "nothing"
        pub_date_raw = item.find("link").text if item.find("link") else "nothing"

        clean_date = None
        if pub_date_raw:
            try:
                # Slice the first 25 characters to isolate the standard date-time sequence
                date_segment = pub_date_raw[:25].strip()
                clean_date = datetime.strptime(date_segment, "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
            except Exception:
                # Fallback if an unexpected timestamp format slips through
                clean_date = None

        if title:
            record = {
                "ticker": ticker,
                "headline": title.strip(),
                "date": clean_date,
                "link": link.strip()
            }
            news_records.append(record)

    return news_records

if __name__ == "__main__":
    TARGET_TICKER = "RELIANCE.NS"

    news_payload = fetch_ticker_news(TARGET_TICKER)
