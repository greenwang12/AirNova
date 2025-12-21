import { useNavigate } from "react-router-dom";

export default function BackButton() {
  const nav = useNavigate();

  return (
    <button
      onClick={() => nav(-1)}
      style={{
        marginBottom: 20,
        padding: "8px 16px",
        borderRadius: 10,
        border: "none",
        background: "rgba(255,255,255,0.2)",
        color: "white",
        cursor: "pointer",
      }}
    >
      ← Back
    </button>
  );
}
