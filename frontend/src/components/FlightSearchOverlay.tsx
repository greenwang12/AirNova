import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function FlightSearchOverlay() {
  const [from, setFrom] = useState("New Delhi");
  const [to, setTo] = useState("Mumbai");
  const [date, setDate] = useState("");
  const nav = useNavigate();

  const search = () => {
    const params = new URLSearchParams();
    if (from) params.set("depart", from);
    if (to) params.set("arrive", to);
    if (date) params.set("date", date);
    nav(`/flights?${params.toString()}`);
  };

  return (
    <div className="card search-overlay">
      <div className="row row-3">
        <div>
          <label>From</label>
          <input className="input" value={from} onChange={e => setFrom(e.target.value)} />
        </div>
        <div>
          <label>To</label>
          <input className="input" value={to} onChange={e => setTo(e.target.value)} />
        </div>
        <div>
          <label>Departure date</label>
          <input className="date" type="date" value={date} onChange={e => setDate(e.target.value)} />
        </div>
      </div>
      <button className="btn" onClick={search}>Search flights</button>
    </div>
  );
}
