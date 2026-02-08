import polars as pl
import matplotlib.pyplot as plt

KPI_PATH = "out/daily_kpi.parquet"
OUTLIER_THRESHOLD = 0.15  # 15%

def main():
    # 1) Load KPI
    kpi = pl.read_parquet(KPI_PATH)

    # 2) Identify "bad" days and print them (quality report)
    bad_days = (
        kpi.filter(pl.col("outlier_rate") > OUTLIER_THRESHOLD)
           .select(["day", "outlier_rate", "trips_count"])
           .sort("outlier_rate", descending=True)
    )

    print("\n=== DATA QUALITY REPORT ===")
    print(f"Outlier threshold: {OUTLIER_THRESHOLD:.0%}")
    print(f"Total days in KPI: {kpi.height}")
    print(f"Days excluded (outlier_rate > threshold): {bad_days.height}")

    if bad_days.height > 0:
        print("\nWorst days (sorted by outlier_rate desc):")
        print(bad_days)

    # 3) Keep only "good" days for plots
    good = kpi.filter(pl.col("outlier_rate") <= OUTLIER_THRESHOLD).sort("day")

    # Convert to python objects for matplotlib
    days = good["day"].to_list()
    total_spend = good["total_spend"].to_list()
    avg_km = good["avg_km_per_trip"].to_list()
    avg_spend = good["avg_spend_per_trip"].to_list()

    # --- Plot 1: Total spend per day ---
    plt.figure()
    plt.plot(days, total_spend)
    plt.xlabel("Day")
    plt.ylabel("Total spend (USD)")
    plt.title("NYC Green Taxi - Total spend per day (clean days only)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # --- Plot 2 (Option B): Avg spend vs Avg distance (daily points) ---
    plt.figure()
    plt.scatter(avg_km, avg_spend)
    plt.xlabel("Avg km per trip (daily)")
    plt.ylabel("Avg spend per trip (daily, USD)")
    plt.title("NYC Green Taxi - Avg spend vs Avg distance (clean days only)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
