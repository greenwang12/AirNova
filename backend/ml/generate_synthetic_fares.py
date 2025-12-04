# backend/ml/generate_synthetic_fares.py
"""
Generate synthetic fares. If backend/data/historical_fares.csv exists,
this script will sample route distribution and price ranges from it
to produce synthetic rows that match your real dataset.
Output: backend/ml/synthetic_fares.csv
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import random
import argparse

HERE = Path(__file__).parent
OUT = HERE / "synthetic_fares.csv"
HIST = Path(__file__).parent.parent / "data" / "historical_fares.csv"

def infer_from_historical(n_samples=5000):
    df = pd.read_csv(HIST, parse_dates=["depart_date"], low_memory=False)
    # ensure columns exist
    if "route" not in df.columns or "base_price" not in df.columns:
        raise ValueError("historical_fares.csv missing required columns: route, base_price")

    # route probabilities
    route_counts = df["route"].value_counts(normalize=True)
    routes = route_counts.index.tolist()
    route_probs = route_counts.values.tolist()

    # company distribution (optional)
    companies = df["company"].dropna().unique().tolist() if "company" in df.columns else ["IndiGo","AirIndia","SpiceJet","Vistara"]

    # base price stats per route
    price_stats = df.groupby("route")["base_price"].agg(["mean","std","min","max"]).to_dict("index")

    return routes, route_probs, companies, price_stats

def fallback_defaults():
    routes = ["DEL-BOM","BLR-MAA","DEL-BLR","BOM-DEL","MAA-BLR"]
    route_probs = [0.25,0.2,0.2,0.2,0.15]
    companies = ["IndiGo","AirIndia","SpiceJet","Vistara"]
    # simple stats: mean and std
    price_stats = {
        "DEL-BOM": {"mean":3000,"std":300,"min":2000,"max":5000},
        "BLR-MAA": {"mean":2200,"std":250,"min":1500,"max":3500},
        "DEL-BLR": {"mean":2500,"std":300,"min":1700,"max":4000},
        "BOM-DEL": {"mean":3000,"std":300,"min":2000,"max":5000},
        "MAA-BLR": {"mean":2000,"std":200,"min":1200,"max":3000},
    }
    return routes, route_probs, companies, price_stats

def generate_rows(n=5000, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # infer or fallback
    if HIST.exists():
        try:
            routes, route_probs, companies, price_stats = infer_from_historical(n)
        except Exception:
            routes, route_probs, companies, price_stats = fallback_defaults()
    else:
        routes, route_probs, companies, price_stats = fallback_defaults()

    rows = []
    base_time = datetime.utcnow()
    for i in range(n):
        route = random.choices(routes, weights=route_probs, k=1)[0]
        company = random.choice(companies)
        depart_offset_days = random.randint(1, 120)
        depart_date = base_time + timedelta(days=depart_offset_days)

        stats = price_stats.get(route, {"mean":2500,"std":300,"min":1000,"max":5000})
        # sample base price around mean, clip to min/max
        base_price = int(np.clip(np.random.normal(stats["mean"], stats.get("std", 300)), stats.get("min", 800), stats.get("max", 8000)))

        historical_mean = round(base_price * (1 + np.random.normal(0, 0.05)), 2)

        days_to_depart = max(0, (depart_date.date() - base_time.date()).days)
        # demand: more demand when fewer days remain (simple heuristic)
        demand_index = 1.0 + max(0, (60 - days_to_depart) / 120.0) + float(np.random.normal(0, 0.05))

        # observed price influenced by demand and noise
        price = int(max(100, base_price * demand_index * (1 + np.random.normal(0, 0.08))))

        rows.append({
            "route": route,
            "company": company,
            "depart_date": depart_date.isoformat(),
            "days_to_depart": days_to_depart,
            "base_price": base_price,
            "historical_mean": historical_mean,
            "weekday": depart_date.weekday(),
            "month": depart_date.month,
            "demand_index": round(demand_index, 3),
            "price": price
        })

    df = pd.DataFrame(rows)
    return df

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=5000, help="Number of synthetic rows to generate")
    p.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
    p.add_argument("--out", type=str, default=str(OUT), help="Output CSV path")
    args = p.parse_args()

    df = generate_rows(n=args.n, seed=args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")

if __name__ == "__main__":
    main()
