import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";

export default function ReportChat() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    api.getReport(id).then((d) => setReport(d.report)).catch((e) => setError(e.message));
    api.history(id).then((d) => setMessages(d.messages)).catch(() => {});
  }, [id]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const ask = async (e) => {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;
    setBusy(true);
    setError("");
    try {
      const d = await api.ask(id, q);
      setMessages((m) => [...m, { question: q, answer: d.answer, sources: d.sources }]);
      setQuestion("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (!report) return <p>{error || "Loading…"}</p>;

  return (
    <>
      <Link to="/">← Back</Link>
      <div className="card">
        <h2>{report.title}</h2>
        <p className="muted">{report.owner_name} · {report.filename}</p>
        {report.summary && <><h3>Summary</h3><p>{report.summary}</p></>}
        {report.entities?.length > 0 && (
          <>
            <h3>Medical entities</h3>
            <div className="tags">
              {report.entities.map((e, i) => <span className="tag" key={i}>{e.text} <small>{e.label}</small></span>)}
            </div>
          </>
        )}
        <details>
          <summary>Report preview</summary>
          <pre>{report.preview}</pre>
        </details>
      </div>

      <div className="card">
        <h2>Ask about this report</h2>
        {messages.map((m, i) => (
          <div key={i} className="msg">
            <p className="q">{m.question}</p>
            <p className="a">{m.answer}</p>
            <details>
              <summary>Sources ({m.sources.length})</summary>
              {m.sources.map((s) => (
                <pre key={s.chunk}>[chunk {s.chunk} · score {s.score}] {s.text}</pre>
              ))}
            </details>
          </div>
        ))}
        <div ref={endRef} />
        {error && <p className="error">{error}</p>}
        <form className="ask" onSubmit={ask}>
          <input placeholder="e.g. What is my hemoglobin level?" value={question}
                 onChange={(e) => setQuestion(e.target.value)} />
          <button className="btn" disabled={busy}>{busy ? "Thinking…" : "Ask"}</button>
        </form>
        <p className="muted">AI answers are informational only. Confirm with your doctor.</p>
      </div>
    </>
  );
}
