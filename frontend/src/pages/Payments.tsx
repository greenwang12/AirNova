import { useState } from "react";

/* ================= COMPONENT ================= */

export default function PaymentStandalone() {
  const [method, setMethod] = useState("upi");
  const total = 5400;

  return (
    <div className="pay-root">
      <div className="pay-header">
        <h2>Secure Payment</h2>
        <span>256-bit encrypted · Demo Mode</span>
      </div>

      <div className="pay-grid">
        {/* LEFT */}
        <div>
          <div className="card summary">
            <h3>Trip Summary</h3>
            <p>Delhi → Mumbai</p>
            <small>1 Adult · Economy</small>
          </div>

          <div className="card methods">
            <h3>Choose Payment Method</h3>

            <PayOption
              active={method === "upi"}
              title="UPI"
              sub="Google Pay · PhonePe · Paytm"
              onClick={() => setMethod("upi")}
            />

            <PayOption
              active={method === "card"}
              title="Credit / Debit Card"
              sub="Visa · Mastercard · RuPay"
              onClick={() => setMethod("card")}
            />

            <PayOption
              active={method === "net"}
              title="Net Banking"
              sub="All major banks"
              onClick={() => setMethod("net")}
            />
          </div>

          {method === "upi" && <UPIForm />}
          {method === "card" && <CardForm />}
        </div>

        {/* RIGHT */}
        <div>
          <div className="card price sticky">
            <h3>Price Details</h3>

            <Line label="Base Fare" value={5000} />
            <Line label="Taxes & Fees" value={400} />

            <div className="divider" />

            <Line bold label="Total Amount" value={total} />

            <button
              className="pay-btn"
              onClick={() => alert("Demo payment successful")}
            >
              Pay ₹{total}
            </button>
          </div>
        </div>
      </div>

      <style>{css}</style>
    </div>
  );
}

/* ================= SMALL COMPONENTS ================= */

type PayOptionProps = {
  title: string;
  sub: string;
  active: boolean;
  onClick: () => void;
};

const PayOption = ({ title, sub, active, onClick }: PayOptionProps) => (
  <div className={`pay-option ${active ? "active" : ""}`} onClick={onClick}>
    <h4>{title}</h4>
    <p>{sub}</p>
  </div>
);


type LineProps = {
  label: string;
  value: string | number;
  bold?: boolean;
};

const Line = ({ label, value, bold = false }: LineProps) => (
  <div className={`line ${bold ? "bold" : ""}`}>
    <span>{label}</span>
    <span>{value}</span>
  </div>
);


const CardForm = () => (
  <div className="card form">
    <h3>Card Details</h3>
    <input placeholder="Card Number" />
    <div className="row">
      <input placeholder="MM / YY" />
      <input placeholder="CVV" />
    </div>
    <input placeholder="Name on Card" />
  </div>
);

const UPIForm = () => (
  <div className="card form">
    <h3>UPI ID</h3>
    <input placeholder="example@upi" />
  </div>
);

/* ================= STRONG CONTRAST CSS ================= */

const css = `
:root{
  --bg:#0f172a;
  --panel:#ffffff;
  --accent:#2563eb;
  --muted:#64748b;
}

/* PAGE */
.pay-root{
  background:linear-gradient(180deg,#0f172a,#1e293b);
  min-height:100vh;
  font-family:system-ui,-apple-system;
}

/* HEADER */
.pay-header{
  background:linear-gradient(135deg,#020617,#1e3a8a);
  color:#fff;
  padding:24px 40px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  box-shadow:0 12px 40px rgba(0,0,0,.5);
}

/* GRID */
.pay-grid{
  max-width:1200px;
  margin:44px auto;
  display:grid;
  grid-template-columns:2.2fr 1fr;
  gap:30px;
  padding:0 22px;
}

/* CARDS */
.card{
  background:var(--panel);
  border-radius:20px;
  padding:22px;
  margin-bottom:20px;
  box-shadow:0 18px 45px rgba(0,0,0,.25);
}

.summary{
  border-left:6px solid var(--accent);
}

.methods{
  border-left:6px solid #22c55e;
}

.form{
  border-left:6px solid #f59e0b;
}

.price{
  border-left:6px solid var(--accent);
  box-shadow:0 25px 60px rgba(37,99,235,.45);
}

/* PAYMENT OPTION */
.option{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:16px 18px;
  border-radius:14px;
  cursor:pointer;
  margin-top:14px;
  border:2px solid #e5e7eb;
  background:#f8fafc;
  transition:.25s ease;
}

.option:hover{
  transform:translateY(-1px);
  background:#eef2ff;
}

.option.active{
  border-color:var(--accent);
  background:#eff6ff;
}

.option p{
  margin:4px 0 0;
  font-size:13px;
  color:var(--muted);
}

.chev{
  font-size:22px;
  color:var(--accent);
}

/* PRICE */
.line{
  display:flex;
  justify-content:space-between;
  margin:10px 0;
  font-size:14px;
}

.bold{
  font-weight:800;
  font-size:18px;
}

.divider{
  height:1px;
  background:#e5e7eb;
  margin:16px 0;
}

/* BUTTON */
.pay-btn{
  margin-top:20px;
  width:100%;
  padding:18px;
  border:none;
  border-radius:999px;
  background:linear-gradient(135deg,#2563eb,#1d4ed8);
  color:#fff;
  font-size:17px;
  font-weight:800;
  cursor:pointer;
  box-shadow:0 16px 40px rgba(37,99,235,.6);
}

.pay-btn:hover{
  filter:brightness(1.05);
  transform:translateY(-1px);
}

/* INPUTS */
input{
  width:100%;
  padding:14px;
  border-radius:12px;
  border:2px solid #cbd5f5;
  margin-top:12px;
  font-size:14px;
}

input:focus{
  outline:none;
  border-color:var(--accent);
  box-shadow:0 0 0 4px rgba(37,99,235,.2);
}

/* LAYOUT */
.row{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
}

.sticky{
  position:sticky;
  top:96px;
}

/* MOBILE */
@media(max-width:900px){
  .pay-grid{grid-template-columns:1fr}
  .sticky{position:static}
}
`;
