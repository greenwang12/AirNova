import HeroSlider from "../components/HeroSlider";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../api/api";

type RecommendedRoute = [route: string, count: number];

export default function Dashboard() {
  const nav = useNavigate();
  const [routes, setRoutes] = useState<RecommendedRoute[]>([]);

  // 👇 read logged-in user (set in Login.tsx)
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    if (!user?.id) return;

    api
      .get(`/recommendations/top-routes/${user.id}`)
      .then(res => setRoutes(res.data))
      .catch(() => setRoutes([]));
  }, [user?.id]);

  return (
    <>
      {/* HERO */}
      <div className="hero">
        <HeroSlider />

        <p className="hero-tagline">Your journey starts here.</p>

        <div className="hero-text">
          <h1 onClick={() => nav("/SearchFlights")}>Search Flights</h1>
        </div>
      </div>

      {/* RECOMMENDATIONS */}
      {routes.length > 0 && (
        <section className="reco-wrap">
          <h2 className="reco-title">Recommended for you</h2>

          <div className="reco-scroll">
            {routes.map(([route, count]) => (
              <div
                key={route}
                className="reco-card"
                onClick={() => nav(`/SearchFlights?route=${route}`)}
              >
                <span className="route">{route}</span>
                <span className="count">{count} trips</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* STYLES */}
      <style>{`
        @import url("https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@1&family=Playfair+Display:ital@1&display=swap");

        .hero {
          position: relative;
          height: 520px;
          overflow: hidden;
        }

        .hero-tagline {
          position: absolute;
          bottom: 120px;
          left: 32px;
          z-index: 20;
          margin: 0;
          font-family: "Playfair Display", serif;
          font-size: 60px;
          letter-spacing: 1.5px;
          font-style: italic;
          opacity: 0.85;
        }

        .hero-text {
          position: absolute;
          bottom: 30px;
          left: 25px;
          z-index: 20;
          pointer-events: none;
        }

        .hero-text h1 {
          pointer-events: auto;
          font-family: "Cormorant Garamond", serif;
          font-weight: 200;
          font-size: 25px;
          letter-spacing: 2px;
          background: rgba(0,0,0,0.8);
          padding: 12px 25px;
          border-radius: 999px;
          color: white;
          cursor: pointer;
          transition: transform .2s ease;
        }

        .hero-text h1:hover {
          transform: scale(1.05);
        }

        .reco-wrap {
          padding: 50px 30px;
          background: linear-gradient(
            to bottom,
            rgba(255,255,255,0.95),
            rgba(245,247,250,0.95)
          );
        }

        .reco-title {
          font-family: "Playfair Display", serif;
          font-style: italic;
          font-size: 30px;
          margin-bottom: 22px;
        }

        .reco-scroll {
          display: flex;
          gap: 20px;
          overflow-x: auto;
          scroll-snap-type: x mandatory;
        }

        .reco-card {
          min-width: 200px;
          padding: 18px 22px;
          border-radius: 18px;
          cursor: pointer;
          scroll-snap-align: start;
          background: rgba(255,255,255,0.65);
          backdrop-filter: blur(12px);
          box-shadow: 0 8px 30px rgba(0,0,0,0.08);
          transition: transform .25s ease, box-shadow .25s ease;
        }

        .reco-card:hover {
          transform: translateY(-6px) scale(1.04);
          box-shadow: 0 18px 40px rgba(0,0,0,0.15);
        }

        .reco-card .route {
          font-size: 20px;
          font-weight: 600;
        }

        .reco-card .count {
          font-size: 13px;
          opacity: 0.6;
        }
      `}</style>
    </>
  );
}
