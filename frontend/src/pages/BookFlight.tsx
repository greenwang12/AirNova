import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/api";
import "./BookFlight.css";

/* ================= TYPES ================= */

type Flight = {
  Flight_ID: number;
  Dept_Location: string;
  Arr_Location: string;
  Price_Per_Seat: number;
};

type Gender = "" | "Male" | "Female" | "Other";

type Traveller = {
  firstName: string;
  lastName: string;
  age: number | "";
  gender: Gender;
  open: boolean;
};

const STEPS = ["Trip", "Travellers", "Seats", "Review & Pay"];

/* ================= VALIDATION ================= */

const nameOk = (s: string) => /^[A-Za-z]+$/.test(s.trim());
const travellerOk = (t: Traveller) =>
  nameOk(t.firstName) &&
  nameOk(t.lastName) &&
  typeof t.age === "number" &&
  t.age >= 12 &&
  !!t.gender;

/* ================= COMPONENT ================= */

export default function BookFlight() {
  const { id } = useParams();
  const nav = useNavigate();

  const [flight, setFlight] = useState<Flight | null>(null);
  const [step, setStep] = useState(0);
  const [travellers, setTravellers] = useState<Traveller[]>([
    { firstName: "", lastName: "", age: "", gender: "", open: true }
  ]);
  const [selectedSeats, setSelectedSeats] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get(`/flights/${id}`).then(r => setFlight(r.data));
  }, [id]);

  const seatCount = travellers.length;

  const total = useMemo(
    () => (flight ? flight.Price_Per_Seat * seatCount : 0),
    [flight, seatCount]
  );

  const travellersValid =
    travellers.length > 0 && travellers.every(travellerOk);

  /* ================= TRAVELLERS ================= */

  const addTraveller = () => {
    setTravellers(t => [
      ...t.map(tr => ({ ...tr, open: false })),
      { firstName: "", lastName: "", age: "", gender: "", open: true }
    ]);
  };

  const updateTraveller = <K extends keyof Traveller>(
    i: number,
    k: K,
    v: Traveller[K]
  ) => {
    setTravellers(t =>
      t.map((tr, idx) =>
        idx === i ? { ...tr, [k]: v } : tr
      )
    );
  };

  /* ================= SEATS ================= */

  const toggleSeat = (seat: string) => {
    setSelectedSeats(p => {
      if (p.includes(seat)) return p.filter(s => s !== seat);
      if (p.length >= seatCount) return p;
      return [...p, seat];
    });
  };

  const seatClass = (r: number) =>
    r < 5 ? "high" : r < 15 ? "low" : "free";

  /* ================= PAYLOAD ================= */

  const confirmAndPay = async () => {
    if (!flight) return;
    setLoading(true);

    await api.post("/bookings", {
      flight_id: flight.Flight_ID,
      travellers: travellers.map(t => ({
        full_name: `${t.firstName} ${t.lastName}`,
        age: t.age,
        gender: t.gender
      })),
      seats: selectedSeats
    });

    nav("/payment");
  };

  if (!flight) return null;

  return (
    <div className="booking-page">
      <div className="booking-container">
        <div className="booking-layout">

          <div className="booking-left">

            {/* STEPS */}
            <div className="steps">
              {STEPS.map((s, i) => (
                <div key={i} className={`step ${step >= i ? "active" : ""}`}>
                  <span>{i + 1}</span>
                  <p>{s}</p>
                </div>
              ))}
            </div>

            {/* STEP 1 — TRIP */}
            {step === 0 && (
              <div className="card trip-card">

                <div className="trip-route">
                  <h2>{flight.Dept_Location} → {flight.Arr_Location}</h2>
                  <span className="trip-badge">Non-Stop</span>
                </div>

                <div className="trip-airline">
                  <div className="airline-left">
                    <div className="airline-logo">✈️</div>
                    <div>
                      <strong>AirNova</strong>
                      <p>Economy · AN-102</p>
                    </div>
                  </div>

                  <div className="airline-right">
                    <p className="price">₹{flight.Price_Per_Seat}</p>
                    <span className="per-seat">per seat</span>
                  </div>
                </div>

                <div className="trip-timeline">
                  <div>
                    <h3>23:40</h3>
                    <p>{flight.Dept_Location}</p>
                  </div>

                  <div className="timeline-line">
                    <span>2h 10m</span>
                  </div>

                  <div>
                    <h3>01:50</h3>
                    <p>{flight.Arr_Location}</p>
                  </div>
                </div>

                <div className="trip-info">
                  <span>🧳 Cabin 7kg</span>
                  <span>🛄 Check-in 15kg</span>
                  <span>❌ Cancellation fee applies</span>
                </div>

              </div>
            )}

            {/* STEP 2 — TRAVELLERS */}
            {step === 1 && (
              <div className="card">
                <h3>Traveller Details</h3>

                {travellers.map((t, i) =>
                  t.open ? (
                    <div key={i} className="traveller-form">
                      <input
                        placeholder="First Name"
                        value={t.firstName}
                        onChange={e => updateTraveller(i, "firstName", e.target.value)}
                      />
                      <input
                        placeholder="Last Name"
                        value={t.lastName}
                        onChange={e => updateTraveller(i, "lastName", e.target.value)}
                      />
                      <input
                        type="number"
                        placeholder="Age"
                        value={t.age}
                        onChange={e =>
                          updateTraveller(i, "age", Number(e.target.value))
                        }
                      />
                      <select
                        value={t.gender}
                        onChange={e =>
                          updateTraveller(i, "gender", e.target.value as Gender)
                        }
                      >
                        <option value="">Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  ) : (
                    <div key={i} className="traveller-summary">
                      Traveller {i + 1}: {t.firstName} {t.lastName}
                    </div>
                  )
                )}

                <button onClick={addTraveller}>+ Add Traveller</button>
              </div>
            )}

            {/* STEP 3 — SEATS */}
            {step === 2 && (
              <div className="card seat-card">
                <div className="seat-header">
                  <h3>Seat Selection</h3>
                  <p>{selectedSeats.length}/{seatCount}</p>
                </div>

                <div className="aircraft-wrapper">
                  <div className="seat-cols">
                    <span /> A B C <span /> D E F <span />
                  </div>

                  <div className="aircraft-scroll">
                    <div className="aircraft-svg-shell">

                      <svg viewBox="0 0 300 900" className="aircraft-svg">
                        <path
                          d="M150 0 C200 30 260 90 280 180
                             V720 C260 820 200 880 150 900
                             C100 880 40 820 20 720
                             V180 C40 90 100 30 150 0 Z"
                          fill="#fff"
                        />
                      </svg>

                      <div className="aircraft-seat-layer">
                        {Array.from({ length: 30 }).map((_, r) => (
                          <div key={r} className="seat-row">
                            <span className="row-no">{r + 1}</span>
                            {["A", "B", "C"].map(c => (
                              <div
                                key={c}
                                className={`seat ${seatClass(r)} ${
                                  selectedSeats.includes(`${r + 1}${c}`)
                                    ? "active"
                                    : ""
                                }`}
                                onClick={() =>
                                  toggleSeat(`${r + 1}${c}`)
                                }
                              />
                            ))}
                            <div className="aisle" />
                            {["D", "E", "F"].map(c => (
                              <div
                                key={c}
                                className={`seat ${seatClass(r)} ${
                                  selectedSeats.includes(`${r + 1}${c}`)
                                    ? "active"
                                    : ""
                                }`}
                                onClick={() =>
                                  toggleSeat(`${r + 1}${c}`)
                                }
                              />
                            ))}
                            <span className="row-no">{r + 1}</span>
                          </div>
                        ))}
                      </div>

                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* STEP 4 — PAY */}
            {step === 3 && (
              <div className="card">
                <h3>Total ₹{total}</h3>
                <button
                  className="pay-btn"
                  disabled={loading}
                  onClick={confirmAndPay}
                >
                  Confirm & Pay
                </button>
              </div>
            )}

            {/* NAV */}
            <div className="actions">
              {step > 0 && (
                <button onClick={() => setStep(step - 1)}>Back</button>
              )}
              {step < 3 && (
                <button
                  disabled={
                    (step === 1 && !travellersValid) ||
                    (step === 2 &&
                      selectedSeats.length !== seatCount)
                  }
                  onClick={() => setStep(step + 1)}
                >
                  Continue
                </button>
              )}
            </div>

          </div>

          <aside className="booking-right">
            <div className="card fare">
              <p>
                Total <strong>₹{total}</strong>
              </p>
            </div>
          </aside>

        </div>
      </div>
    </div>
  );
}
