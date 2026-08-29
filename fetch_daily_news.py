from datetime import datetime
from google.cloud import bigquery
from gnews import GNews
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
client = bigquery.Client()
TABLE_ID = "stockmaxx.stock_warehouse.news_headlines"

# Ticker to search query mapping
TICKERS = {
    "NVDA": "NVIDIA",
    "AAPL": "Apple stock",
    "GOOGL": "Google Alphabet",
    "META": "Meta Platforms",
    "AMD": "AMD stock",
    "BTC-USD": "Bitcoin",
}

google_news = GNews(language="en", country="US", period="7d", max_results=15)

all_rows = []

for ticker, search_term in TICKERS.items():
    print(f"Fetching news for {ticker}...")
    news = google_news.get_news(search_term)

    for article in news:
        title = article.get("title", "").strip()
        pub_date_str = article.get("published date", "")

        if not title:
            continue

        try:
            dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S GMT")
            clean_date = dt.strftime("%Y-%m-%d")
        except Exception:
            clean_date = datetime.now().strftime("%Y-%m-%d")

        # Guarantee non-null float compound score
        scores = analyzer.polarity_scores(title)
        compound_score = float(round(scores["compound"], 4))

        all_rows.append({
            "ticker": ticker,
            "headlines": title,
            "date": clean_date,
            "sentiment_score": compound_score,
        })

print(f"Scraped {len(all_rows)} total headlines.")

if all_rows:
    status = client.insert_rows_json(TABLE_ID, all_rows)
    if not status:
        print("🟢 Successfully inserted headlines and sentiment scores! 🟢")
    else:
        print(f"🔴 Insertion errors: {status} 🔴")
