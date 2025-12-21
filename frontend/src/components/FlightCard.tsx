import "./Flightcard.css";
import { useNavigate } from "react-router-dom";

/* ================= TYPES ================= */
type Flight = {
  Flight_ID: number;
  Flight_Code: string;
  Dept_Location: string;
  Arr_Location: string;
  Departure_Time: string;
  Arrival_Time: string;
  Price_Per_Seat: number;
  Stops: number;
  Available_Seats: number;
  company?: {
    Name: string;
  };
};

/* ================= LOGO MAPPING ================= */
const airlineLogos: Record<string, string> = {
  "Air India": "/logos/air-india.jpg",
  "Lufthansa": "/logos/Lufthansa.png",
  "British Airways": "/logos/british-airways.png",
  "Gulf Air": "/logos/gulfair.svg",
  "Vistara": "/logos/vistara.jpeg",
  "SpiceJet": "/logos/spicejet.png",
  "Singapore Airlines": "/logos/singapore-airlines.png",
  "Akasa Air": "/logos/Akasa-Air-Emblem.png",
  "IndiGo": "/logos/indigo.png",
  "Qatar Airways": "/logos/Qatar-Airways.png",
  "Emirates": "/logos/emirates.jpg",
  "Caribbean Airlines": "/logos/caribbean.jpg",
  "American Airlines": "/logos/americanairlines.jpg",
};

/* ================= COMPONENT ================= */
export default function FlightCard({ f }: { f: Flight }) {
  const nav = useNavigate();

  // Time calculations
  const dep = new Date(f.Departure_Time);
  const arr = new Date(f.Arrival_Time);
  const durMin = Math.floor((arr.getTime() - dep.getTime()) / 60000);
  const h = Math.floor(durMin / 60);
  const m = durMin % 60;

  return (
    <div className="flight-card">
      {/* Airline */}
      <div className="airline">
        <img
          className="airline-logo"
          src={airlineLogos[f.company?.Name ?? ""] || "/logos/default.png"}
          alt={f.company?.Name}
        />
        <div>
          <div className="airline-name">{f.company?.Name}</div>
          <div className="flight-code">{f.Flight_Code}</div>
        </div>
      </div>

      {/* Departure */}
      <div className="time-block">
        <div className="time">
          {dep.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
        <div className="city">{f.Dept_Location}</div>
      </div>

      {/* Duration */}
      <div className="duration">
        <div className="dur">{h}h {m}m</div>
        <div className="stop">{f.Stops === 0 ? "Non-stop" : `${f.Stops} stop`}</div>
      </div>

      {/* Arrival */}
      <div className="time-block">
        <div className="time">
          {arr.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
        <div className="city">{f.Arr_Location}</div>
      </div>

      {/* Price + Booking */}
      <div className="price-block">
        <div className="price">₹ {f.Price_Per_Seat.toLocaleString()}</div>

        {/* Navigate to booking page */}
        <button className="book-btn" onClick={() => nav(`/book/${f.Flight_ID}`)}>
          BOOK NOW
        </button>

        {f.Available_Seats <= 5 && (
          <div className="seats-left">⚠ {f.Available_Seats} seats left</div>
        )}
      </div>
    </div>
  );
}
