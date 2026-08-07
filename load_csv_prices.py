import pandas as pd
from google.cloud import bigquery
import re # Thank you, UTF-16 encoding

client = bigquery.Client()
table_id = "stockmaxx.stock_warehouse.market_prices"

csv_path = "./data/NVidia_stock_history.csv"
# df = pd.read_csv(csv_path)

try:
    df = pd.read_csv(csv_path)
    if df.columns[0].startswith('_'):
        df = pd.read_csv(csv_path, encoding = 'utf-16')
except exception:
    df = pd.read_csv(csv_path, encoding='utf-16')

# I hate it when datasets have names capitalized. Like, why? And also spaces.
#df.columns = df.columns.str.lower().str.strip().str.replace('','_')

df.columns = [re.sub(r'[^a-zA-Z0-9]','',str(c)).lower() for c in df.columns]


if 'date' not in df.columns:
    print(f"❗ ERROR! Could not parse date column. Columns found: {df.columns.tolist()}")
    exit(1)

df['ticker'] = "NVDA"
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
df['volume'] = df['volume'].astype('int64')

for col in ['open', 'high', 'low', 'close']:
    df[col] = df[col].round(2)

target_columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume'] # No use included adjusted close
df_clean = df[target_columns].copy()

print(f"Uploading {len(df_clean)} rows from CSV to my BigQuery table...")

job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
job = client.load_table_from_dataframe(df_clean, table_id, job_config=job_config)
job.result()

# deduplication
cleanup_sql = f"""
CREATE OR REPLACE TABLE `{table_id}` AS
SELECT DISTINCT ticker, date, open, high, low, close, volume
FROM `{table_id}`
ORDER BY date DESC, ticker;
"""
client.query(cleanup_sql).result()
print("🟢 Local CSV prices have been successfully added to your BQ table! 🟢")

