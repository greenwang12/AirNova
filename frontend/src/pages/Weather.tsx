import { useState } from "react";
import api from "../api/api";
import BackButton from "../components/BackButton";

type WeatherResp = {
  airport: string;
  weather: {
    summary: string;
    rain?: number;
    wind?: number;
    visibility?: number;
    storm?: boolean;
  };
  risk_score: number;
  status: string;
};

export default function Weather() {
  const [iata, setIata] = useState("");
  const [data, setData] = useState<WeatherResp | null>(null);
  const [error, setError] = useState("");

  const fetchWeather = async () => {
    try {
      setError("");
      const res = await api.get<WeatherResp>(`/weather/airport/${iata}`);
      setData(res.data);
    } catch {
      setData(null);
      setError("Invalid airport code");
    }
  };

  return (
    <>
      <style>{`
        .weather {
          min-height: 100vh;
          padding: 40px;
          background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
          color: white;
          font-family: system-ui;
        }
        .card {
          max-width: 420px;
          margin: auto;
          background: rgba(255,255,255,0.12);
          padding: 30px;
          border-radius: 16px;
          backdrop-filter: blur(10px);
        }
        input {
          width: 100%;
          padding: 12px;
          border-radius: 8px;
          border: none;
          margin-bottom: 12px;
        }
        button {
          width: 100%;
          padding: 12px;
          border-radius: 999px;
          border: none;
          font-weight: bold;
          cursor: pointer;
        }
        .risk {
          margin-top: 20px;
          padding: 16px;
          border-radius: 12px;
          background: rgba(0,0,0,0.3);
        }
        .safe { color: #7CFF7C; }
        .risky { color: #FF7C7C; }
      `}</style>

      <div className="weather">
        <div className="card">
          <BackButton />

          <h2>🌦️ Airport Weather Risk</h2>

          <input
            placeholder="Enter Airport IATA (e.g. DEL)"
            value={iata}
            onChange={e => setIata(e.target.value)}
          />

          <button onClick={fetchWeather}>Check Weather</button>

          {error && <p className="risky">{error}</p>}

          {data && (
            <div className="risk">
              <h3>{data.airport}</h3>
              <p>{data.weather.summary}</p>
              <p>🌧 Rain: {data.weather.rain ?? 0}</p>
              <p>💨 Wind: {data.weather.wind ?? 0}</p>
              <p>👁 Visibility: {data.weather.visibility ?? 0}</p>
              <p>
                ⚠ Status:{" "}
                <span className={data.status === "Risky" ? "risky" : "safe"}>
                  {data.status}
                </span>
              </p>
              <p>Risk Score: {data.risk_score}</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
