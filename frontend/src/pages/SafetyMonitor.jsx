import { useState } from "react";
import { api } from "../api";
import ImageUpload from "../components/upload/ImageUpload";
import RiskBadge from "../components/common/RiskBadge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function SafetyMonitor() {
  const [observation, setObservation] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleImage = (file) => {
    setImageFile(file);
    setImagePreview(file ? URL.createObjectURL(file) : null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    const formData = new FormData();
    if (observation) formData.append("observation_log", observation);
    if (imageFile) formData.append("site_photo", imageFile);

    try {
      const body = await api.safety(formData);
      setResult(body);
    } catch (err) {
      setError(err.message || "Safety analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Site Safety Monitor</h2>
        <p>
          Upload a construction site photograph and optional observation log to receive a
          structured AI-assisted safety hazard report.
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h3>Input Data</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Observation Log</label>
              <textarea
                rows="5"
                value={observation}
                onChange={(e) => setObservation(e.target.value)}
                placeholder="Describe the scene e.g. Workers on scaffold without harness..."
              />
              <span className="field-hint">Optional description of the scene.</span>
            </div>
            <ImageUpload label="Site Photo (Optional)" accept="image/*" onFile={handleImage} maxSizeMB={10} />
            {imagePreview && (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
              </div>
            )}
            <div style={{ marginTop: 20 }}>
              <ButtonSubmit loading={loading} disabled={loading}>
                {loading ? <LoadingSpinner text="Analyzing hazards..." /> : "Analyze Hazards"}
              </ButtonSubmit>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Analysis Results</h3>
          </div>
          {!result && !loading && !error ? (
            <div className="empty-state">
              <h3>Waiting for input...</h3>
              <p>Submit a site photo and/or observation log to begin analysis.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Analyzing site safety..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>{" "}
                <span style={{ fontSize: 12, color: "#6b7280" }}>{result.meta.request_id}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Summary:</strong> <p style={{ display: "inline", margin: 0 }}>{result.data.summary}</p>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Overall Risk Level:</strong>{" "}
                <RiskBadge level={result.data.overall_risk_level} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Severity:</strong> {result.data.severity}
              </div>

              {result.data.identified_hazards && result.data.identified_hazards.length > 0 && (
                <div>
                  <strong style={{ display: "block", marginBottom: 6 }}>Identified Hazards</strong>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Hazard</th><th>Category</th><th>Severity</th><th>Observable</th><th>Observation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.data.identified_hazards.map((h, i) => (
                        <tr key={i}>
                          <td>{h.hazard}</td>
                          <td>{h.category}</td>
                          <td>{h.severity}</td>
                          <td>{String(h.observable)}</td>
                          <td>{h.observation}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {result.data.supporting_visual_observations && result.data.supporting_visual_observations.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Supporting Visual Observations</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.supporting_visual_observations.map((o, i) => (
                      <li key={i}>{o}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.recommended_ppe && result.data.recommended_ppe.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Recommended PPE</strong>
                  <span style={{ marginRight: 8 }}>{result.data.recommended_ppe.join(", ")}</span>
                </div>
              )}

              {result.data.corrective_actions && result.data.corrective_actions.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Corrective Actions</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.corrective_actions.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.uncertainty_notes && (
                <div style={{ marginTop: 12 }}>
                  <strong style={{ display: "block", marginBottom: 4 }}>Uncertainty / Limitations</strong>
                  <p style={{ fontSize: 13, color: "#92400e" }}>{result.data.uncertainty_notes}</p>
                </div>
              )}

              <div className="disclaimer">
                {result.data.disclaimer || "AI-assisted preliminary assessment only. Not a certified safety inspection."}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ButtonSubmit({ children, loading, disabled }) {
  return (
    <button
      className="btn btn-primary"
      disabled={disabled}
      style={{ width: "100%", padding: 12 }}
    >
      {children}
    </button>
  );
}
