import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Select from "react-select";
import "./SearchFlights.css";

/* ========= TYPES ========= */
type Airport = { value: string; label: string };
type TravelClass = "Economy" | "Premium Economy" | "Business" | "First Class";
type TripType = "oneway" | "round" | "multi";

/* ========= DATA ========= */
const AIRPORTS: Airport[] = [
  { value: "DEL", label: "Delhi (DEL)" },
  { value: "BLR", label: "Bengaluru (BLR)" },
  { value: "BOM", label: "Mumbai (BOM)" },
  { value: "GOA", label: "Goa (GOA)" },
  { value: "DXB", label: "Dubai (DXB)" },
  { value: "SIN", label: "Singapore (SIN)" },
  { value: "LHR", label: "London Heathrow (LHR)" },
  { value: "JFK", label: "New York (JFK)" }
];

const CLASSES: TravelClass[] = [
  "Economy",
  "Premium Economy",
  "Business",
  "First Class"
];

const DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

function getMonthDays(y: number, m: number) {
  const first = new Date(y, m, 1).getDay();
  const total = new Date(y, m + 1, 0).getDate();
  return [
    ...Array(first).fill(null),
    ...Array.from({ length: total }, (_, i) => i + 1)
  ];
}

/* ========= COMPONENT ========= */
export default function SearchFlights() {
  const navigate = useNavigate();

  const [tripType, setTripType] = useState<TripType>("oneway");

  const [from, setFrom] = useState<Airport | null>(AIRPORTS[0]);
  const [to, setTo] = useState<Airport | null>(AIRPORTS[2]);

  const [showCalendar, setShowCalendar] = useState(false);
  const [baseMonth, setBaseMonth] = useState(new Date());
  const [departDate, setDepartDate] = useState<Date | null>(null);

  const [priceMap, setPriceMap] =
    useState<Record<string, number>>({});

  const [showTravellers, setShowTravellers] = useState(false);
  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [infants, setInfants] = useState(0);
  const [travelClass, setTravelClass] =
    useState<TravelClass>("Economy");

  const totalTravellers = adults + children + infants;

  useEffect(() => {
    const map: Record<string, number> = {};

    [0, 1].forEach(offset => {
      const y = baseMonth.getFullYear();
      const m = baseMonth.getMonth() + offset;
      const days = new Date(y, m + 1, 0).getDate();

      for (let d = 1; d <= days; d++) {
        const key = new Date(y, m, d).toISOString().slice(0, 10);
        map[key] = 3500 + d * 20;
      }
    });

    setPriceMap(map);
  }, [baseMonth]);

  const search = () => {
    if (!from || !to || !departDate) return;

    navigate(
      `/flights?depart=${from.value}` +
        `&arrive=${to.value}` +
        `&date=${departDate.toISOString().slice(0, 10)}` +
        `&adults=${adults}&children=${children}&infants=${infants}` +
        `&class=${travelClass}&trip=${tripType}`
    );
  };

  return (
    <div className="mmt-page">
      <div className="mmt-search-card">

        <div className="trip-type-pill">
          {[
            { label: "One Way", value: "oneway" },
            { label: "Round Trip", value: "round" },
            { label: "Multi City", value: "multi" }
          ].map(t => (
            <label key={t.value} className="trip-pill">
              <input
                type="radio"
                name="tripType"
                checked={tripType === t.value}
                onChange={() => setTripType(t.value as TripType)}
              />
              <span>{t.label}</span>
            </label>
          ))}
        </div>

        <div className="inputs">
          <div className="box">
            <span>From</span>
            <Select
              options={AIRPORTS}
              value={from}
              onChange={v => setFrom(v as Airport)}
              classNamePrefix="airport"
            />
          </div>

          <div
            className="swap"
            onClick={() => {
              if (!from || !to) return;
              setFrom(to);
              setTo(from);
            }}
          >
            ⇄
          </div>

          <div className="box">
            <span>To</span>
            <Select
              options={AIRPORTS}
              value={to}
              onChange={v => setTo(v as Airport)}
              classNamePrefix="airport"
            />
          </div>

          <div className="box" onClick={() => setShowCalendar(true)}>
            <span>Departure</span>
            <h2>{departDate ? departDate.toDateString() : "Select"}</h2>
          </div>

          <div className="box" onClick={() => setShowTravellers(true)}>
            <span>Travellers & Class</span>
            <h2>{totalTravellers} Traveller</h2>
            <p>{travelClass}</p>
          </div>
        </div>

        <button className="search-btn" onClick={search}>
          SEARCH
        </button>
      </div>

      {showCalendar && (
        <div className="calendar-overlay" onClick={() => setShowCalendar(false)}>
          <div className="calendar-box" onClick={e => e.stopPropagation()}>
            <div className="cal-header">
              <button onClick={() =>
                setBaseMonth(new Date(baseMonth.getFullYear(), baseMonth.getMonth() - 1))
              }>‹</button>
              <b>Select Dates</b>
              <button onClick={() =>
                setBaseMonth(new Date(baseMonth.getFullYear(), baseMonth.getMonth() + 1))
              }>›</button>
            </div>

            <div className="cal-months">
              {[0, 1].map(offset => {
                const d = new Date(baseMonth.getFullYear(), baseMonth.getMonth() + offset, 1);
                const days = getMonthDays(d.getFullYear(), d.getMonth());

                return (
                  <div key={offset} className="cal-month">
                    <h3>{d.toLocaleString("en-IN", { month: "long", year: "numeric" })}</h3>

                    <div className="cal-week">
                      {DAYS.map(x => <span key={x}>{x}</span>)}
                    </div>

                    <div className="cal-grid">
                      {days.map((day, i) => {
                        if (!day) return <div key={i} />;

                        const date = new Date(d.getFullYear(), d.getMonth(), day);
                        const key = date.toISOString().slice(0, 10);

                        return (
                          <div
                            key={i}
                            className="cal-day"
                            onClick={() => {
                              setDepartDate(date);
                              setShowCalendar(false);
                            }}
                          >
                            <b>{day}</b>
                            <small>₹{priceMap[key] ?? "--"}</small>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
{/* ========= TRAVELLERS ========= */}
      {showTravellers && (
        <div className="calendar-overlay" onClick={() => setShowTravellers(false)}>
          <div className="traveller-box" onClick={e => e.stopPropagation()}>

            {/* ADULTS */}
            <div className="trav-row">
              <div className="trav-label">
                <b>ADULTS (12y +)</b>
                <span>on the day of travel</span>
              </div>
              <div className="trav-tiles">
                {[1,2,3,4,5,6,7,8,9].map(n => (
                  <button key={n} className={adults === n ? "active" : ""}
                    onClick={() => { setAdults(n); if (infants > n) setInfants(n); }}>
                    {n}
                  </button>
                ))}
                <button>&gt;9</button>
              </div>
            </div>
            {/* CHILDREN */}
            <div className="trav-row">
              <div className="trav-label">
                <b>CHILDREN (2y - 12y)</b>
                <span>on the day of travel</span>
              </div>
              <div className="trav-tiles">
                {[0,1,2,3,4,5,6].map(n => (
                  <button key={n} className={children === n ? "active" : ""}
                    onClick={() => setChildren(n)}>
                    {n}
                  </button>
                ))}
                <button>&gt;6</button>
              </div>
            </div>
            {/* INFANTS */}
            <div className="trav-row">
              <div className="trav-label">
                <b>INFANTS (below 2y)</b>
                <span>on the day of travel</span>
              </div>
              <div className="trav-tiles">
                {[0,1,2,3,4,5,6].map(n => (
                  <button key={n} className={infants === n ? "active" : ""}
                    onClick={() => n <= adults && setInfants(n)}>
                    {n}
                  </button>
                ))}
                <button>&gt;6</button>
              </div>
            </div>

             {/* CLASS */}
            <div className="trav-class">
              <b>CHOOSE TRAVEL CLASS</b>
              <div className="class-tiles">
                {CLASSES.map(c => (
                  <button key={c} className={travelClass === c ? "active" : ""}
                    onClick={() => setTravelClass(c)}>
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <button className="apply-btn" onClick={() => setShowTravellers(false)}>
              APPLY
            </button>
          </div>
        </div>
      )}
    </div>
  );
}