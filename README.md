## 📈 Stockmaxx - A Serverless GCP Market & Sentiment Ingestion Pipeline

Stockmaxx is an end-to-end data engineering and machine learning pipeline hosted on Google Cloud Platform (GCP). It streams real-time stock and cryptocurrency prices alongside financial news headlines, computes VADER natural language sentiment scores, engineers lag and rolling features, and executes daily directional ML predictions stored directly in BigQuery.

Additional modules include: 
- [x] ML model for 'prediction' 
- [ ] Dashboard  
- [ ] Congressional trading tracker - Ingesting US senate financial disclosures

## 🚀 Getting Started

### Prerequisites
* Python 3.11+
* Google Cloud SDK (`gcloud` CLI)
* BigQuery CLI(`bq`) enabled
* Key Python dependencies: `google-cloud-bigquery`, `pandas`, `nltk`

### Environment Setup
* Clone repository and navigate to the project directory
* Create and activate the virtual environmnet
  * For Fish shell activation
    ```sh
    source .venv/bin/activate.fish
    ```
  * For Bash/Zsh activation
    ```sh
    source .venv/bin/activate
    ```
* Install the dependencies
  ```sh
  pip install -r requirements.txt
  ```
NOTE: The regular 'requirements.txt' file should be enough to run everything, but if you want the exact replica of the environment, use 'requirements-dev.txt'

### GCP Setup

1. GCP Project and API activation
   ```sh
   # Log in to Google Cloud
   gcloud auth login

   # Set your active GCP project
   gcloud config set project <project_name>

   # Enable required GCP APIs
   gcloud services enable bigquery.googleapis.com run.googleapis.com cloudscheduler.googleapis.com    artifactregistry.googleapis.com
   ```
2. Create BigQuery dataset and tables

