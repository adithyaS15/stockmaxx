import pandas as pd
import numpy as np
from datetime import datetime
from google.cloud import bigquery
from sklearn.ensemble import RandomForestClassifier

# I wish I had this stupid extension before. Would've made it so much easier
from main import PROJECT_ID

PROJECT_ID = "stockmaxx"
DATASET_ID = "stock_warehouse"
SOURCE_VIEW = f"{PROJECT_ID}.{DATASET_ID}.daily_asset_summary"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.ml_predictions"

client = bigquery.Client(project=PROJECT_ID)

def fetch_data() -> pd.DataFrame:
    print("Fetching daily summary history from BQ...")
    query = f"""
    SELECT ticker, date, close_price, daily_return_pct, volume, average_sentiment_score, headline_count
    FROM `{SOURCE_VIEW}` ORDER BY ticker, date ASC
    """

    df = client.query(query).to_dataframe()
    df["date"] = pd.to_datetime(df["date"])
    return df

def engineer_features(df: pd.DataFrame) -> pd.DateFrame: 
    print("Engineering lag features and rolling sentiment indicators...")
    df = df.sort_values(by=["ticker", "date"]).reset_index(drop=True)

    # If tomorrow's price will be higher than today's
    df["next_close"] = df.groupby("ticker")["close_price"].shift(-1)
    df["target"] = (df["next_close"] > df["close_price"]).astype(float)

    df.loc[df["next_close"].isna(), "target"] = np.nan

    # Lag features, price and sentiment memory
    df["return_lag_1"] = df.groupby("ticker")["daily_return_pct"].shift(1)
    df["return_lag_2"] = df.groupby("ticker")["daily_return_pct"].shift(2)

    df["sentiment_lag_1"] = df.groupby("ticker")["avg_sentiment_score"].shift(1)
    df["sentiment_lag_2"] = df.groupby("ticker")["avg_sentiment_score"].shift(2)

    # Rolling momentum indicators
    df["sentiment_3d_avg"] = df.groupby("ticker")["avg_sentiment_score"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df["volatility_5d"] = df.groupby("ticker")["daily_return_pct"].transform(lambda x: x.rolling(5, min_periods=2).std()).fillna(0)
    df["price_5d_sma"] = df.groupby("ticker")["close_price"].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df["price_to_sma_ratio"] = df["close_price"] / df["price_5d_sma"]

    return df

def train_and_predict(df: pd.DataFrame):
    feature_cols = [
        "daily_return_pct", "avg_sentiment_score", "headline_count",
        "return_lag_1", "return_lag_2", "sentiment_lag_1", "sentiment_lag_2",
        "sentiment_3d_avg", "volatility_5d", "price_to_sma_ratio"
    ]

    # cleaning rows
    cleaned_df = df.dropna(subset=feature_cols).copy()

    # training time
    train_date = cleaned_df.dropna(subset=["target"]).copy()

    #inference set
    inference_date = cleaned_df.groupby("ticker").last().reset_index()

    print(f"Training set size: {len(train_data)} rows across all tickers.")
    
    X_train = train_data[feature_cols]
    y_train = train_data["target"].astype(int)

    # Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # Generate predictions for latest date
    X_inference = inference_data[feature_cols]
    probabilities = model.predict_proba(X_inference)[:, 1] # Probability of "UP"

    predictions = []
    for idx, row in inference_data.iterrows():
        prob_up = round(float(probabilities[idx]), 4)
        direction = "UP" if prob_up >= 0.50 else "DOWN"
        
        predictions.append({
            "ticker": row["ticker"],
            "as_of_date": row["date"].strftime("%Y-%m-%d"),
            "predicted_direction": direction,
            "up_probability": prob_up,
            "close_price": float(row["close_price"]),
            "latest_sentiment": float(row["avg_sentiment_score"]),
            "model_version": "v1.0-RandomForest",
            "created_at": datetime.utcnow().isoformat()
        })

    return pd.DataFrame(predictions)

def save_predictions_to_bigquery(pred_df: pd.DataFrame):
    print(f"Writing {len(pred_df)} predictions to BigQuery table `{TARGET_TABLE}`...")
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND", # Appends daily predictions over time
        schema=[
            bigquery.SchemaField("ticker", "STRING"),
            bigquery.SchemaField("as_of_date", "DATE"),
            bigquery.SchemaField("predicted_direction", "STRING"),
            bigquery.SchemaField("up_probability", "FLOAT"),
            bigquery.SchemaField("close_price", "FLOAT"),
            bigquery.SchemaField("latest_sentiment", "FLOAT"),
            bigquery.SchemaField("model_version", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
        ]
    )

    job = client.load_table_from_dataframe(pred_df, TARGET_TABLE, job_config=job_config)
    job.result()
    print("🟢 Prediction run completed successfully!")

if __name__ == "__main__":
    raw_df = fetch_data()
    engineered_df = engineer_features(raw_df)
    predictions_df = train_and_predict(engineered_df)
    
    print("\n--- Model Predictions Generated ---")
    print(predictions_df[["ticker", "as_of_date", "predicted_direction", "up_probability", "latest_sentiment"]])
    
    save_predictions_to_bigquery(predictions_df)
    