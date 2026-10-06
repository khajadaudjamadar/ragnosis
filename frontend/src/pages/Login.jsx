import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, auth } from "../api.js";

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "patient" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data = mode === "login"
        ? await api.login(form.email, form.password)
        : await api.register(form);
      auth.save(data.token, data.user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card narrow" onSubmit={submit}>
      <h2>{mode === "login" ? "Sign in" : "Create account"}</h2>
      {mode === "register" && (
        <>
          <input placeholder="Full name" value={form.name} onChange={set("name")} required />
          <select value={form.role} onChange={set("role")}>
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
          </select>
        </>
      )}
      <input type="email" placeholder="Email" value={form.email} onChange={set("email")} required />
      <input type="password" placeholder="Password (min 6 chars)" value={form.password}
             onChange={set("password")} required />
      {error && <p className="error">{error}</p>}
      <button className="btn" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? "Sign in" : "Register"}</button>
      <p className="muted">
        {mode === "login" ? "No account? " : "Already registered? "}
        <a href="#" onClick={(e) => { e.preventDefault(); setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "Register" : "Sign in"}
        </a>
      </p>
    </form>
  );
}
