import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { auth } from "./api.js";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ReportChat from "./pages/ReportChat.jsx";

function Protected({ children }) {
  return auth.token() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const navigate = useNavigate();
  const user = auth.user();

  const logout = () => {
    auth.clear();
    navigate("/login");
  };

  return (
    <>
      <header className="nav">
        <Link to="/" className="brand">RAGnosis</Link>
        {user && (
          <div className="nav-right">
            <span>{user.name} · {user.role}</span>
            <button className="btn ghost" onClick={logout}>Log out</button>
          </div>
        )}
      </header>
      <main className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
          <Route path="/reports/:id" element={<Protected><ReportChat /></Protected>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}
