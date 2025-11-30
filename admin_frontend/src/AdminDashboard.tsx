/* eslint-disable */
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Plus, Users, Plane, Wallet, Search } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getToken } from "./auth";

const API_BASE: string = (window as any).__API_BASE__ || "http://127.0.0.1:8000";
const ADMIN_TOKEN_KEY = "admin_token";

type Flight = {
  Flight_ID: number;
  Company_ID?: number;
  Dept_Location: string;
  Arr_Location: string;
  Departure_Time: string;
  Arrival_Time: string;
  Seats: number;
  Status?: string;
};

type Booking = {
  Booking_ID: number;
  Customer_ID: number;
  Flight_ID: number;
  Seats: number;
  Status: string;
  Created_At: string;
  Payment?: number;
};

type Customer = {
  Customer_ID: number;
  Name: string;
  Email: string;
};

function Stat({ num, label, icon }: { num: React.ReactNode; label: string; icon: React.ReactNode }) {
  return (
    <div className="flex items-center gap-4 p-4 bg-white border rounded-xl shadow-sm">
      <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white">{icon}</div>
      <div>
        <div className="text-xl font-semibold">{num}</div>
        <div className="text-sm text-gray-500">{label}</div>
      </div>
    </div>
  );
}

export default function AdminDashboard(): JSX.Element {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [query, setQuery] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fForm, setFForm] = useState({
    Company_ID: 1,
    Dept_Location: "",
    Arr_Location: "",
    Departure_Time: "",
    Arrival_Time: "",
    Seats: 100,
  });

  useEffect(() => {
    fetchAll();
  }, []);

  async function authFetch(path: string, opts: RequestInit = {}) {
    const token = getToken() || localStorage.getItem(ADMIN_TOKEN_KEY);
    const headers: any = { ...(opts.headers || {}) };
    headers["Content-Type"] = "application/json";
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(API_BASE + path, { ...opts, headers });
    if (!res.ok) {
      // simple handling: if unauthorized -> redirect to login
      if (res.status === 401 || res.status === 403) {
        alert("Not authorized. Please login as admin.");
        window.location.href = "/login";
        return null;
      }
      const txt = await res.text();
      console.error("API error", path, txt);
      return null;
    }
    return res.json();
  }

  async function fetchAll() {
    setLoading(true);
    try {
      const [f, b, c] = await Promise.all([
        authFetch("/flights/all"),
        authFetch("/bookings/all"),
        authFetch("/customers/all"),
      ]);
      setFlights((f as Flight[]) || []);
      setBookings((b as Booking[]) || []);
      setCustomers((c as Customer[]) || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  function filteredFlights() {
    if (!query) return flights;
    const q = query.toLowerCase();
    return flights.filter(
      (f) =>
        f.Dept_Location?.toLowerCase().includes(q) ||
        f.Arr_Location?.toLowerCase().includes(q) ||
        String(f.Flight_ID).includes(q)
    );
  }

  async function handleAddFlight(e: React.FormEvent) {
    e.preventDefault();
    const payload = {
      Company_ID: Number(fForm.Company_ID),
      Dept_Location: fForm.Dept_Location,
      Arr_Location: fForm.Arr_Location,
      Departure_Time: fForm.Departure_Time,
      Arrival_Time: fForm.Arrival_Time,
      Seats: Number(fForm.Seats),
    };
    const res = await authFetch("/flights/add", { method: "POST", body: JSON.stringify(payload) });
    if (res) {
      setFlights((s) => [res as Flight, ...s]);
      setShowAdd(false);
      setFForm({ Company_ID: 1, Dept_Location: "", Arr_Location: "", Departure_Time: "", Arrival_Time: "", Seats: 100 });
    }
  }

  async function handleCancelFlight(f: Flight) {
    const res = await authFetch(`/flights/${f.Flight_ID}/status`, {
      method: "PATCH",
      body: JSON.stringify({ Status: "Cancelled" }),
    });
    if (res) {
      setFlights((old) => old.map((it) => (it.Flight_ID === f.Flight_ID ? { ...it, Status: "Cancelled" } : it)));
    }
  }

  const revenue = bookings.reduce((s, b) => s + (b.Payment || 0), 0);

  return (
    <div className="p-6 min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <header className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
            <p className="text-sm text-gray-600">Manage flights, bookings and customers.</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center px-3 py-2 bg-white border rounded-lg">
              <Search size={18} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search flights by airport or id"
                className="ml-2 outline-none bg-transparent"
              />
            </div>

            <button onClick={() => setShowAdd(true)} className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg">
              <Plus size={16} /> Create Flight
            </button>

            <button
              onClick={() => {
                localStorage.removeItem(ADMIN_TOKEN_KEY);
                alert("Logged out");
                window.location.href = "/login";
              }}
              className="px-3 py-2 rounded-lg border"
            >
              Logout
            </button>
          </div>
        </header>

        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-3 gap-4 mb-6">
          <Stat num={flights.length} label="Flights" icon={<Plane size={20} />} />
          <Stat num={bookings.length} label="Bookings" icon={<Users size={20} />} />
          <Stat num={`₹${revenue.toFixed(2)}`} label="Revenue" icon={<Wallet size={20} />} />
        </motion.div>

        <div className="grid grid-cols-3 gap-6">
          <section className="col-span-2">
            <div className="bg-white rounded-2xl p-4 shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Flights</h3>
                <div className="text-sm text-gray-500">{flights.length} total</div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-xs text-gray-500 uppercase">
                    <tr>
                      <th className="px-3 py-2">ID</th>
                      <th className="px-3 py-2">From</th>
                      <th className="px-3 py-2">To</th>
                      <th className="px-3 py-2">Dept</th>
                      <th className="px-3 py-2">Arr</th>
                      <th className="px-3 py-2">Seats</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredFlights().map((f) => (
                      <tr key={f.Flight_ID} className="border-t">
                        <td className="px-3 py-2">{f.Flight_ID}</td>
                        <td className="px-3 py-2">{f.Dept_Location}</td>
                        <td className="px-3 py-2">{f.Arr_Location}</td>
                        <td className="px-3 py-2">{f.Departure_Time ? new Date(f.Departure_Time).toLocaleString() : "-"}</td>
                        <td className="px-3 py-2">{f.Arrival_Time ? new Date(f.Arrival_Time).toLocaleString() : "-"}</td>
                        <td className="px-3 py-2">{f.Seats}</td>
                        <td className="px-3 py-2">{f.Status || "On-Time"}</td>
                        <td className="px-3 py-2">
                          <div className="flex gap-2">
                            <button onClick={() => handleCancelFlight(f)} className="px-2 py-1 rounded bg-red-50 text-red-600">Cancel</button>
                            <button onClick={() => navigator.clipboard.writeText(JSON.stringify(f))} className="px-2 py-1 rounded border">Copy</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-6 bg-white rounded-2xl p-4 shadow">
              <h3 className="text-lg font-semibold mb-2">Bookings (recent)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-xs text-gray-500 uppercase">
                    <tr>
                      <th className="px-3 py-2">ID</th>
                      <th className="px-3 py-2">Customer</th>
                      <th className="px-3 py-2">Flight</th>
                      <th className="px-3 py-2">Seats</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bookings.slice(0, 15).map((b) => (
                      <tr key={b.Booking_ID} className="border-t">
                        <td className="px-3 py-2">{b.Booking_ID}</td>
                        <td className="px-3 py-2">{b.Customer_ID}</td>
                        <td className="px-3 py-2">{b.Flight_ID}</td>
                        <td className="px-3 py-2">{b.Seats}</td>
                        <td className="px-3 py-2">{b.Status}</td>
                        <td className="px-3 py-2">{new Date(b.Created_At).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <aside className="col-span-1 space-y-4">
            <div className="bg-white p-4 rounded-2xl shadow">
              <h4 className="font-semibold mb-3">Quick actions</h4>
              <div className="flex flex-col gap-2">
                <button onClick={() => setShowAdd(true)} className="w-full py-2 rounded bg-indigo-600 text-white flex items-center justify-center gap-2"><Plus size={14}/> Add flight</button>
                <button onClick={() => alert('Export not implemented in demo')} className="w-full py-2 rounded border">Export CSV</button>
                <button onClick={() => alert('Run price prediction (demo)')} className="w-full py-2 rounded border">Run price prediction</button>
              </div>
            </div>

            <div className="bg-white p-4 rounded-2xl shadow">
              <h4 className="font-semibold mb-3">Customers</h4>
              <div className="space-y-2 max-h-56 overflow-auto">
                {customers.slice(0, 8).map((c) => (
                  <div key={c.Customer_ID} className="flex items-center justify-between">
                    <div className="text-sm">
                      <div className="font-medium">{c.Name}</div>
                      <div className="text-xs text-gray-500">{c.Email}</div>
                    </div>
                    <div className="text-xs text-gray-400">id: {c.Customer_ID}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-4 rounded-2xl shadow">
              <h4 className="font-semibold mb-3">Traffic (30d)</h4>
              <div style={{ height: 120 }}>
                <ResponsiveContainer width="100%" height={120}>
                  <LineChart data={[ { name: 'd-7', uv: 40 }, { name: 'd-6', uv: 50 }, { name: 'd-5', uv: 45 }, { name: 'd-4', uv: 70 }, { name: 'd-3', uv: 60 }, { name: 'd-2', uv: 85 }, { name: 'd-1', uv: 95 } ]}>
                    <XAxis dataKey="name" hide />
                    <YAxis hide />
                    <Tooltip />
                    <Line type="monotone" dataKey="uv" stroke="#7c9cff" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </aside>
        </div>

        {showAdd && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="bg-white p-6 rounded-2xl w-[680px] max-w-full">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Create Flight</h3>
                <button onClick={() => setShowAdd(false)} className="text-gray-400">✕</button>
              </div>

              <form onSubmit={handleAddFlight} className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm">From</label>
                  <input required value={fForm.Dept_Location} onChange={(e) => setFForm({ ...fForm, Dept_Location: e.target.value })} className="w-full p-2 border rounded" />
                </div>
                <div>
                  <label className="text-sm">To</label>
                  <input required value={fForm.Arr_Location} onChange={(e) => setFForm({ ...fForm, Arr_Location: e.target.value })} className="w-full p-2 border rounded" />
                </div>

                <div>
                  <label className="text-sm">Departure (ISO)</label>
                  <input required value={fForm.Departure_Time} onChange={(e) => setFForm({ ...fForm, Departure_Time: e.target.value })} className="w-full p-2 border rounded" placeholder="2025-12-01T08:30:00" />
                </div>
                <div>
                  <label className="text-sm">Arrival (ISO)</label>
                  <input required value={fForm.Arrival_Time} onChange={(e) => setFForm({ ...fForm, Arrival_Time: e.target.value })} className="w-full p-2 border rounded" placeholder="2025-12-01T11:30:00" />
                </div>

                <div>
                  <label className="text-sm">Seats</label>
                  <input type="number" value={fForm.Seats} onChange={(e) => setFForm({ ...fForm, Seats: Number(e.target.value) })} className="w-full p-2 border rounded" />
                </div>
                <div>
                  <label className="text-sm">Company ID</label>
                  <input type="number" value={fForm.Company_ID} onChange={(e) => setFForm({ ...fForm, Company_ID: Number(e.target.value) })} className="w-full p-2 border rounded" />
                </div>

                <div className="col-span-2 flex gap-2 justify-end mt-2">
                  <button type="button" onClick={() => setShowAdd(false)} className="px-4 py-2 rounded border">Cancel</button>
                  <button type="submit" className="px-4 py-2 rounded bg-indigo-600 text-white">Create</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
