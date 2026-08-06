import pandas as pd
from google.cloud import bigquery
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

client = bigquery.Client()
analyzer = SentimentIntensityAnalyzer()

target_table = "stockmaxx.stock_warehouse.news_headlines"
staging_table = "stockmaxx.stock_warehouse.temp_sentiment_staging"

print("Fetching headlines missing sentiment scores...")
query = f"""
SELECT ticker, headlines, date
FROM `{target_table}`
WHERE sentiment_score IS NULL
"""
df = client.query(query).to_dataframe()

if df.empty:
    print("No rows need backfilling!")
    exit()

print(f"Computing VADER sentiment scores for {len(df)} headlines in memory...")
# Calculate sentiment in memory across the pandas series
df['sentiment_score'] = df['headlines'].apply(
    lambda h: round(analyzer.polarity_scores(str(h))['compound'], 4)
)

# Format date column as string for seamless staging schema matching
df['date'] = df['date'].astype(str)

print("Uploading batch to BigQuery temporary staging table...")
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",
    schema=[
        bigquery.SchemaField("ticker", "STRING"),
        bigquery.SchemaField("headlines", "STRING"),
        bigquery.SchemaField("date", "STRING"),
        bigquery.SchemaField("sentiment_score", "FLOAT64"),
    ]
)
load_job = client.load_table_from_dataframe(df, staging_table, job_config=job_config)
load_job.result()  # Wait for upload to complete

print("Executing bulk MERGE operation in BigQuery...")
merge_sql = f"""
MERGE `{target_table}` T
USING `{staging_table}` S
ON T.ticker = S.ticker
   AND CAST(T.date AS STRING) = S.date
   AND T.headlines = S.headlines
WHEN MATCHED THEN
  UPDATE SET T.sentiment_score = S.sentiment_score;
"""
client.query(merge_sql).result()

print("Cleaning up staging table...")
client.delete_table(staging_table, not_found_ok=True)

print(f"🟢 Successfully backfilled {len(df)} sentiment scores! 🟢")
