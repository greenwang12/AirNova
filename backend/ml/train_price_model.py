# backend/ml/train_price_model.py
import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
import joblib

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def train(csv_path, n_models=5):
    df = pd.read_csv(csv_path)

    X = df[
        [
            "days_from_today","departure_hour","day_of_week",
            "seats","stops","is_weekend",
            "base_price","demand_index",
            "from_city","to_city","airline"
        ]
    ]
    y = df["price"].values

    num_features = [
        "days_from_today","departure_hour",
        "seats","stops","is_weekend",
        "base_price","demand_index"
    ]

    cat_features = ["from_city","to_city","airline","day_of_week"]

    preproc = ColumnTransformer([
        ("num", "passthrough", num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
    ])

    models = []

    for seed in range(n_models):
        model = Pipeline([
            ("prep", preproc),
            ("gb", GradientBoostingRegressor(
                n_estimators=400,
                learning_rate=0.05,
                max_depth=3,
                min_samples_leaf=20,
                random_state=seed
            ))
        ])

        Xtr, _, ytr, _ = train_test_split(X, y, test_size=0.15, random_state=seed)
        model.fit(Xtr, ytr)
        models.append(model)
        print(f"Trained model {seed+1}/{n_models}")

    joblib.dump(models, MODELS_DIR / "price_ensemble.joblib")
    print("✅ Model saved")


if __name__ == "__main__":
    import sys
    train(sys.argv[1])
