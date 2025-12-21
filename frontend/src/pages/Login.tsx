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
  const navigate = useNavigate();

  const submit = async () => {
    if (!email || !password || (mode === "register" && (!name || !phone))) {
      alert("Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      if (mode === "login") {
        const res = await api.post("/auth/login", { email, password });
        localStorage.setItem("token", res.data.access_token);


// 👇 store user info (needed for dashboard & recommendations)
        localStorage.setItem(
         "user",
          JSON.stringify({
          id: res.data.customer_id,
          name: res.data.name,
          email: res.data.email,
          role: res.data.role,
        })
      );

        const redirect = localStorage.getItem("redirectAfterLogin") || "/dashboard";
        navigate(redirect);
        localStorage.removeItem("redirectAfterLogin");
      } else {
        await api.post("/auth/register", { name, email, phone, password });
        alert("Registered successfully. Please login.");
        setMode("login");
      }
    } catch {
      alert("Invalid details or server error");
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
        }

        .box {
        background: rgba(255,255,255,0.1);
        padding: 40px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 17px;
        width: 400px; /* outer width */
        }

        input,
        button {
          width: 260px; /* inner width */
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
          font-weight: bold;
          cursor: pointer;
        }
        h2, p {
          color: white;
          text-align: center;
        }
        p {
          font-size: 0.85rem;
          cursor: pointer;
        }
      `}</style>

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
