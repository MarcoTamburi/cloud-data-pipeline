# src/lambda_ingest/handler.py
from __future__ import annotations

from dataclasses import dataclass
import polars as pl


@dataclass(frozen=True)
class IngestConfig:
    input_path: str


def ingest(cfg: IngestConfig) -> pl.DataFrame:
    """
    Lambda-style step: INGEST
    - Legge il parquet raw
    - Seleziona un subset di colonne utili (schema stabile)
    - Ritorna un DataFrame Polars
    """
    df = pl.read_parquet(cfg.input_path)

    # Colonne tipiche del Green Taxi (lpep_*)
    # Nota: alcune versioni possono avere varianti -> gestiamo con intersection
    wanted = [
        "VendorID",
        "lpep_pickup_datetime",
        "lpep_dropoff_datetime",
        "PULocationID",
        "DOLocationID",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "total_amount",
        "payment_type",
    ]

    cols = [c for c in wanted if c in df.columns]
    if not cols:
        raise ValueError(
            "Nessuna colonna attesa trovata. Controlla df.columns e aggiorna 'wanted'."
        )

    df = df.select(cols)

    # Mini pulizia: cast coerenti dove serve
    # (se i tipi sono già ok, Polars non fa danni)
    if "passenger_count" in df.columns:
        df = df.with_columns(pl.col("passenger_count").cast(pl.Int64, strict=False))
    if "trip_distance" in df.columns:
        df = df.with_columns(pl.col("trip_distance").cast(pl.Float64, strict=False))
    if "fare_amount" in df.columns:
        df = df.with_columns(pl.col("fare_amount").cast(pl.Float64, strict=False))
    if "total_amount" in df.columns:
        df = df.with_columns(pl.col("total_amount").cast(pl.Float64, strict=False))

    return df
