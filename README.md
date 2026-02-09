
# Cloud Data Pipeline (Polars + PyArrow)

A small data pipeline on the NYC Green Taxi dataset built with **Polars/PyArrow** and orchestrated with **AWS Step Functions (Local)**.
Each pipeline step is implemented as a “Lambda-style” function and executed locally through a lightweight **Flask worker**.

## What it does
Pipeline steps:
1. **Ingest**: loads the raw dataset (Parquet) and writes a staged copy
2. **Transform**: feature engineering + basic data quality / outlier flagging + daily KPI aggregation (includes a per-capita metric)
3. **Store**: writes final outputs as Parquet

Outputs are saved under `out/`.

## Architecture (local)
- **Step Functions Local** (Docker) orchestrates the workflow (sequence + retries)
- **Lambda integration pattern** is used in the state machine (`arn:aws:states:::lambda:invoke`)
- A local **Flask worker** simulates the Lambda invoke endpoint and dispatches to:
  - `lambda_ingest`
  - `lambda_transform`
  - `lambda_store`

State is passed as JSON between steps + persisted via Parquet files in `out/staging/` (S3-like staging).

## Project structure
- `src/lambda_ingest/` – ingest step
- `src/lambda_transform/` – transform + KPI step
- `src/lambda_store/` – store step
- `src/worker/app.py` – local Lambda-style HTTP worker
- `state_machine/pipeline.json` – Step Functions state machine definition

## Local run (from scratch)

### 1) Setup
```bash
cd ~/projects/cloud-data-pipeline
source .venv/bin/activate

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

### 2) Start the worker (lambda simulator)
PYTHONPATH=src python src/worker/app.py

### 3) Start Step Functions Local (Docker)
docker run --rm -it -p 8083:8083 \
  -e LAMBDA_ENDPOINT=http://host.docker.internal:9000/lambda/invoke \
  amazon/aws-stepfunctions-local

### 4) Create the state machine
(new tab)
aws stepfunctions create-state-machine \
  --endpoint-url http://localhost:8083 \
  --name nyc-green-taxi-pipeline \
  --definition file://state_machine/pipeline.json \
  --role-arn arn:aws:iam::123456789012:role/DummyRole

### 5) Run an execution
aws stepfunctions start-execution \
  --endpoint-url http://localhost:8083 \
  --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:nyc-green-taxi-pipeline \
  --input '{"input_path":"data/raw.parquet"}'

### OUTPUT
Final KPI table: out/daily_kpi.parquet
Staging artifacts: out/staging/

### Plots (optional)
This project can generate two quick plots from the final KPI table (saved as images, not interactive windows):
- `out/plots/daily_total_amount.png` (daily total cost over time)
- `out/plots/cost_vs_km.png` (cost vs distance scatter)

Run:
PYTHONPATH=src python src/plots/make_plots.py


## Data sources

- NYC Taxi & Limousine Commission (TLC) Trip Record Data (Green Taxi), Parquet files:
  https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- NYC population reference (used only to compute a per-capita macro indicator):
  U.S. Census Bureau — City and Town Population Totals: 2020-2024 (Vintage 2024):
  https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html

Notes:
- The dataset does not contain "citizen" information. The per-capita metric is an aggregate indicator computed as: total daily green-taxi spend / NYC population.

