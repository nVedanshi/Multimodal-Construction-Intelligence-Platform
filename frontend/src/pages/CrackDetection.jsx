import { useState } from "react";
import { api } from "../api";
import ImageUpload from "../components/upload/ImageUpload";
import RiskBadge from "../components/common/RiskBadge";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function CrackDetection() {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [surfaceType, setSurfaceType] = useState("");
  const [elementType, setElementType] = useState("");
  const [ageYears, setAgeYears] = useState("");
  const [notedConcerns, setNotedConcerns] = useState("");
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
    if (imageFile) formData.append("image", imageFile);
    if (surfaceType) formData.append("surface_type", surfaceType);
    if (elementType) formData.append("element_type", elementType);
    if (ageYears) formData.append("age_years", ageYears);
    if (notedConcerns) formData.append("noted_concerns", notedConcerns);

    try {
      const body = await api.crack(formData);
      setResult(body);
    } catch (err) {
      setError(err.message || "Crack analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Structural Crack Detection</h2>
        <p>
          Upload a photograph of a wall, concrete, column, or beam surface to receive a
          preliminary crack analysis report.
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h3>Input Data</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <ImageUpload label="Crack Photograph (Optional)" accept="image/*" onFile={handleImage} maxSizeMB={10} />
            {imagePreview && (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
              </div>
            )}
            <div className="form-row" style={{ marginTop: 16 }}>
              <div className="field">
                <label>Surface Type</label>
                <select value={surfaceType} onChange={(e) => setSurfaceType(e.target.value)}>
                  <option value="">Not specified</option>
                  <option value="wall">Wall</option>
                  <option value="concrete">Concrete</option>
                  <option value="column">Column</option>
                  <option value="beam">Beam</option>
                  <option value="slab">Slab</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="field">
                <label>Element Type</label>
                <select value={elementType} onChange={(e) => setElementType(e.target.value)}>
                  <option value="">Not specified</option>
                  <option value="load-bearing">Load-bearing</option>
                  <option value="non-load-bearing">Non-load-bearing</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
            </div>
            <div className="field">
              <label>Approximate Age (Years)</label>
              <input type="number" value={ageYears} onChange={(e) => setAgeYears(e.target.value)} />
            </div>
            <div className="field">
              <label>Noted Concerns</label>
              <textarea rows="2" value={notedConcerns} onChange={(e) => setNotedConcerns(e.target.value)} />
            </div>
            <div style={{ marginTop: 20 }}>
              <button className="btn btn-primary" disabled={loading} style={{ width: "100%", padding: 12 }}>
                {loading ? <LoadingSpinner text="Analyzing crack..." /> : "Analyze Crack"}
              </button>
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
              <p>Upload a crack photograph to begin analysis.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Analyzing crack..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>{" "}
                <span style={{ fontSize: 12, color: "#6b7280" }}>{result.meta.request_id}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Classification:</strong> {result.data.crack_classification}
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Preliminary Severity:</strong>{" "}
                <RiskBadge level={result.data.preliminary_severity} />
              </div>
              {result.data.apparent_orientation && (
                <div style={{ marginBottom: 12 }}>
                  <strong>Apparent Orientation:</strong> {result.data.apparent_orientation}
                </div>
              )}
              {result.data.continuity && (
                <div style={{ marginBottom: 12 }}>
                  <strong>Continuity:</strong> {result.data.continuity}
                </div>
              )}

              {result.data.observable_characteristics && result.data.observable_characteristics.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Observable Characteristics</strong>
                  <table className="table">
                    <thead>
                      <tr><th>Characteristic</th><th>Description</th><th>Confidence</th></tr>
                    </thead>
                    <tbody>
                      {result.data.observable_characteristics.map((c, i) => (
                        <tr key={i}>
                          <td>{c.characteristic}</td>
                          <td>{c.description}</td>
                          <td>{c.confidence}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {result.data.possible_causes && result.data.possible_causes.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Possible Causes</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.possible_causes.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.potential_risks && result.data.potential_risks.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Potential Risks</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.potential_risks.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.recommended_next_steps && result.data.recommended_next_steps.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Recommended Next Steps</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.recommended_next_steps.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.needs_professional_inspection && (
                <div style={{ marginBottom: 12, padding: 10, background: "#fef3c7", borderRadius: 6, border: "1px solid #fcd34d" }}>
                  <strong>\u26A0 Professional Inspection Recommended</strong>
                  <p style={{ margin: 4, fontSize: 13 }}>
                    A qualified structural engineer should assess this crack. Image-only analysis cannot
                    establish structural safety or the actual cause.
                  </p>
                </div>
              )}

              {result.data.uncertainty && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 4 }}>Uncertainty / Limitations</strong>
                  <p style={{ fontSize: 13, color: "#92400e" }}>{result.data.uncertainty}</p>
                </div>
              )}

              <div className="disclaimer">
                {result.data.disclaimer || "Image-only preliminary assessment. Consult a qualified structural engineer."}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
