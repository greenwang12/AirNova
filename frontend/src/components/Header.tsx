import { useEffect, useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams
} from "react-router-dom";
import api from "../api/api";
import logo from "../assets/Aeronova-logo (2).png";

export default function Header() {
  const { pathname } = useLocation();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const depart = params.get("depart");

  const [open, setOpen] = useState(false);
  const [priceSignal, setPriceSignal] = useState("Loading price trend...");
  const [weatherSignal, setWeatherSignal] = useState(
    "Global Aviation Weather · Checking conditions..."
  );

  /* ---------------- PRICE SIGNAL ---------------- */
  useEffect(() => {
    api
      .get("/price-signal")
      .then(r => setPriceSignal(r.data.message))
      .catch(() => setPriceSignal("Price Trend · Data Unavailable"));
  }, []);

  /* ---------------- WEATHER SIGNAL ---------------- */
  useEffect(() => {
    const req = depart
      ? api.get("/weather/signal", { params: { depart } })
      : api.get("/weather/signal/global");

    req
      .then(r => setWeatherSignal(r.data.message))
      .catch(() =>
        setWeatherSignal(
          "Global Aviation Weather · No Significant Disruptions"
        )
      );
  }, [depart]);

  return (
    <>
      <style>{`
        .header {
  height: 76px;
  background: linear-gradient(
    to right,
    rgba(250,242,242,.95),
    rgba(197,227,251,.95)
  );
  backdrop-filter: blur(12px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 4px 18px rgba(0,0,0,.08);
  position: sticky;
  top: 0;
  z-index: 1000;
  overflow: visible;                 /* FIX */
}

/* ---------- LEFT ---------- */
.left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  height: 70px;
  cursor: pointer;
}

/* ---------- NAV ---------- */
.nav {
  display: flex;
  gap: 26px;
}

.nav a {
  font-weight: 600;
  color: #334155;
  text-decoration: none;
}

.nav a.active {
  color: #2563eb;
}

/* ---------- RIGHT ---------- */
.right {
  display: flex;
  align-items: center;
  gap: 18px;
  position: relative;                /* FIX */
  z-index: 20;
}

/* ---------- TICKER ---------- */
.signal-wrap {
  width: 620px;
  overflow: hidden;
  position: relative;                /* FIX */
  z-index: 10;
}

.signal-track {
  display: flex;
  width: max-content;
  animation: ticker 18s linear infinite;
}

.signal {
  font-size: 13px;
  font-weight: 600;
  padding: 6px 18px;
  border-radius: 999px;
  white-space: nowrap;
  margin-right: 28px;
}

.price-signal {
  background: linear-gradient(135deg,#e0f2fe,#f0f9ff);
  color: #0369a1;
}

.weather-signal {
  background: linear-gradient(135deg,#ecfeff,#f0fdfa);
  color: #0f766e;
}

@keyframes ticker {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* ---------- PROFILE ---------- */
.user {
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

/* ---------- DROPDOWN ---------- */
.dropdown {
  position: absolute;
  top: 52px;
  right: 0;
  background: linear-gradient(
    to right,
    rgba(250,242,242,.95),
    rgba(197,227,251,.95)
  ); /* ✅ FIXED */
  border-radius: 14px;
  box-shadow:
    0 20px 40px rgba(0,0,0,0.18),
    0 6px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  z-index: 9999;
  min-width: 190px;
  padding: 6px 0;
}

.dropdown div {
  padding: 12px 18px;
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.dropdown div:hover {
  background: rgba(37,99,235,0.08);
  color: #2563eb;
}


/* ---------- RESPONSIVE ---------- */
@media (max-width: 900px) {
  .nav,
  .signal-wrap {
    display: none;
  }
}

      `}</style>

      <header className="header">
        <div className="left">
          <img
            src={logo}
            className="logo"
            onClick={() => nav("/dashboard")}
          />

          <nav className="nav">
            <Link to="/dashboard" className={pathname === "/dashboard" ? "active" : ""}>Home</Link>
            <Link to="/SearchFlights" className={pathname === "/SearchFlights" ? "active" : ""}>Flights</Link>
            <Link to="/predict" className={pathname === "/predict" ? "active" : ""}>Price Prediction</Link>
            <Link to="/weather" className={pathname === "/weather" ? "active" : ""}>Weather</Link>
            <Link to="/trips" className={pathname === "/trips" ? "active" : ""}>My Trips</Link>
          </nav>
        </div>

        <div className="right">
          <div className="signal-wrap">
            <div className="signal-track">
              <div className="signal price-signal">{priceSignal}</div>
              <div className="signal weather-signal">{weatherSignal}</div>
              <div className="signal price-signal">{priceSignal}</div>
              <div className="signal weather-signal">{weatherSignal}</div>
            </div>
          </div>

          <div className="user" onClick={() => setOpen(!open)}>
            Profile ▾
          </div>

          {open && (
            <div className="dropdown">
              <div onClick={() => nav("/bookings/my")}>My Bookings</div>
              <div onClick={() => nav("/profile")}>Profile</div>
              <div onClick={() => nav("/login")}>Logout</div>
            </div>
          )}
        </div>
      </header>
    </>
  );
}
