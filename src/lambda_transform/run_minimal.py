from lambda_ingest.handler import ingest, IngestConfig
from lambda_transform.handler import add_features_and_flag_outliers, daily_kpis

def main():
    df = ingest(IngestConfig(input_path="data/raw.parquet"))
    df_t = add_features_and_flag_outliers(df)
    kpi = daily_kpis(df_t, nyc_population=8_478_072)
    print("\nDAILY KPI shape:", kpi.shape)
    print(kpi.head(10))


    print("TRANSFORM OK - shape:", df_t.shape)
    print(df_t.select(["day", "duration_min", "trip_distance", "total_amount", "is_outlier"]).head(10))

if __name__ == "__main__":
    main()
