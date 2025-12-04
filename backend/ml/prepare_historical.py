# backend/ml/prepare_historical.py
import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np

ROOT = Path(__file__).parent.parent
RAW = ROOT / "data" / "historical_fares.csv"
OUT = ROOT / "data" / "historical_fares_prepared.csv"
SYN = ROOT / "ml" / "synthetic_fares.csv"
COMBINED = ROOT / "ml" / "combined_fares.csv"

def load_raw():
    try:
        return pd.read_csv(RAW, parse_dates=["depart_date"])
    except:
        # assume headerless 6-column format
        df = pd.read_csv(RAW, header=None, names=[
            "route", "depart_date", "base_price", "price",
            "historical_mean", "demand_index"
        ], parse_dates=["depart_date"])
        return df

def normalize_units(df: pd.DataFrame):
    # If base_price is huge (like 150000), convert from paise to rupees
    if df["base_price"].median() > 10000:
        df["base_price"] /= 100
        df["price"] /= 100
        df["historical_mean"] /= 100
    return df

def prepare(df: pd.DataFrame):
    df = df.copy()
    
    # Compute standard features
    now = pd.Timestamp.utcnow().normalize()

    df["days_to_depart"] = (df["depart_date"].dt.date - now.date()).apply(lambda d: max(0, d.days))
    df["weekday"] = df["depart_date"].dt.weekday
    df["month"] = df["depart_date"].dt.month

    # Ensure demand_index exists
    if "demand_index" not in df.columns:
        df["demand_index"] = 1.0

    # Required final columns
    cols = [
        "route", "depart_date", "days_to_depart",
        "base_price", "historical_mean",
        "weekday", "month", "demand_index", "price"
    ]

    df = df[cols]
    return df

def main():
    print("Loading raw historical fares...")
    df = load_raw()
    df = normalize_units(df)
    df = prepare(df)

    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print("Prepared historical saved to:", OUT)

    # Combine with synthetic if exists
    if SYN.exists():
        df_syn = pd.read_csv(SYN, parse_dates=["depart_date"])
        df_syn = prepare(df_syn)
        combined = pd.concat([df, df_syn], ignore_index=True)
        combined.to_csv(COMBINED, index=False)
        print("Combined dataset saved to:", COMBINED)
    else:
        print("Synthetic file not found, skipping combine.")

if __name__ == "__main__":
    main()
