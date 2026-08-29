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
* Clone repository or download it and navigate to the project directory
* Create and activate the virtual environmnet
  * Create virtual environment
    ```sh
    python3 -m venv .venv
    ```
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
   * Log in to Google Cloud
     ```sh
     gcloud auth login
     ```
   * Set your active GCP project
     ```sh
     gcloud config set project <project_name>
     ```
   * Enable required GCP APIs
   ```sh
   # Enable required GCP APIs
   gcloud services enable bigquery.googleapis.com run.googleapis.com cloudscheduler.googleapis.com artifactregistry.googleapis.com
   ```
3. Create BigQuery dataset and tables
   * Creating dataset
     ```sh
     bq mk --location=us-central1 --dataset <project_name>:<dataset_name>
     ```
   * Create news headlines table
      ```sh
     bq query 'CREATE TABLE IF NOT EXISTS `<project_name>.<dataset_name>.<table_name>`(ticker STRING, headlines STRING, date DATE, sentiment_score FLOAT 64)'
     ```
   * Create stock prices table
    ```sh
    bq query 'CREATE TABLE IF NOT EXISTS `<project_name>.<dataset_name>.<table_name>` (ticker STRING, date DATE, open FLOAT64, high FLOAT64, low FLOAT64, close FLOAT64, volume INTEGER)'
    ```
   * Create ML predictions table
   ```sh
   bq query 'CREATE TABLE IF NOT EXISTS `<project_name>.<dataset_name>.<table_name>` (ticker STRING, as_of_date DATE, predicted_direction STRING, up_probability FLOAT64, latest_sentiment FLOAT64)'
   ```
   
## Operations Guide

1. Running the ML pipeline Job(Cloud Run)
2. Viewing daily predictions
3. Backfilling any missing sentiment scores
