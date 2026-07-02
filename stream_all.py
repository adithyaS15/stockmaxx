import json
import requests
import yfinance as yf
from datetime import datetime
from bs4 import beautifulsoup4
from google.cloud import pubsub_v1

PROJECT_ID = ""
PRICE_TOPIC = "stockky-price-ingest"
NEWS_TOPIC = "stockky-news-ingest"

ASSET_MATRIX = {
        "AAPL": {"search": "Apple+stock", "type": "stock"}
        "NVDA": {"search": "NVIDIA+stock", "type": "stock"}
        "AMD": {"search": "AMD+stock", "type": "stock"}
        "META": {"search": "Meta+Platforms+stock", "type": "stock"}
        "GOOGL": {"search": "Google+stock", "type": "stock"}
        "BTC-USD": {"search": "Bitcoin+crypto", "type": "crypto"}
    }

def publish_to_cloud(topic_id: str, data_dict: dict, publisher_client, project_id: str):
    try:
        topic_path = publisher_client.topic_path(project_id, topic_id)
        serialized_data = json.dumps(data_dict).encode("utf-8")
        future = publisher_client.publish(topic_path, data=serialized_data)
        return future.result()
    except Exception as e:
        print(f"Cloud Streaming Error: {e}")
        return none

def process_pipeline():
    publisher = pubsub_v1.PublisherClient()

    print(f"=== Starting Multi-Asset Ingestion Pipeline | {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    for ticker, config in ASSET_MATRIX.items():
        print(f"\nProcessing Asset Target: {ticker} ({config['type'].upper()})")

        # --- PHASE A: FETCH & STREAM LATEST PRICE ---
        try:
            stock = yf.Ticker(ticker)
            # Fetching just the last 1 day of intervals to capture the current state
            df = stock.history(period="1d")
            if not df.empty:
                df = df.reset_index()
                row = df.iloc[-1] # Grabs the latest complete trading row

                price_payload = {
                    "ticker": ticker,
                    "date": row["Date"].strftime("%Y-%m-%d") if hasattr(row["Date"], "strftime") else str(row["Date"])[:10],
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"])
                }

                msg_id = publish_to_cloud(PRICE_TOPIC, price_payload, publisher, PROJECT_ID)
                if msg_id:
                    print(f"   ✅ Market metrics successfully streamed to Pub/Sub.")
            else:
                print(f"   ❌ Price Fetch Failed: Empty dataset returned for {ticker}.")
        except Exception as pe:
            print(f"   ❌ Price Extraction Crash on {ticker}: {pe}")

        # --- PHASE B: FETCH & STREAM HEADLINES ---
        url = f"https://news.google.com/rss/search?q={config['search']}&hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")

                news_count = 0
                # Take top 5 headlines per asset to prevent spamming the stream
                for item in items[:5]:
                    title = item.find("title").text if item.find("title") else ""
                    pub_date_raw = item.find("pubDate").text if item.find("pubDate") else ""

                    if " - " in title: title = title.rsplit(" - ", 1)[0]

                    clean_date = None
                    if pub_date_raw:
                        try:
                            clean_date = datetime.strptime(pub_date_raw[:25].strip(), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
                        except:
                            clean_date = datetime.now().strftime("%Y-%m-%d") # Fallback to today

                    if title:
                        news_payload = {
                            "ticker": ticker,
                            "headline": title.strip(),
                            "date": clean_date
                        }
                        msg_id = publish_to_cloud(NEWS_TOPIC, news_payload, publisher, PROJECT_ID)
                        if msg_id: news_count += 1

                print(f"   ✅ Streamed {news_count} news headlines to Pub/Sub.")
            else:
                print(f"   ❌ News Fetch Failed: HTTP Status {response.status_code}")
        except Exception as ne:
            print(f"   ❌ News Scraper Crash on {ticker}: {ne}")

    print("\n=== Pipeline Execution Completed Successfully ===")


if __name__ == "__main__":
    process_pipeline()
