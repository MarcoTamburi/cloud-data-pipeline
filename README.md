
# Cloud Data Pipeline (Polars + PyArrow)

Short project to ingest -> transform -> store data (lambda style).

## Setup
pythpython3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Smoke test
python src/smoke_test.py


## Data sources

- NYC Taxi & Limousine Commission (TLC) Trip Record Data (Green Taxi), Parquet files:
  https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- NYC population reference (used only to compute a per-capita macro indicator):
  U.S. Census Bureau — City and Town Population Totals: 2020-2024 (Vintage 2024):
  https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html

Notes:
- The dataset does not contain "citizen" information. The per-capita metric is an aggregate indicator computed as: total daily green-taxi spend / NYC population.

