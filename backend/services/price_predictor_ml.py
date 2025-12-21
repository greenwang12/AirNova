from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

MODEL_PATH = Path(__file__).parent.parent / "models" / "price_ensemble.joblib"


class PricePredictorML:
    def __init__(self):
        self.ensemble = None
        if MODEL_PATH.exists():
            self.ensemble = joblib.load(MODEL_PATH)

    def available(self) -> bool:
        return self.ensemble is not None

    def _build_row(
        self,
        route: str,
        depart_date: str,
        base_price: float,
        historical_mean: float | None = None,
        demand_index: float = 1.0,
    ):
        d = pd.to_datetime(depart_date)

        days_to_depart = max(
            0, (d.date() - pd.Timestamp.utcnow().date()).days
        )

        return {
            "days_to_depart": days_to_depart,
            "base_price": base_price,
            "historical_mean": historical_mean or base_price,
            "weekday": d.weekday(),
            "month": d.month,
            "demand_index": demand_index,
            "route": route,
        }

    def predict(
        self,
        route: str,
        depart_date: str,
        base_price: float,
        historical_mean: float | None = None,
        demand_index: float = 1.0,
    ):
        # 🔁 Fallback if model missing
        if not self.available():
            from ..services.price_predictor import PricePredictor

            res = PricePredictor.predict(
                base_price, pd.to_datetime(depart_date)
            )
            return {
                "predicted_price": res["predicted_price"],
                "model": "fallback",
            }

        row = self._build_row(
            route,
            depart_date,
            base_price,
            historical_mean,
            demand_index,
        )

        X = pd.DataFrame([row])
        preds = np.array([m.predict(X)[0] for m in self.ensemble])

        return {
            "predicted_price": round(float(preds.mean()), 2),
            "uncertainty_std": round(float(preds.std(ddof=0)), 2),
            "model": "ensemble_mean",
        }
