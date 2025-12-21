# split_route_csv.py
import pandas as pd

PATH = "backend/data/training_flight_prices.csv"

df = pd.read_csv(PATH)

df["from_city"] = df["route"].str.split("-").str[0]
df["to_city"] = df["route"].str.split("-").str[1]

df.drop(columns=["route"], inplace=True)

# final perfect order
df = df[
    [
        "from_city",
        "to_city",
        "airline",
        "days_from_today",
        "departure_hour",
        "day_of_week",
        "seats",
        "stops",
        "is_weekend",
        "base_price",
        "demand_index",
        "price",
    ]
]

df.to_csv(PATH, index=False)
print("✅ CSV fixed for general routes")
