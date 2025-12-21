# backend/ml/generate_synthetic_fares.py
import pandas as pd
import numpy as np
import random
from pathlib import Path
import argparse

HERE = Path(__file__).parent
OUT = HERE / "synthetic_fares.csv"

AIRPORTS = ["DEL","BLR","BOM","MAA","HYD","CCU"]
AIRLINES = ["IndiGo","AirIndia","Akasa","Vistara"]

def generate(n=5000, seed=None):
    if seed:
        random.seed(seed)
        np.random.seed(seed)

    rows = []

    for _ in range(n):
        from_city = random.choice(AIRPORTS)
        to_city = random.choice([a for a in AIRPORTS if a != from_city])

        days = random.randint(1, 60)
        base = random.randint(3500, 7500)
        demand = 1 + (30 - days) / 60 + np.random.normal(0, 0.05)

        price = int(base * demand * (1 + np.random.normal(0, 0.08)))

        rows.append({
            "from_city": from_city,
            "to_city": to_city,
            "airline": random.choice(AIRLINES),
            "days_from_today": days,
            "departure_hour": random.choice([6,9,12,18,21]),
            "day_of_week": random.randint(0,6),
            "seats": random.choice([150,180,200]),
            "stops": random.choice([0,1]),
            "is_weekend": random.choice([0,1]),
            "base_price": base,
            "demand_index": round(demand,3),
            "price": price
        })

    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=5000)
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()

    df = generate(args.n, args.seed)
    df.to_csv(OUT, index=False)
    print("✅ Synthetic fares written:", OUT)


if __name__ == "__main__":
    main()
