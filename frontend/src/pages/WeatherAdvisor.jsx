import { useState } from "react";
import { api } from "../api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function WeatherAdvisor() {
  const [form, setForm] = useState({
    activity: "",
    location: "",
    planned_time: "",
    weather_conditions: "",
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const body = await api.weather(form);
      setResult(body);
    } catch (err) {
      setError(err.message || "Weather advisory failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Weather-Aware Advisory</h2>
        <p>
          Receive a GO / NO-GO / REVIEW REQUIRED recommendation for a construction
          activity based on location and weather conditions.
        </p>
      </div>

      <div className="grid-2">
        <div className="card" style={{ maxWidth: 720 }}>
          <div className="card-header">
            <h3>Activity &amp; Conditions</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Construction Activity</label>
              <input value={form.activity} onChange={(e) => handleChange("activity", e.target.value)} placeholder="e.g. concrete pouring" />
            </div>
            <div className="field">
              <label>Location</label>
              <input value={form.location} onChange={(e) => handleChange("location", e.target.value)} placeholder="e.g. Pune, India" />
            </div>
            <div className="field">
              <label>Planned Time</label>
              <input type="datetime-local" value={form.planned_time} onChange={(e) => handleChange("planned_time", e.target.value)} />
            </div>
            <div className="field">
              <label>Weather Conditions (optional, if live data unavailable)</label>
              <textarea rows="2" value={form.weather_conditions} onChange={(e) => handleChange("weather_conditions", e.target.value)} placeholder="e.g. Rain, wind 12 m/s" />
              <span className="field-hint">Leave blank to attempt live weather fetch (requires backend WEATHER_ENABLED + API key).</span>
            </div>
            <div style={{ marginTop: 20 }}>
              <button className="btn btn-primary" disabled={loading} style={{ width: "100%", padding: 12 }}>
                {loading ? <LoadingSpinner text="Checking weather..." /> : "Get Advisory"}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Advisory</h3>
          </div>
          {!result && !loading && !error ? (
            <div className="empty-state">
              <h3>Waiting for input...</h3>
              <p>Enter activity and location to receive a weather advisory.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Checking weather..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>{" "}
                <span style={{ fontSize: 12, color: "#6b7280" }}>{result.data.weather_source}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Activity:</strong> {result.data.activity} &nbsp;|&nbsp;
                <strong>Location:</strong> {result.data.location} &nbsp;|&nbsp;
                {result.data.planned_time && <span>Planned: {result.data.planned_time}</span>}
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Decision:</strong>{" "}
                <span className={`decision-badge decision-${result.data.decision.replace(/\s+/g, "-")}`}>
                  {result.data.decision}
                </span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Reasoning:</strong>
                <p style={{ marginTop: 4, fontSize: 13 }}>{result.data.reasoning}</p>
              </div>

              {result.data.hazards && result.data.hazards.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Hazards</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.hazards.map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.precautions && result.data.precautions.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Precautions</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.precautions.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.mitigation_actions && result.data.mitigation_actions.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Mitigation Actions</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.mitigation_actions.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.weather_timestamp && (
                <div style={{ marginBottom: 12, fontSize: 12, color: "#6b7280" }}>
                  Weather data timestamp: {new Date(result.data.weather_timestamp * 1000).toLocaleString()}
                </div>
              )}

              {result.data.data_limitations && result.data.data_limitations.length > 0 && (
                <div>
                  <strong style={{ display: "block", marginBottom: 4 }}>Data Limitations</strong>
                  <ul style={{ marginLeft: 20, fontSize: 12, color: "#6b7280" }}>
                    {result.data.data_limitations.map((d, i) => (
                      <li key={i}>{d}</li>
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
