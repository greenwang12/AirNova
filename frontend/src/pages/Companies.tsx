import { useEffect, useState } from "react";
import api from "../api/api";

type Company = {
  Company_ID: number;
  Name: string;
  Type: string;
  History?: string;
  Logo_URL?: string;
};

export default function Companies() {
  const [companies, setCompanies] = useState<Company[]>([]);

  useEffect(() => {
    api.get("/companies/all").then(res => setCompanies(res.data));
  }, []);

  return (
    <div className="container">
      <h2 style={{ marginTop: 0 }}>Airlines</h2>
      <div className="row" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))" }}>
        {companies.map((c) => (
          <div key={c.Company_ID} className="card">
            {c.Logo_URL && (
              <div style={{ display: "grid", placeItems: "center", marginBottom: 12 }}>
                <img src={c.Logo_URL} alt={c.Name} style={{ height: 50, objectFit: "contain" }} />
              </div>
            )}
            <h3 style={{ margin: "4px 0" }}>{c.Name}</h3>
            <p style={{ margin: "4px 0", opacity: 0.9 }}>{c.Type}</p>
            {c.History && <p style={{ margin: "6px 0", opacity: 0.8 }}>{c.History}</p>}
            <div style={{ color: "#00bcd4", fontWeight: 600, cursor: "pointer", marginTop: 8 }}>
              Add to compare +
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
