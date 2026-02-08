from lambda_ingest.handler import ingest, IngestConfig
from lambda_transform.handler import add_features_and_flag_outliers, daily_kpis
from lambda_store.handler import store_outputs, StoreConfig

def main():
    df = ingest(IngestConfig(input_path="data/raw.parquet"))
    df_t = add_features_and_flag_outliers(df)
    kpi = daily_kpis(df_t, nyc_population=8_500_000)

    paths = store_outputs(
        daily_kpi=kpi,
        df_clean=df_t,
        cfg=StoreConfig(output_dir="out", write_clean_trips=False)
    )

    print("STORE OK - wrote:", paths)

if __name__ == "__main__":
    main()
