import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/api";

type Flight = {
  Flight_ID: number;
  Dept_Location: string;
  Arr_Location: string;
  Price_Per_Seat: number;
};

export default function BookFlight() {
  const { id } = useParams();
  const [flight, setFlight] = useState<Flight | null>(null);
  const [seats, setSeats] = useState(1);

  useEffect(() => {
    api.get(`/flights/${id}`).then(r => setFlight(r.data));
  }, [id]);

  if (!flight) return <div>Loading…</div>;

  const total = flight.Price_Per_Seat * seats + 350;

  const proceed = async () => {
    try {
      await api.post(
        "/bookings",
        { flight_id: flight.Flight_ID, seats },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`
          }
        }
      );

      window.location.href = "/payment";
    } catch (e) {
      alert("BOOKING FAILED");
      console.error(e);
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h1>{flight.Dept_Location} → {flight.Arr_Location}</h1>

      <input
        type="number"
        min={1}
        value={seats}
        onChange={e => setSeats(+e.target.value)}
      />

      <p>Total ₹ {total}</p>

      <button onClick={proceed}>PROCEED TO PAYMENT</button>
    </div>
  );
}
