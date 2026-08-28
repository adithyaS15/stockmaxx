from google.cloud import bigquery
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

# Download VADER lexicon
nltk.download("vader_lexicon", quiet=True)

PROJECT_ID = "stockmaxx"
DATASET_TABLE = "stockmaxx.stock_warehouse.news_headlines"
TEMP_TABLE = "stockmaxx.stock_warehouse.temp_backfill_scores"

client = bigquery.Client(project=PROJECT_ID)
analyzer = SentimentIntensityAnalyzer()

# 1. Fetch NULL rows
print("Fetching unscored headlines...")
fetch_query = f"""
    SELECT ticker, headlines, date
    FROM `{DATASET_TABLE}`
    WHERE sentiment_score IS NULL
"""
df = client.query(fetch_query).to_dataframe()

if df.empty:
    print("No missing sentiment scores found.")
    exit(0)

# 2. Deduplicate in Python to prevent MERGE collisions
df = df.drop_duplicates(subset=["ticker", "headlines", "date"])

print(f"Calculating scores for {len(df)} unique headlines...")

# 3. Compute compound sentiment scores
df["sentiment_score"] = df["headlines"].apply(
    lambda text: analyzer.polarity_scores(str(text))["compound"] if pd.notnull(text) else 0.0
)

# 4. Load scored data into a temporary staging table
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(df, TEMP_TABLE, job_config=job_config).result()

# 5. Merge staging table back into news_headlines and clean up
merge_query = f"""
    MERGE `{DATASET_TABLE}` T
    USING `{TEMP_TABLE}` S
    ON T.ticker = S.ticker AND T.headlines = S.headlines AND T.date = S.date
    WHEN MATCHED THEN
      UPDATE SET T.sentiment_score = S.sentiment_score;

    DROP TABLE IF EXISTS `{TEMP_TABLE}`;
"""

print("Updating BigQuery table...")
client.query(merge_query).result()
print("Backfill complete!")
