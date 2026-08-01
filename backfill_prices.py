import yfinance as yf
import pandas as pd
from google.cloud import bigquery

print("Fetching missing NVDA marketprice data...")
nvda = yf.Ticker("NVDA")
df = nvda.history(start="2026-04-13", end="2026-07-20").reset_index()

if df.empty:
	print("Data retrieval failed.")
	exit()


