import polars as pl

def add_features_and_flag_outliers(df: pl.DataFrame) -> pl.DataFrame:
    """
    Step TRANSFORM (parte 1):
    - aggiunge day e duration_min
    - aggiunge flag is_outlier con regole semplici
    """
    df2 = df.with_columns(
        pl.col("lpep_pickup_datetime").dt.date().alias("day"),
        ((pl.col("lpep_dropoff_datetime") - pl.col("lpep_pickup_datetime")).dt.total_seconds() / 60.0)
        .alias("duration_min"),
    )

    is_outlier = (
        (pl.col("duration_min") <= 0) |
        (pl.col("duration_min") > 180) |
        (pl.col("trip_distance") <= 0) |
        (pl.col("trip_distance") > 100) |
        (pl.col("total_amount") <= 0) |
        (pl.col("total_amount") > 500)
    )

    return df2.with_columns(is_outlier.alias("is_outlier"))


# KPI giornaliera
def daily_kpis(df: pl.DataFrame, nyc_population: int = 8_478_072) -> pl.DataFrame:
    """
    Step TRANSFORM (parte 2):
    - aggrega KPI per giorno:
      trips_count, total_spend, avg_spend_per_trip, avg_km_per_trip,
      avg_duration_min, outlier_rate, spend_per_capita (macro-indicatore)
    """
    if "day" not in df.columns or "duration_min" not in df.columns or "is_outlier" not in df.columns:
        raise ValueError("Missing columns. Run add_features_and_flag_outliers() first.")

    kpi = (
        df.group_by("day")
        .agg(
            pl.len().alias("trips_count"),
            pl.col("total_amount").sum().alias("total_spend"),
            pl.col("total_amount").mean().alias("avg_spend_per_trip"),
            pl.col("trip_distance").mean().alias("avg_km_per_trip"),
            pl.col("duration_min").mean().alias("avg_duration_min"),
            pl.col("is_outlier").mean().alias("outlier_rate"),
        )
        .with_columns(
            (pl.col("total_spend") / nyc_population).alias("spend_per_capita")
        )
        .sort("day")
    )
    return kpi
