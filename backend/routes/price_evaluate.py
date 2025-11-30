# backend/routes/price_evaluate.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from ..services.price_predictor_ml import PricePredictorML
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import io
import numpy as np

router = APIRouter(prefix="/predict-eval", tags=["predict-eval"])

@router.post("/upload-csv")
async def evaluate_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    content = await file.read()
    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8")), parse_dates=["depart_date"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    required = {"route", "depart_date", "base_price", "price"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required}")

    predictor = PricePredictorML()
    if not predictor.available():
        raise HTTPException(status_code=400, detail="ML model not found. Train model first (backend/models/price_ensemble.joblib)")

    preds = []
    for _, row in df.iterrows():
        hist_mean = row.get("historical_mean", None) if "historical_mean" in df.columns else None
        demand = row.get("demand_index", 1.0) if "demand_index" in df.columns else 1.0
        res = predictor.predict(
            route=str(row["route"]),
            depart_date=row["depart_date"].isoformat() if not pd.isna(row["depart_date"]) else str(row["depart_date"]),
            base_price=float(row["base_price"]),
            historical_mean=float(hist_mean) if hist_mean is not None and not pd.isna(hist_mean) else None,
            demand_index=float(demand) if not pd.isna(demand) else 1.0
        )
        preds.append(res["predicted_price"])

    y_true = df["price"].astype(float).values
    y_pred = np.array(preds, dtype=float)

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))

    sample = []
    for i in range(min(10, len(df))):
        sample.append({
            "route": str(df.iloc[i]["route"]),
            "depart_date": str(df.iloc[i]["depart_date"]),
            "base_price": float(df.iloc[i]["base_price"]),
            "actual_price": float(df.iloc[i]["price"]),
            "predicted_price": float(y_pred[i])
        })

    return {
        "metrics": {"MAE": round(mae, 3), "RMSE": round(rmse, 3), "R2": round(r2, 4)},
        "n_rows": int(len(df)),
        "sample_predictions": sample
    }
