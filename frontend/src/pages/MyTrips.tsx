import { useEffect, useMemo, useState } from "react";
import api from "../api/api";

type Row = {
  Booking: {
    Booking_ID: number;
    Seats: number;
    Status: string;
  };
  Flight: {
    Flight_Code: string;
    Dept_Location: string;
    Arr_Location: string;
    Departure_Time: string;
    Arrival_Time: string;
  };
};

export default function MyTrips() {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/bookings/my")
      .then(res => setRows(res.data))
      .finally(() => setLoading(false));
  }, []);

  const now = new Date().getTime();


  const { upcoming, completed } = useMemo(() => {
    const ok = rows.filter(r =>
  ["captured", "CONFIRMED"].includes(r.Booking.Status)
);
    return {
      upcoming: ok.filter(r => new Date(r.Flight.Departure_Time).getTime() > now),
      completed: ok.filter(r => new Date(r.Flight.Departure_Time).getTime() <= now),
    };
  }, [rows, now]);

  if (loading) return <p style={{ padding: 40 }}>Loading trips…</p>;

  return (
    <div className="page">
      <h1>My Trips</h1>

      <section>
        <h2>Upcoming</h2>
        {upcoming.length === 0 ? (
          <p className="empty">No upcoming trips</p>
        ) : (
          upcoming.map(r => <TripCard key={r.Booking.Booking_ID} r={r} />)
        )}
      </section>

      <section>
        <h2>Completed</h2>
        {completed.length === 0 ? (
          <p className="empty">No completed trips</p>
        ) : (
          completed.map(r => <TripCard key={r.Booking.Booking_ID} r={r} />)
        )}
      </section>

      <style>{`
        .page {
          min-height: calc(100vh - 80px);
          padding: 40px;
          background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
          color: white;
        }
        h2 { margin-top: 24px; }
        .card {
          background: rgba(255,255,255,0.12);
          backdrop-filter: blur(10px);
          border-radius: 16px;
          padding: 16px;
          margin-top: 12px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .row {
          display: flex;
          justify-content: space-between;
          font-weight: 700;
        }
        .meta {
          opacity: 0.85;
          margin-top: 6px;
        }
        .empty { opacity: 0.7; margin-top: 8px; }
      `}</style>
    </div>
  );
}

function TripCard({ r }: { r: Row }) {
  return (
    <div className="card">
      <div className="row">
        <span>{r.Flight.Dept_Location} → {r.Flight.Arr_Location}</span>
        <span>{r.Flight.Flight_Code}</span>
      </div>
      <div className="meta">
    {new Date(r.Flight.Departure_Time).toLocaleString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    })} • Seats {r.Booking.Seats}
      </div>
    </div>
  );
}
