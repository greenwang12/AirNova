import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../api/api";
import FlightCard from "../components/FlightCard";

/* ========= TYPES ========= */

type Company = {
  Company_ID: number;
  Name: string;
};

type Flight = {
  Flight_ID: number;
  Flight_Code: string;
  Company_ID: number;
  Dept_Location: string;
  Arr_Location: string;
  Departure_Time: string;
  Arrival_Time: string;
  Price_Per_Seat: number;
  Stops: number;
  Available_Seats: number;
  company?: Company;
};

/* ========= COMPONENT ========= */

export default function Flights() {
  const [params] = useSearchParams();

  const departCity = params.get("depart") || "";
  const arriveCity = params.get("arrive") || "";

  const [flights, setFlights] = useState<Flight[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [showAllAirlines, setShowAllAirlines] = useState(false);

  const [filters, setFilters] = useState({
    maxPrice: 20000,
    stops: new Set<number>(),
    departTime: new Set<string>(),
    arriveTime: new Set<string>(),
    airlines: new Set<number>(),
  });

  /* ========= RESET ========= */

  const resetFilters = () => {
    setFilters({
      maxPrice: 20000,
      stops: new Set(),
      departTime: new Set(),
      arriveTime: new Set(),
      airlines: new Set(),
    });
  };

  /* ========= FETCH ========= */

  useEffect(() => {
    api.get("/companies/all").then(res => setCompanies(res.data));
  }, []);

  useEffect(() => {
    api
      .get("/flights/search", {
        params: { depart: departCity, arrive: arriveCity },
      })
      .then(res => setFlights(res.data));
  }, [departCity, arriveCity]);

  /* ========= MAP COMPANY ========= */

  const flightsWithCompany = useMemo(() => {
    return flights.map(f => ({
      ...f,
      company: companies.find(c => c.Company_ID === f.Company_ID),
    }));
  }, [flights, companies]);

  /* ========= FILTER ========= */

  const filteredFlights = useMemo(() => {
    let data = [...flightsWithCompany];

    data = data.filter(f => f.Price_Per_Seat <= filters.maxPrice);

    if (filters.stops.size > 0) {
      data = data.filter(f => filters.stops.has(f.Stops));
    }

    if (filters.departTime.size > 0) {
      data = data.filter(f => {
        const h = new Date(f.Departure_Time).getHours();
        if (filters.departTime.has("before6")) return h < 6;
        if (filters.departTime.has("morning")) return h >= 6 && h < 12;
        if (filters.departTime.has("afternoon")) return h >= 12 && h < 18;
        if (filters.departTime.has("evening")) return h >= 18;
        return true;
      });
    }

    if (filters.arriveTime.size > 0) {
      data = data.filter(f => {
        const h = new Date(f.Arrival_Time).getHours();
        if (filters.arriveTime.has("before6")) return h < 6;
        if (filters.arriveTime.has("morning")) return h >= 6 && h < 12;
        if (filters.arriveTime.has("afternoon")) return h >= 12 && h < 18;
        if (filters.arriveTime.has("evening")) return h >= 18;
        return true;
      });
    }

    if (filters.airlines.size > 0) {
      data = data.filter(f => filters.airlines.has(f.Company_ID));
    }

    return data.sort((a, b) => a.Price_Per_Seat - b.Price_Per_Seat);
  }, [flightsWithCompany, filters]);

  /* ========= HELPERS ========= */

  const toggleSet = <T,>(set: Set<T>, value: T) => {
    const next = new Set(set);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    return next;
  };

  /* ========= RENDER ========= */

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: 24,
        background: "linear-gradient(135deg,#b6d8ef,#b8e2e0)",
      }}
    >
      <div style={{ display: "flex", gap: 24 }}>

        {/* FILTERS */}
        <div style={sidebar}>
          <button style={resetBtn} onClick={resetFilters}>
            Reset Filters
          </button>

          <h3 style={title}>One Way Price</h3>
          <input
            type="range"
            min={0}
            max={20000}
            step={500}
            value={filters.maxPrice}
            onChange={e =>
              setFilters({ ...filters, maxPrice: Number(e.target.value) })
            }
          />

          <h3 style={title}>Stops From {departCity.toUpperCase()}</h3>
          {[0, 1].map(s => (
            <label key={s} style={row}>
              <input
                type="checkbox"
                checked={filters.stops.has(s)}
                onChange={() =>
                  setFilters({
                    ...filters,
                    stops: toggleSet(filters.stops, s),
                  })
                }
              />
              {s === 0 ? "Non Stop" : "1 Stop"}
            </label>
          ))}

          <h3 style={title}>Departure From {departCity.toUpperCase()}</h3>
          <div className="time-grid">
            {["before6", "morning", "afternoon", "evening"].map(t => (
              <button
                key={t}
                className={filters.departTime.has(t) ? "active" : ""}
                onClick={() =>
                  setFilters({
                    ...filters,
                    departTime: toggleSet(filters.departTime, t),
                  })
                }
              >
                {t === "before6" && "Before 6 AM"}
                {t === "morning" && "6AM to 12PM"}
                {t === "afternoon" && "12PM to 6PM"}
                {t === "evening" && "After 6PM"}
              </button>
            ))}
          </div>

          <h3 style={title}>Arrival At {arriveCity.toUpperCase()}</h3>
          <div className="time-grid">
            {["before6", "morning", "afternoon", "evening"].map(t => (
              <button
                key={t}
                className={filters.arriveTime.has(t) ? "active" : ""}
                onClick={() =>
                  setFilters({
                    ...filters,
                    arriveTime: toggleSet(filters.arriveTime, t),
                  })
                }
              >
                {t === "before6" && "Before 6 AM"}
                {t === "morning" && "6AM to 12PM"}
                {t === "afternoon" && "12PM to 6PM"}
                {t === "evening" && "After 6PM"}
              </button>
            ))}
          </div>

          <h3 style={title}>Airlines</h3>
          {(showAllAirlines ? companies : companies.slice(0, 3)).map(c => (
            <label key={c.Company_ID} style={row}>
              <input
                type="checkbox"
                checked={filters.airlines.has(c.Company_ID)}
                onChange={() =>
                  setFilters({
                    ...filters,
                    airlines: toggleSet(filters.airlines, c.Company_ID),
                  })
                }
              />
              {c.Name}
            </label>
          ))}

          {!showAllAirlines && companies.length > 3 && (
            <div
              style={{ color: "#1a73e8", cursor: "pointer", fontWeight: 600 }}
              onClick={() => setShowAllAirlines(true)}
            >
              + {companies.length - 3} more
            </div>
          )}
        </div>

        {/* FLIGHTS */}
        <div style={{ flex: 1 }}>
          <div className="flight-header">
            <div>AIRLINES</div>
            <div>DEPART</div>
            <div>DURATION</div>
            <div>ARRIVE</div>
            <div>PRICE</div>
          </div>

          {filteredFlights.map(f => (
            <FlightCard key={f.Flight_ID} f={f} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ========= STYLES ========= */

const sidebar = {
  width: 320,
  background: "#fff",
  padding: 24,
  borderRadius: 18,
  boxShadow: "0 6px 20px rgba(0,0,0,0.08)",
};

const title = { margin: "18px 0 10px", fontSize: 16, fontWeight: 700 };
const row = { display: "flex", gap: 8, marginBottom: 10 };
const resetBtn = {
  width: "100%",
  padding: 10,
  borderRadius: 10,
  border: "1px solid #e5e7eb",
  background: "#f9fafb",
  fontWeight: 600,
  cursor: "pointer",
  marginBottom: 12,
};
