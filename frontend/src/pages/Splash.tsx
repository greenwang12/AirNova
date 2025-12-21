// src/pages/SplashScreen.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../assets/Aeronova-logo (2).png"; // make sure you saved the logo PNG or SVG here

const text = "Seamless journeys redefined";

export default function SplashScreen() {
  const [show, setShow] = useState("");
  const nav = useNavigate();

  useEffect(() => {
  let i = 0;
  const t = setInterval(() => {
    setShow(text.slice(0, i + 1));
    i++;
    if (i === text.length) {
      clearInterval(t);
      const timeout = setTimeout(() => nav("/dashboard"), 1200);
      return () => clearTimeout(timeout);
    }
  }, 100);
  return () => clearInterval(t);
}, [nav]);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;600&display=swap');

        .splash {
          height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #0a1a2f, #b8e2e0ff);
          color: #0b1b3a;
        }
        .brand {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px; /* minimal spacing between logo and text */
        }
        .brand img {
          height: 220px;
          max-width: 90%;
          width: auto;
          margin: 0;
          padding: 0;
          filter: drop-shadow(0 6px 12px rgba(0,0,0,0.15));
        }
       .typing {
        margin: 0;
        padding: 0;
        font-size: 2rem;
        letter-spacing: 3px;
        font-family: 'Dancing Script', cursive;
        color: rgba(201, 216, 239, 0.6);
        }
        .fade-in {
          animation: fade 600ms ease forwards;
          opacity: 0;
        }
        @keyframes fade { to { opacity: 1 } }
      `}</style>

      <div className="splash">
        <div className="brand fade-in">
          <img src={Logo} alt="AeroNova logo" />
          <h1 className="typing">{show}</h1>
        </div>
      </div>
    </>
  );
}
