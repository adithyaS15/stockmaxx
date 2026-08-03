from gnews import GNews
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from google.cloud import bigquery
from datetime import datetime, timedelta

analyzer = SentimentIntensityAnalyzer()
client = bigquery.Client()
table_id = "stockmaxx.stock_warehouse.news_headlines"

google_news = GNews(
        language = 'en',
        country = 'US',
        period = '30d',
        max_results = 30
    )

news = google_news.get_news('NVIDA')
rows = []

for article in results:
    title = article.get('title','').strip()
    pub_date_str = article.get('published date', '')

    try:
        dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S GMT")
        clean_date = dt.strftime("%Y-%m-%d")
    except Exception:
        clean_date = datetime.now().strftime("%Y-%m-%d")

    scores = analyzer.polarity_scores(title)
    compound_score = round(scores['compound'],4)

    rows_to_insert.append({
            "ticker": "NVDA",
            "headlines": title,
            "date": clean_date
        })

print(f"Scraped {len(rows)} news headlines...")

if rows:
    status = client.insert_rows_json(table_id, rows)
    if push:
        print("🟢 Successfully backfilled headlines! 🟢")
    else:
        print(f"🔴 Encountered errors: {status} 🔴")
