import { useState } from "react";
import BackButton from "../components/BackButton";

type PredictResult = {
  predicted_price: number;
  confidence?: number;
};

export default function PricePredict() {
  const [route, setRoute] = useState("");
  const [date, setDate] = useState("");
  const [base, setBase] = useState("");
  const [result, setResult] = useState<PredictResult | null>(null);
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          route,
          depart_date: date,
          base_price: Number(base),
        }),
      });

      if (!res.ok) throw new Error();
      setResult(await res.json());
    } catch {
      setError("Unable to predict price");
    }
  };

  return (
    <>
      <style>{`
        .page {
          min-height: 100vh;
          padding: 40px;
          background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
          color: white;
          font-family: system-ui;
        }
        .card {
          max-width: 520px;
          margin: auto;
          background: rgba(255,255,255,0.12);
          padding: 28px;
          border-radius: 18px;
          backdrop-filter: blur(10px);
        }
        input {
          width: 100%;
          padding: 12px;
          border-radius: 10px;
          border: none;
          margin-top: 12px;
        }
        button {
          margin-top: 16px;
          padding: 12px;
          width: 100%;
          border-radius: 12px;
          border: none;
          background: #4ade80;
          font-weight: bold;
          cursor: pointer;
        }
        .result {
          margin-top: 20px;
          font-size: 1.2rem;
        }
        .error {
          margin-top: 12px;
          color: #ffb4b4;
        }
      `}</style>

      <div className="page">
        <div className="card">
          <BackButton />

          <h2>🔮 Flight Price Prediction</h2>

          <input
            placeholder="Route (DEL-BOM)"
            value={route}
            onChange={e => setRoute(e.target.value)}
          />

          <input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
          />

          <input
            type="number"
            placeholder="Base Price"
            value={base}
            onChange={e => setBase(e.target.value)}
          />

          <button onClick={submit}>Predict</button>

          {error && <div className="error">{error}</div>}

          {result && (
            <div className="result">
              <p><b>Predicted Price:</b> ₹{result.predicted_price}</p>
              {result.confidence && <p>Confidence: {result.confidence}</p>}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
