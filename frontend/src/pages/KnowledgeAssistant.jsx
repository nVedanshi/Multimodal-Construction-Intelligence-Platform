import { useState, useRef, useEffect } from "react";
import { api } from "../api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function KnowledgeAssistant() {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [result, error, history]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    setError(null);
    setResult(null);
    setLoading(true);

    const userMsg = message;
    setHistory((h) => [...h, { role: "user", content: userMsg }]);
    setMessage("");

    try {
      const body = await api.knowledge({ message: userMsg, history });
      setResult(body);
      setHistory((h) => [...h, { role: "assistant", content: body.data.response }]);
    } catch (err) {
      setError(err.message || "Knowledge assistant failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Construction Chatbot</h2>
        <p>
          Ask questions about construction materials, building practices, planning,
          estimation, maintenance, and safety procedures. Conversation history is
          kept for the current session.
        </p>
      </div>

      <div className="grid-2">
        <div className="card" style={{ maxWidth: 720, height: 520, display: "flex", flexDirection: "column" }}>
          <div className="card-header">
            <h3>Conversation</h3>
          </div>
          <div className="chat-box" ref={scrollRef}>
            {history.map((m, i) => (
              <div key={i} className={`message ${m.role}`}>
                <div className="bubble">{m.content}</div>
              </div>
            ))}
            {loading && (
              <div className="message assistant">
                <div className="bubble"><LoadingSpinner text="Thinking..." /></div>
              </div>
            )}
            {error && (
              <div className="message assistant">
                <div className="bubble" style={{ color: "#991b1b" }}>
                  Error: {error}
                </div>
              </div>
            )}
            {result && !error && history[history.length - 1]?.role !== "assistant" ? null : null}
          </div>
          <div className="chat-input">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit(e)}
              placeholder="Ask a construction question..."
              disabled={loading}
            />
            <button className="btn btn-primary" onClick={handleSubmit} disabled={loading || !message.trim()}>
              {loading ? <span style={{ fontSize: 14 }}>\u2026</span> : "Send"}
            </button>
          </div>
          <div className="disclaimer" style={{ marginTop: 8 }}>
            General construction information only. Not a substitute for qualified professional advice on structural, regulatory, or safety-critical matters.
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Last Result</h3>
          </div>
          {!result && !loading && !error ? (
            <div className="empty-state">
              <h3>Waiting for input...</h3>
              <p>Ask a question to see the assistant response.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Thinking..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>
              </div>
              <div style={{ whiteSpace: "pre-wrap", fontSize: 14, lineHeight: 1.6 }}>{result.data.response}</div>
              {result.data.sources && result.data.sources.length > 0 && (
                <div style={{ marginTop: 10 }}>
                  <strong style={{ display: "block", marginBottom: 4, fontSize: 12 }}>Sources</strong>
                  <ul style={{ marginLeft: 20, fontSize: 12 }}>
                    {result.data.sources.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="disclaimer">
                {result.data.disclaimer}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
