import { useNavigate } from "react-router-dom";

export default function Profile() {
  const nav = useNavigate();

  return (
    <div className="profile-page">
      <div className="profile-card">
        <button className="back" onClick={() => nav(-1)}>← Back</button>

        {/* Avatar */}
        <div className="avatar">A</div>

        <h2>AeroNova User</h2>
        <p className="muted">guest@aeronova.com</p>

        <div className="info">
          <div>
            <span>Role</span>
            <strong>Customer</strong>
          </div>
          <div>
            <span>Member Since</span>
            <strong>2025</strong>
          </div>
        </div>

        <button className="logout" onClick={() => nav("/login")}>
          Logout
        </button>
      </div>

      <style>{`
        .profile-page {
          min-height: calc(100vh - 80px);
          display: flex;
          justify-content: center;
          align-items: center;
          background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
        }

        .profile-card {
          width: 420px;
          padding: 30px;
          border-radius: 20px;
          background: rgba(255,255,255,0.12);
          backdrop-filter: blur(10px);
          color: white;
          text-align: center;
          box-shadow: 0 25px 60px rgba(0,0,0,0.35);
        }

        .back {
          background: rgba(255,255,255,0.15);
          border: none;
          color: white;
          padding: 6px 14px;
          border-radius: 999px;
          cursor: pointer;
          margin-bottom: 16px;
        }

        .avatar {
          width: 90px;
          height: 90px;
          margin: 0 auto 14px;
          border-radius: 50%;
          background: linear-gradient(135deg,#2563eb,#38bdf8);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 36px;
          font-weight: 800;
        }

        .muted {
          opacity: 0.8;
          margin-bottom: 20px;
        }

        .info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 22px;
          opacity: 0.9;
        }

        .info div {
          text-align: left;
        }

        .info span {
          display: block;
          font-size: 13px;
          opacity: 0.7;
        }

        .logout {
          width: 100%;
          padding: 12px;
          border-radius: 999px;
          border: none;
          background: #ef4444;
          color: white;
          font-weight: 700;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
}
