import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../api/api";
import FlightCard from "../components/FlightCard";

/* ========= TYPES ========= */

type Company = {
  Company_ID: number;
  Name: string;
  Logo_URL?: string;
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
  const navigate = useNavigate();

  const departCity = params.get("depart") || "";
  const arriveCity = params.get("arrive") || "";

  const [flights, setFlights] = useState<Flight[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);

  const [filters, setFilters] = useState({
    morning: false,
    nonstop: false,
    airlines: new Set<number>(),
  });

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

    if (filters.morning) {
      data = data.filter(f => {
        const h = new Date(f.Departure_Time).getHours();
        return h >= 5 && h < 12;
      });
    }

    if (filters.nonstop) {
      data = data.filter(f => f.Stops === 0);
    }

    if (filters.airlines.size > 0) {
      data = data.filter(f => filters.airlines.has(f.Company_ID));
    }

    return data.sort((a, b) => a.Price_Per_Seat - b.Price_Per_Seat);
  }, [flightsWithCompany, filters]);

  /* ========= RENDER ========= */

  return (
<div
  style={{
    minHeight: "100vh",
    padding: 24,
    background: "linear-gradient(135deg, #b6d8efff, #b8e2e0ff)",
  }}
>`1 ,2
      <div style={{ display: "flex", gap: 24 }}>

        {/* FILTER SIDEBAR */}
        <div style={sidebar}>
          <h3 style={title}>Departure From {departCity.toUpperCase()}</h3>
          <h3 style={title}>Arrival At {arriveCity.toUpperCase()}</h3>

          <h3 style={title}>Airlines</h3>
          {companies.map(c => (
            <label key={c.Company_ID} style={row}>
              <input
                type="checkbox"
                checked={filters.airlines.has(c.Company_ID)}
                onChange={e => {
                  const next = new Set(filters.airlines);

                  if (e.target.checked) {
                    next.add(c.Company_ID);
                  } else {
                    next.delete(c.Company_ID);
                  }

                  setFilters({ ...filters, airlines: next });
                }}
              />
              {c.Name}
            </label>
          ))}

          <h3 style={title}>Popular Filters</h3>

          <label style={row}>
            <input
              type="checkbox"
              checked={filters.nonstop}
              onChange={e =>
                setFilters({ ...filters, nonstop: e.target.checked })
              }
            />
            Non Stop
          </label>

          <label style={row}>
            <input
              type="checkbox"
              checked={filters.morning}
              onChange={e =>
                setFilters({ ...filters, morning: e.target.checked })
              }
            />
            Morning Flights
          </label>
        </div>

        {/* FLIGHT LIST */}
        <div style={{ flex: 1 }}>
          <h2 style={{ marginBottom: 20 }}>Flights</h2>

          {filteredFlights.map(f => (
            <div
              key={f.Flight_ID}
             
              onClick={() =>  navigate(`/book/${f.Flight_ID}`)}
              style={{ cursor: "pointer", marginBottom: 16 }}
            >
              <FlightCard f={f} />
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

/* ========= STYLES ========= */

const sidebar = {
  width: 300,
  background: "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
  padding: 20,
  borderRadius: 14,
  position: "sticky" as const,
  top: 90,
  boxShadow: "0 6px 20px rgba(0,0,0,0.08)",
};

const title = {
  margin: "20px 0 12px",
  fontSize: 16,
  fontWeight: 700,
};

const row = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 10,
};
