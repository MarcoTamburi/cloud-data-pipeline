# src/run_ingest.py
from lambda_ingest.handler import ingest, IngestConfig

def main():
    df = ingest(IngestConfig(input_path="data/raw.parquet"))
    print("INGEST OK - shape:", df.shape)
    print(df.head(5))

if __name__ == "__main__":
    main()
