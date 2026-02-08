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
