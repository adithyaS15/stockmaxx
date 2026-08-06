from google.cloud import bigquery
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

client = bigquery.Client()
analyzer = SentimentIntensityAnalyzer()
table_id = "`stockmaxx.stock_warehouse.news_headlines`"

select_query = f"""SELECT ticker, headlines, date FROM {table_id} WHERE sentiment_score IS NULL"""

rows = list(client.query(select_query).result())

print(f"Found {len(rows)} headlines to backfill")

updated_count = 0

for row in rows:
    headline = row["headlines"]
    ticker = row["ticker"]
    date = str(row["date"])

    scores = analyzer.polarity_scores(headline)
    compound_score = round(scores["compound"], 4)
    # safe_headline = headline.replace("'", "\\'")

    update_query = f"""
    UPDATE {table_id} SET sentiment_score = @sentiment_score WHERE ticker = @ticker AND date = @date AND headlines = @headlines
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("sentiment_score", "FLOAT64", compound_score),
            bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
            bigquery.ScalarQueryParameter("date", "STRING", date),
            bigquery.ScalarQueryParameter("headlines", "STRING", headline),
        ]
    )

    client.query(update_query, job_config=job_config).result()
    updated_count += 1

print(f"🟢 Successfully updated {updated_count} headlines with sentiment scores! 🟢")
