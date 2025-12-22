import "./Flightcard.css";
import { useNavigate } from "react-router-dom";

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
  company?: { Name: string };
};

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

const timeOnly = (dt: string) => dt.slice(11, 16);

const durationHM = (d: string, a: string) => {
  const [dh, dm] = d.slice(11, 16).split(":").map(Number);
  const [ah, am] = a.slice(11, 16).split(":").map(Number);
  let mins = ah * 60 + am - (dh * 60 + dm);
  if (mins < 0) mins += 1440;
  return `${Math.floor(mins / 60)} h ${mins % 60} m`;
};

export default function FlightCard({ f }: { f: Flight }) {
  const nav = useNavigate();

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
      <div className="time-col left">
        <div className="time">{timeOnly(f.Departure_Time)}</div>
        <div className="city">{f.Dept_Location}</div>
      </div>

      {/* Duration */}
      <div className="mid-col">
        <div className="dur">
          {durationHM(f.Departure_Time, f.Arrival_Time)}
        </div>
        <div className="bar" />
        <div className="stop">
          {f.Stops === 0 ? "Non stop" : `${f.Stops} stop`}
        </div>
      </div>

      {/* Arrival */}
      <div className="time-col right">
        <div className="time">{timeOnly(f.Arrival_Time)}</div>
        <div className="city">{f.Arr_Location}</div>
      </div>

      {/* Price */}
      <div className="price-block">
        <div className="price">₹ {f.Price_Per_Seat.toLocaleString()}</div>
        <button
          className="book-btn"
          onClick={() => nav(`/book/${f.Flight_ID}`)}
        >
          BOOK NOW
        </button>
      </div>
    </div>
  );
}
