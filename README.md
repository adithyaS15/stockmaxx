## Stockmaxx - A Serverless GCP Market & Sentiment Ingestion Pipeline

Stockmaxx is an end-to-end data engineering pipeline hosted on Google Cloud Platform (GCP). It streams real-time stock prices and financial news headlines, performs VADER natural language sentiment analysis, and stores the analytics-ready data in BigQuery for historical correlation analysis.

## 🏗️ Architecture

[ Cloud Scheduler ] ➔ (4hr Clock Trigger)
│
▼
[ Cloud Functions Engine ]
(Python 3.11)
│
┌─────────────┴─────────────┐
▼                           ▼
(Market Price Data)        (News Headlines Scraper)
│                           │
└─────────────┬─────────────┘
▼
[ Pub/Sub Topic ]
│
(BigQuery Subscription)
│
▼
[ BigQuery Data Warehouse ]
├── market_prices (OHLCV)
└── news_headlines (Sentiments)

## 🚀 Getting Started

### Prerequisites
* Python 3.11+
* Google Cloud SDK (`gcloud` CLI)
* Access to a GCP Project with BigQuery, Pub/Sub, and Cloud Functions enabled

### 1. Environment Setup

Clone the repository and set up your virtual environment:

```fish
git clone [https://github.com/adithyaS15/stockmaxx.git](https://github.com/adithyaS15/stockmaxx.git)
cd stockmaxx

# Create and activate virtual environment (Fish Shell)
python3 -m venv .venv
source .venv/bin/activate.fish

# Install dependencies
pip install -r requirements.txt
