import polars as pl

PATH = "data/raw.parquet"

def main():
    df = pl.read_parquet(PATH)
    print("Shape:", df.shape)
    print(df.head(5))

    # trasformazioni minime "da pipeline"
    df2 = (
        df
        .with_columns(
            pl.lit(1).alias("dummy_col")
        )
        .select(df.columns[:5] + ["dummy_col"])
    )

    print("After transform:", df2.shape)
    print(df2.head(5))

if __name__ == "__main__":
    main()

