import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";

import Splash from "./pages/Splash";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Flights from "./pages/Flights";
import SearchFlights from "./pages/SearchFlights";
import Bookings from "./pages/MyBookings";
import Payment from "./pages/Payments";
import Companies from "./pages/Companies";
import Weather from "./pages/Weather";
import PricePredict from "./pages/PricePredict";
import MyTrips from "./pages/MyTrips";
import BookFlight from "./pages/BookFlight";
import Protected from "./components/Protected";
import Header from "./components/Header";
import Profile from "./pages/Profile";

function AppRoutes() {
  const { pathname } = useLocation();

  const hideHeader =
    pathname === "/" ||
    pathname === "/login" ||
    pathname.startsWith("/payment");

  return (
    <>
      {!hideHeader && <Header />}

      <Routes>
        {/* ---------- PUBLIC ROUTES ---------- */}
        <Route path="/" element={<Splash />} />
        <Route path="/login" element={<Login />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/SearchFlights" element={<SearchFlights />} />
        <Route path="/flights" element={<Flights />} />
        <Route path="/companies" element={<Companies />} />
        <Route path="/weather" element={<Weather />} />
        <Route path="/predict" element={<PricePredict />} />

        {/* ---------- PROTECTED ROUTES ---------- */}
        <Route
          path="/book/:id"
          element={
            <Protected>
              <BookFlight />
            </Protected>
          }
        />

        <Route
          path="/payment"
          element={
            <Protected>
              <Payment />
            </Protected>
          }
        />

        <Route
          path="/bookings/my"
          element={
            <Protected>
              <Bookings />
            </Protected>
          }
        />

        <Route
          path="/trips"
          element={
            <Protected>
              <MyTrips />
            </Protected>
          }
        />

        <Route
          path="/profile"
          element={
            <Protected>
              <Profile />
            </Protected>
          }
        />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
