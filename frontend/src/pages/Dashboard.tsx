import HeroSlider from "../components/HeroSlider";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const nav = useNavigate();

  return (
    <>
      <section className="hero">
        <HeroSlider />
        <div className="hero-overlay" />

        <div className="hero-content">
          <h1>Your journey starts here.</h1>
          <button onClick={() => nav("/SearchFlights")}>
            Search Flights
          </button>
        </div>

        {/* FEATURE CARDS */}
        <div className="hero-cards">
          <div className="hero-card" onClick={() => nav("/SearchFlights")}>
            ✈️
            <h3>Smart Flight Search</h3>
            <p>Find the best routes instantly.</p>
          </div>

          <div className="hero-card" onClick={() => nav("/PricePrediction")}>
            💰
            <h3>Price Prediction</h3>
            <p>Know when to book or wait.</p>
          </div>

          <div className="hero-card" onClick={() => nav("/Weather")}>
            ☁️
            <h3>Weather Insights</h3>
            <p>Plan smarter with aviation data.</p>
          </div>

          <div className="hero-card" onClick={() => nav("/Trips")}>
            📍
            <h3>Trip Tracking</h3>
            <p>Manage all your trips.</p>
          </div>
        </div>

        <div className="hero-bottom-fade" />
      </section>

      <style>{`
        @import url("https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&display=swap");

        .hero {
          position: relative;
          height: 720px;
          overflow: hidden;
          background: #000;
        }

        .hero,
        .hero .slick-list,
        .hero .slick-track,
        .hero .slick-slide {
          height: 100%;
        }

        .hero img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .hero-overlay {
          position: absolute;
          inset: 0;
          background: linear-gradient(
            to bottom,
            rgba(0,0,0,.55),
            rgba(0,0,0,.2),
            rgba(0,0,0,.75)
          );
          z-index: 5;
        }

        .hero-bottom-fade {
          position: absolute;
          bottom: 0;
          height: 180px;
          width: 100%;
          background: linear-gradient(
            to bottom,
            rgba(15,23,42,0),
            rgba(15,23,42,.95)
          );
          z-index: 6;
        }

        .hero-content {
          position: absolute;
          left: 56px;
          top: 48%;
          transform: translateY(-50%);
          z-index: 10;
          max-width: 520px;
        }

        .hero-content h1 {
          font-family: "Playfair Display", serif;
          font-size: 56px;
          font-style: italic;
          color: white;
          margin-bottom: 24px;
          text-shadow: 0 12px 30px rgba(0,0,0,.5);
        }

        .hero-content button {
          padding: 14px 36px;
          border-radius: 999px;
          border: none;
          font-size: 16px;
          color: white;
          cursor: pointer;
          background: linear-gradient(135deg,#020617,#0f172a);
          box-shadow: 0 20px 45px rgba(0,0,0,.45);
          transition: transform .25s ease, box-shadow .25s ease;
        }

        .hero-content button:hover {
          transform: translateY(-2px) scale(1.05);
          box-shadow: 0 30px 70px rgba(0,0,0,.65);
        }

        /* blended cards container */
        .hero-cards {
          position: absolute;
          bottom: 72px;
          left: 50%;
          transform: translateX(-50%);
          width: calc(100% - 120px);
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 26px;
          padding: 32px 24px;
          border-radius: 36px;
          background: linear-gradient(
            to top,
            rgba(15,23,42,.6),
            rgba(15,23,42,0)
          );
          z-index: 15;
        }

        /* glass cards */
        .hero-card {
          padding: 30px 24px;
          border-radius: 26px;
          text-align: center;
          cursor: pointer;
          color: white;
          opacity: 69%;
          background: linear-gradient(
            135deg,
            rgba(255,255,255,.28),
            rgba(255,255,255,.1)
          );
          backdrop-filter: blur(22px) saturate(140%);
          border: 1px solid rgba(255,255,255,.18);
          box-shadow:
            0 25px 60px rgba(0,0,0,.45),
            inset 0 1px 1px rgba(255,255,255,.25);
          transition: transform .3s ease, box-shadow .3s ease;
        }

        .hero-card:hover {
          transform: translateY(-8px) scale(1.04);
          box-shadow: 0 40px 90px rgba(0,0,0,.6);
        }

        .hero-card h3 {
          margin: 12px 0 6px;
          font-size: 18px;
          font-weight: 600;
          color: #f8fafc;
        }

        .hero-card p {
          font-size: 14px;
          margin: 0;
          color: rgba(255,255,255,.75);
        }

        @media (max-width: 1100px) {
          .hero-cards {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (max-width: 640px) {
          .hero {
            height: 780px;
          }
          .hero-cards {
            grid-template-columns: 1fr;
            bottom: 32px;
          }
        }
      `}</style>
    </>
  );
}
