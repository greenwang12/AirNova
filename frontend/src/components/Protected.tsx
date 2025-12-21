import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

export default function Protected({ children }: { children: ReactNode }) {
  const token = localStorage.getItem("token");
  return token ? <>{children}</> : <Navigate to="/login" />;
}
