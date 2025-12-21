import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

export default function Login() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const [toast, setToast] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const navigate = useNavigate();

  const showToast = (type: "success" | "error", text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 2600);
  };

  const submit = async () => {
    if (!email || !password || (mode === "register" && (!name || !phone))) {
      showToast("error", "Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      if (mode === "login") {
        const res = await api.post("/auth/login", { email, password });

        localStorage.setItem("token", res.data.access_token);
        localStorage.setItem(
          "user",
          JSON.stringify({
            id: res.data.customer_id,
            name: res.data.name,
            email: res.data.email,
            role: res.data.role,
          })
        );

        showToast("success", "Login successful");

        const redirect =
          localStorage.getItem("redirectAfterLogin") || "/dashboard";

        setTimeout(() => {
          navigate(redirect);
          localStorage.removeItem("redirectAfterLogin");
        }, 800);
      } else {
        await api.post("/auth/register", { name, email, phone, password });
        showToast("success", "Registered successfully. Please login.");
        setMode("login");
      }
    } catch {
      showToast("error", "Invalid details or server error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth">
      <style>{`
        .auth {
          height: 100vh;
          display: flex;
          justify-content: center;
          align-items: center;
          font-family: system-ui;
          background:
            linear-gradient(rgba(15,32,39,0.75), rgba(15,32,39,0.75)),
            url("/flight.png") center/cover no-repeat;
          position: relative;
        }

        .box {
          background: rgba(255,255,255,0.1);
          padding: 40px;
          border-radius: 16px;
          backdrop-filter: blur(12px);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
          width: 400px;
        }

        input,
        button {
          width: 260px;
        }

        input {
          padding: 12px;
          border-radius: 8px;
          border: none;
          outline: none;
        }

        button {
          padding: 12px;
          border-radius: 999px;
          border: none;
          font-weight: 600;
          cursor: pointer;
        }

        button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        h2 {
          color: #ffffff;
          font-weight: 700;
        }

        p {
          color: #e5e7eb;
          font-size: 0.85rem;
          cursor: pointer;
        }

        p:hover {
          color: #ffffff;
          text-decoration: underline;
        }

        /* ===== Premium Toast ===== */
        .toast {
          position: absolute;
          top: 22px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          gap: 10px;

          padding: 12px 18px;
          border-radius: 12px;
          font-size: 0.9rem;
          font-weight: 500;

          background: transparent;
          backdrop-filter: blur(12px);
          color: #fcfff5ff;

          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          animation: toastIn 0.35s ease, toastOut 0.35s ease 2.3s forwards;
        }

        .toast.success .dot { background: #22c55e; }
        .toast.error .dot { background: #ef4444; }

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        @keyframes toastIn {
          from { opacity: 0; transform: translate(-50%, -8px); }
          to { opacity: 1; transform: translate(-50%, 0); }
        }

        @keyframes toastOut {
          to { opacity: 0; transform: translate(-50%, -8px); }
        }
      `}</style>

      {toast && (
        <div className={`toast ${toast.type}`}>
          <span className="dot" />
          {toast.text}
        </div>
      )}

      <div className="box">
        <h2>{mode === "login" ? "Login" : "Register"}</h2>

        {mode === "register" && (
          <>
            <input placeholder="Full Name" value={name} onChange={e => setName(e.target.value)} />
            <input placeholder="Phone" value={phone} onChange={e => setPhone(e.target.value)} />
          </>
        )}

        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />

        <button onClick={submit} disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
        </button>

        <p onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Create new account" : "Already have an account?"}
        </p>
      </div>
    </div>
  );
}
