import os
from dataclasses import dataclass
import polars as pl


@dataclass(frozen=True)
class StoreConfig:
    output_dir: str = "out"
    write_clean_trips: bool = False  # metti True se vuoi salvare anche df_clean


def store_outputs(daily_kpi: pl.DataFrame, df_clean: pl.DataFrame | None, cfg: StoreConfig) -> dict:
    """
    Step STORE:
    - crea la cartella di output se non esiste
    - salva daily_kpi in parquet
    - opzionalmente salva anche df_clean
    - ritorna i path scritti (utile per orchestrazione/Step Functions)
    """
    os.makedirs(cfg.output_dir, exist_ok=True)

    paths = {}

    daily_path = os.path.join(cfg.output_dir, "daily_kpi.parquet")
    daily_kpi.write_parquet(daily_path)
    paths["daily_kpi"] = daily_path

    if cfg.write_clean_trips and df_clean is not None:
        clean_path = os.path.join(cfg.output_dir, "clean_trips.parquet")
        df_clean.write_parquet(clean_path)
        paths["clean_trips"] = clean_path

    return paths
