import yfinance as yf
import pandas as pd
from google.cloud import bigquery

print("Fetching missing NVDA marketprice data...")
nvda = yf.Ticker("NVDA")
df = nvda.history(start="2026-04-13", end="2026-07-20").reset_index()

if df.empty:
	print("🔴 Data retrieval failed. 🔴")
	exit()

df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
df['ticker'] = 'NVDA'
df['open'] = df['Open'].round(2)
df['high'] = df['High'].round(2)
df['low'] = df['Low'].round(2)
df['close'] = df['Close'].round(2)
df['volume'] = df['Volume'].astype(int)

df_final = df[['ticker', 'date', 'open', 'high', 'low', 'close','volume']]

client = bigquery.Client()
table_id = "stockmaxx.stock_warehouse.market_prices"

job_config = bigquery.LoadJobConfig(write_disposition = bigquery.writeDisposition.WRITE_APPEND)

job = client.load_table_from_datafeam(df_final, table_id, job_config)

print("🟢 Successfully backfilled market price gap in BQ! 🟢")



