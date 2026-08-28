## 📈 Stockmaxx - A Serverless GCP Market & Sentiment Ingestion Pipeline

Stockmaxx is an end-to-end data engineering and machine learning pipeline hosted on Google Cloud Platform (GCP). It streams real-time stock and cryptocurrency prices alongside financial news headlines, computes VADER natural language sentiment scores, engineers lag and rolling features, and executes daily directional ML predictions stored directly in BigQuery.

## 🚀 Getting Started

### Prerequisites
* Python 3.11+
* Google Cloud SDK (`gcloud` CLI)
* BigQuery CLI(`bq`) enabled
* Key Python dependencies: `google-cloud-bigquery`, `pandas`, `nltk`

### Environment Setup
* Clone repository and navigate to the project directory
* Activate the virtual environmnet
  * For Fish shell
    ```sh
    source .venv/bin/activate.fish
    ```
  * For Bash/Zsh
    ```sh
    source .venv/bin/activate
    ```
* Install the dependencies
  ```sh
  pip install -r requirements.txt
  ```
NOTE: The regular 'requirements.txt' file should be enough to run everything, but if you want the exact replica of the environment, use 'requirements-dev.txt'

