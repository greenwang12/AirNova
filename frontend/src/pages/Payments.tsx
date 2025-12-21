import { useEffect, useState } from "react";
import api from "../api/api";

/* ================= TYPES ================= */

type PaymentPageResponse = {
  header: { title: string; secureText: string };
  trip: { title: string; subtitle: string };
  totals: {
    totalLabel: string;
    totalAmount: number;
    breakdown: { label: string; amount: number }[];
  };
  savedMethods: { id: string; label: string; actionText: string }[];
  paymentOptions: {
    id: string;
    title: string;
    subtitle: string;
    badge?: string;
  }[];
};

/* ================= COMPONENT ================= */

export default function Payments() {
  const [data, setData] = useState<PaymentPageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .get("/payments/page")
      .then(r => setData(r.data))
      .catch(() => setErr("No active booking found"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="pay-msg">Loading payment…</div>;
  if (err) return <div className="pay-msg">{err}</div>;
  if (!data) return null;

  return (
    <div className="pay-root">
      <div className="pay-header">
        <h2>{data.header.title}</h2>
        <span>{data.header.secureText}</span>
      </div>

      <div className="pay-grid">
        <div>
          <div className="card">
            <h3>{data.trip.title}</h3>
            <p>{data.trip.subtitle}</p>
          </div>

          <div className="card">
            <h3>Payment Options</h3>
            {data.paymentOptions.map(o => (
              <div key={o.id} className="option">
                <div>
                  <b>{o.title}</b>
                  <p>{o.subtitle}</p>
                </div>
                {o.badge && <span className="badge">{o.badge}</span>}
                <span className="arrow">›</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="card">
            <h3>{data.totals.totalLabel}</h3>
            <h1>₹ {data.totals.totalAmount}</h1>

            {data.totals.breakdown.map(b => (
              <div key={b.label} className="line">
                <span>{b.label}</span>
                <span>₹ {b.amount}</span>
              </div>
            ))}

            <button className="pay-btn">PAY NOW</button>
          </div>
        </div>
      </div>

      <style>{css}</style>
    </div>
  );
}

/* ================= CSS ================= */

const css = `
.pay-root{background:#f2f2f2;min-height:100vh;font-family:system-ui}
.pay-header{background:#fff;padding:16px 24px;display:flex;justify-content:space-between}
.pay-grid{max-width:1100px;margin:24px auto;display:grid;grid-template-columns:2fr 1fr;gap:20px}
.card{background:#fff;border-radius:14px;padding:16px;margin-bottom:14px}
.option{display:flex;justify-content:space-between;padding:14px 0;border-top:1px solid #eee}
.option p{margin:4px 0 0;font-size:13px;color:#555}
.arrow{font-size:20px;color:#2563eb}
.badge{background:#d1fae5;color:#065f46;font-size:12px;padding:4px 10px;border-radius:999px}
.line{display:flex;justify-content:space-between;margin:6px 0}
.pay-btn{margin-top:16px;width:100%;padding:14px;border:none;border-radius:999px;background:#2563eb;color:#fff;font-weight:700;cursor:pointer}
.pay-msg{padding:40px;text-align:center}
`;
