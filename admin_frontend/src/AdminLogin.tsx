/* eslint-disable */
import React, { useState } from "react";
import { saveToken } from "./auth";

const API_BASE = (window as any).__API_BASE__ || "http://127.0.0.1:8000";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin(e: any) {
    e.preventDefault();

    const res = await fetch(API_BASE + "/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) return alert("Invalid login");

    const data = await res.json();
    saveToken(data.token);
    window.location.href = "/dashboard";
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white shadow p-8 rounded-xl w-[360px]">
        <h1 className="text-2xl font-bold mb-4">Admin Login</h1>

        <form className="space-y-4" onSubmit={handleLogin}>
          <input
            type="email"
            className="w-full border p-2 rounded"
            placeholder="Email"
            required
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            className="w-full border p-2 rounded"
            placeholder="Password"
            required
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="w-full bg-indigo-600 text-white py-2 rounded">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
