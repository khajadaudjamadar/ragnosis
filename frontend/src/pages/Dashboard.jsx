import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, auth } from "../api.js";

export default function Dashboard() {
  const user = auth.user();
  const fileRef = useRef(null);
  const [reports, setReports] = useState([]);
  const [title, setTitle] = useState("");
  const [patientEmail, setPatientEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = () => api.listReports().then((d) => setReports(d.reports)).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const upload = async (e) => {
    e.preventDefault();
    const file = fileRef.current.files[0];
    if (!file) return setError("Choose a PDF or TXT file first");
    const form = new FormData();
    form.append("file", file);
    if (title) form.append("title", title);
    if (patientEmail) form.append("patient_email", patientEmail);
    setBusy(true);
    setError("");
    try {
      await api.uploadReport(form);
      setTitle(""); setPatientEmail(""); fileRef.current.value = "";
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id) => {
    if (!confirm("Delete this report?")) return;
    await api.deleteReport(id);
    load();
  };

  return (
    <>
      <form className="card" onSubmit={upload}>
        <h2>Upload a medical report</h2>
        <input ref={fileRef} type="file" accept=".pdf,.txt,.md" />
        <input placeholder="Title (optional)" value={title} onChange={(e) => setTitle(e.target.value)} />
        {user.role === "doctor" && (
          <input type="email" placeholder="Patient email (optional, upload on behalf of patient)"
                 value={patientEmail} onChange={(e) => setPatientEmail(e.target.value)} />
        )}
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Processing… (first upload downloads models)" : "Upload"}</button>
      </form>

      <div className="card">
        <h2>{user.role === "doctor" ? "All patient reports" : "My reports"}</h2>
        {reports.length === 0 && <p className="muted">No reports yet.</p>}
        {reports.map((r) => (
          <div className="row" key={r.id}>
            <div>
              <Link to={`/reports/${r.id}`}><strong>{r.title}</strong></Link>
              <div className="muted">
                {r.owner_name} · {new Date(r.created_at).toLocaleString()} · {r.num_chunks} chunks
              </div>
            </div>
            <button className="btn ghost" onClick={() => remove(r.id)}>Delete</button>
          </div>
        ))}
      </div>
    </>
  );
}
