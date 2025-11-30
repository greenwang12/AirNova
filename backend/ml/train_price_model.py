# backend/ml/train_price_model.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

def load_data(path_csv: str):
    # expected columns: route, depart_date (ISO), days_to_depart, base_price, historical_mean, weekday, month, demand_index
    return pd.read_csv(path_csv, parse_dates=["depart_date"])

def make_features(df):
    df = df.copy()
    df["days_to_depart"] = (df["depart_date"].dt.date - pd.Timestamp.utcnow().date()).apply(lambda d: max(0, d.days))
    df["weekday"] = df["depart_date"].dt.weekday
    df["month"] = df["depart_date"].dt.month
    # fillna
    df["historical_mean"] = df.get("historical_mean", df["base_price"]).fillna(df["base_price"])
    df["demand_index"] = df.get("demand_index", 1.0).fillna(1.0)
    return df

def train(csv_path: str, n_models: int = 5):
    df = load_data(csv_path)
    df = make_features(df)

    feature_cols = ["days_to_depart", "base_price", "historical_mean", "weekday", "month", "demand_index", "route"]
    X = df[feature_cols]
    y = df["price"].values  # true observed price

    numeric_features = ["days_to_depart", "base_price", "historical_mean", "demand_index"]
    cat_features = ["weekday", "month", "route"]

    preproc = ColumnTransformer([
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
    ])

    ensemble = []
    for seed in range(n_models):
        model = Pipeline([
            ("preproc", preproc),
            ("gb", GradientBoostingRegressor(n_estimators=200, random_state=seed))
        ])
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=seed)
        model.fit(X_train, y_train)
        ensemble.append(model)
        print(f"Trained model {seed+1}/{n_models}")

    joblib.dump(ensemble, MODELS_DIR / "price_ensemble.joblib")
    print("Saved ensemble to", MODELS_DIR / "price_ensemble.joblib")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python train_price_model.py historical_fares.csv")
        raise SystemExit(1)
    train(sys.argv[1])
