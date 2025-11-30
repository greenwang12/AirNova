import { BrowserRouter, Routes, Route } from "react-router-dom";
import AdminLogin from "../AdminLogin";
import AdminDashboard from "../AdminDashboard";
import PrivateRoute from "./PrivateRoute";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<AdminLogin />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <AdminDashboard />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<AdminLogin />} />
      </Routes>
    </BrowserRouter>
  );
}
