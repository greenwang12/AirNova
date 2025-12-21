# backend/ml/prepare_historical.py
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent

RAW = ROOT / "data" / "training_flight_prices.csv"
SYN = ROOT / "ml" / "synthetic_fares.csv"
OUT = ROOT / "ml" / "combined_training_fares.csv"


REQUIRED_COLS = [
    "from_city","to_city","airline",
    "days_from_today","departure_hour","day_of_week",
    "seats","stops","is_weekend",
    "base_price","demand_index","price"
]


def clean(df: pd.DataFrame):
    df = df.copy()

    # numeric safety
    for c in ["days_from_today","departure_hour","day_of_week",
              "seats","stops","is_weekend",
              "base_price","demand_index","price"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna()
    return df


def main():
    df = pd.read_csv(RAW)
    df = clean(df)

    if SYN.exists():
        df_syn = pd.read_csv(SYN)
        df_syn = clean(df_syn)
        df = pd.concat([df, df_syn], ignore_index=True)

    df = df[REQUIRED_COLS]
    df.to_csv(OUT, index=False)
    print("✅ Combined training data saved:", OUT)


if __name__ == "__main__":
    main()
