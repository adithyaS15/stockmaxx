import json
from datetime import datetime
import yfinance as yf

def fetch_historical_data(ticker: str, period: str = "2y") -> list:
    print(f"Retrieving {ticker} information for {period}...")

    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        print(f"No data retrieved for {ticker}, ensure the symbol is accurate.")
        return []

    df = df.reset_index()

    records = []
    for _, row in df.iterrows():
        record = {
            "ticker": ticker,
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        }
        records.append(record)

    return records

if __name__ == "__main__":  # Added missing colon here!
    TARGET_TICKER = "RELIANCE.NS"

    historical_records = fetch_historical_data(TARGET_TICKER, period='2y')

    if historical_records:
        print(f"\n Success! Extracted {len(historical_records)} daily market rows")
        print(json.dumps(historical_records[-1], indent=4))
