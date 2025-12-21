import { useEffect, useState } from "react";
import api from "../api/api";

/* ================= TYPES ================= */

type Booking = {
  Booking_ID: number;
  Seats: number;
  Status: "CONFIRMED" | "PAID" | "CANCELLED" | "REBOOKED" | "REFUNDED";
};

type Flight = {
  Flight_Code: string;
  Dept_Location: string;
  Arr_Location: string;
  Price_Per_Seat: number;
};

type Row = {
  Booking: Booking;
  Flight: Flight;
};

/* ================= COMPONENT ================= */

export default function MyBookings() {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await api.get("/bookings/my");
      setRows(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const cancelBooking = async (id: number) => {
    await api.delete(`/bookings/cancel/${id}`);
    load();
  };

  if (loading) return <p style={{ padding: 40 }}>Loading...</p>;

  return (
    <div className="page">
      <h1>My Bookings</h1>

      {rows.length === 0 && <p>No bookings yet</p>}

      {rows.map(r => (
        <div className="card" key={r.Booking.Booking_ID}>
          <div className="row">
            <strong>
              {r.Flight.Dept_Location} → {r.Flight.Arr_Location}
            </strong>
            <span>{r.Flight.Flight_Code}</span>
          </div>

          <div className="meta">
            Seats: {r.Booking.Seats} · ₹{r.Flight.Price_Per_Seat}
          </div>

          <div className="status">
            Status: <b>{r.Booking.Status}</b>
          </div>

          {/* ✅ Correct enum check */}
          {!["CANCELLED", "REFUNDED"].includes(r.Booking.Status) && (
            <button onClick={() => cancelBooking(r.Booking.Booking_ID)}>
              Cancel Booking
            </button>
          )}
        </div>
      ))}

      <style>{`
        .page {
          min-height: calc(100vh - 80px);
          padding: 40px;
          background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
          color: white;
        }

        .card {
          background: rgba(255,255,255,0.12);
          backdrop-filter: blur(10px);
          padding: 20px;
          border-radius: 16px;
          margin-bottom: 16px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .row {
          display: flex;
          justify-content: space-between;
          font-size: 18px;
          margin-bottom: 6px;
        }

        .meta {
          opacity: 0.85;
        }

        .status {
          margin: 10px 0;
        }

        button {
          background: #ef4444;
          border: none;
          padding: 8px 18px;
          border-radius: 999px;
          color: white;
          cursor: pointer;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
}
