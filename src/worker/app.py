from flask import Flask, request, jsonify
import polars as pl

from lambda_ingest.handler import ingest, IngestConfig
from lambda_transform.handler import add_features_and_flag_outliers, daily_kpis
from lambda_store.handler import store_outputs, StoreConfig

app = Flask(__name__)

# Staging area to simulate S3 between steps
STAGING_DIR = "out/staging"
RAW_PATH_DEFAULT = "data/raw.parquet"
INGEST_PATH = f"{STAGING_DIR}/ingested.parquet"
TRANSFORM_PATH = f"{STAGING_DIR}/transformed.parquet"
KPI_PATH = f"{STAGING_DIR}/daily_kpi.parquet"

def ensure_dirs():
    import os
    os.makedirs(STAGING_DIR, exist_ok=True)

@app.post("/ingest")
def ingest_route():
    ensure_dirs()
    payload = request.get_json(silent=True) or {}
    input_path = payload.get("input_path", RAW_PATH_DEFAULT)

    df = ingest(IngestConfig(input_path=input_path))
    df.write_parquet(INGEST_PATH)

    return jsonify({
        "status": "ok",
        "input_path": input_path,
        "ingest_path": INGEST_PATH,
        "rows": df.height,
        "cols": df.width
    })

@app.post("/transform")
def transform_route():
    ensure_dirs()
    payload = request.get_json(silent=True) or {}
    ingest_path = payload.get("ingest_path", INGEST_PATH)
    nyc_population = int(payload.get("nyc_population", 8_478_072))
    outlier_threshold = float(payload.get("outlier_threshold", 0.15))

    df = pl.read_parquet(ingest_path)
    df_t = add_features_and_flag_outliers(df)
    kpi = daily_kpis(df_t, nyc_population=nyc_population)

    df_t.write_parquet(TRANSFORM_PATH)
    kpi.write_parquet(KPI_PATH)

    bad_days = (
        kpi.filter(pl.col("outlier_rate") > outlier_threshold)
           .select(["day", "outlier_rate", "trips_count"])
    )

    return jsonify({
        "status": "ok",
        "ingest_path": ingest_path,
        "transform_path": TRANSFORM_PATH,
        "kpi_path": KPI_PATH,
        "days_total": kpi.height,
        "days_excluded": bad_days.height
    })

@app.post("/store")
def store_route():
    ensure_dirs()
    payload = request.get_json(silent=True) or {}
    kpi_path = payload.get("kpi_path", KPI_PATH)

    kpi = pl.read_parquet(kpi_path)

    paths = store_outputs(
        daily_kpi=kpi,
        df_clean=None,
        cfg=StoreConfig(output_dir="out", write_clean_trips=False)
    )

    return jsonify({
        "status": "ok",
        "stored": paths
    })
@app.post("/lambda/invoke")
def lambda_invoke():
    """
    Minimal Lambda Invoke adapter:
    expects JSON like { "FunctionName": "ingest", "Payload": {...} }
    returns JSON like { "StatusCode": 200, "Payload": {...} }
    """
    req = request.get_json(force=True)
    fn = req.get("FunctionName")
    payload = req.get("Payload", {}) or {}

    if fn == "ingest":
        # reuse the same logic as /ingest
        payload = payload or {}
        input_path = payload.get("input_path", RAW_PATH_DEFAULT)
        df = ingest(IngestConfig(input_path=input_path))
        ensure_dirs()
        df.write_parquet(INGEST_PATH)
        out = {
            "status": "ok",
            "input_path": input_path,
            "ingest_path": INGEST_PATH,
            "rows": df.height,
            "cols": df.width
        }

    elif fn == "transform":
        ensure_dirs()
        ingest_path = payload.get("ingest_path", INGEST_PATH)
        nyc_population = int(payload.get("nyc_population", 8_478_072))
        outlier_threshold = float(payload.get("outlier_threshold", 0.15))

        df = pl.read_parquet(ingest_path)
        df_t = add_features_and_flag_outliers(df)
        kpi = daily_kpis(df_t, nyc_population=nyc_population)

        df_t.write_parquet(TRANSFORM_PATH)
        kpi.write_parquet(KPI_PATH)

        bad_days = kpi.filter(pl.col("outlier_rate") > outlier_threshold)

        out = {
            "status": "ok",
            "ingest_path": ingest_path,
            "transform_path": TRANSFORM_PATH,
            "kpi_path": KPI_PATH,
            "days_total": kpi.height,
            "days_excluded": bad_days.height
        }

    elif fn == "store":
        ensure_dirs()
        kpi_path = payload.get("kpi_path", KPI_PATH)
        kpi = pl.read_parquet(kpi_path)

        paths = store_outputs(
            daily_kpi=kpi,
            df_clean=None,
            cfg=StoreConfig(output_dir="out", write_clean_trips=False)
        )
        out = {"status": "ok", "stored": paths}

    else:
        return jsonify({"StatusCode": 400, "FunctionError": "UnknownFunction", "Payload": {"fn": fn}}), 400

    return jsonify({"StatusCode": 200, "Payload": out})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=False)
