import { useState } from "react";
import { api } from "../api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function ProjectPlanner() {
  const [form, setForm] = useState({
    project_name: "",
    location: "",
    construction_type: "residential",
    intended_use: "house",
    num_floors: 2,
    plot_area: "",
    plot_area_unit: "sqm",
    built_up_area: "",
    built_up_area_unit: "sqm",
    quality_level: "medium",
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

    const payload = {
      ...form,
      num_floors: Number(form.num_floors) || 1,
      plot_area: form.plot_area ? Number(form.plot_area) : undefined,
      built_up_area: form.built_up_area ? Number(form.built_up_area) : undefined,
    };

    try {
      const body = await api.planning(payload);
      setResult(body);
    } catch (err) {
      setError(err.message || "Project planning failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Project Planner</h2>
        <p>
          Generate a consolidated construction project plan with material requirements,
          category-wise cost estimate in INR, schedule, milestones, and recommendations.
        </p>
      </div>

      <div className="grid-2">
        <div className="card" style={{ maxWidth: 720 }}>
          <div className="card-header">
            <h3>Project Parameters</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Project Name</label>
              <input value={form.project_name} onChange={(e) => handleChange("project_name", e.target.value)} />
            </div>
            <div className="form-row">
              <div className="field">
                <label>Location</label>
                <input value={form.location} onChange={(e) => handleChange("location", e.target.value)} />
              </div>
              <div className="field">
                <label>Number of Floors</label>
                <input type="number" value={form.num_floors} onChange={(e) => handleChange("num_floors", e.target.value)} />
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label>Construction Type</label>
                <select value={form.construction_type} onChange={(e) => handleChange("construction_type", e.target.value)}>
                  <option value="residential">Residential</option>
                  <option value="commercial">Commercial</option>
                  <option value="industrial">Industrial</option>
                  <option value="mixed_use">Mixed Use</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="field">
                <label>Intended Use</label>
                <select value={form.intended_use} onChange={(e) => handleChange("intended_use", e.target.value)}>
                  <option value="house">House</option>
                  <option value="apartment">Apartment</option>
                  <option value="office">Office</option>
                  <option value="shop">Shop</option>
                  <option value="warehouse">Warehouse</option>
                  <option value="factory">Factory</option>
                  <option value="school">School</option>
                  <option value="hospital">Hospital</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label>Plot Area</label>
                <input type="number" value={form.plot_area} onChange={(e) => handleChange("plot_area", e.target.value)} />
              </div>
              <div className="field">
                <label>Unit</label>
                <select value={form.plot_area_unit} onChange={(e) => handleChange("plot_area_unit", e.target.value)}>
                  <option value="sqm">sqm</option>
                  <option value="sqft">sqft</option>
                  <option value="acre">acre</option>
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label>Approx. Built-up Area</label>
                <input type="number" value={form.built_up_area} onChange={(e) => handleChange("built_up_area", e.target.value)} />
                <span className="field-hint">Distinct from plot area.</span>
              </div>
              <div className="field">
                <label>Unit</label>
                <select value={form.built_up_area_unit} onChange={(e) => handleChange("built_up_area_unit", e.target.value)}>
                  <option value="sqm">sqm</option>
                  <option value="sqft">sqft</option>
                </select>
              </div>
            </div>
            <div className="field">
              <label>Quality Preference</label>
              <select value={form.quality_level} onChange={(e) => handleChange("quality_level", e.target.value)}>
                <option value="standard">Standard</option>
                <option value="medium">Medium</option>
                <option value="premium">Premium</option>
              </select>
            </div>
            <div style={{ marginTop: 20 }}>
              <button className="btn btn-primary" disabled={loading} style={{ width: "100%", padding: 12 }}>
                {loading ? <LoadingSpinner text="Generating plan..." /> : "Generate Project Plan"}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Project Plan</h3>
          </div>
          {!result && !loading && !error ? (
            <div className="empty-state">
              <h3>Waiting for input...</h3>
              <p>Enter project parameters to generate a plan.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Generating plan..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Project:</strong> {result.data.project_name}{" "}
                <span style={{ marginLeft: 8, fontSize: 12, color: "#6b7280" }}>{result.data.construction_type}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Built-up Area:</strong>{" "}
                {result.data.built_up_area_sqm != null ? result.data.built_up_area_sqm + " sqm" : "Not provided"} &nbsp;|&nbsp;
                <strong>Plot Area:</strong>{" "}
                {result.data.plot_area_sqm != null ? result.data.plot_area_sqm + " sqm" : "Not provided"} &nbsp;|&nbsp;
                <strong>Floors:</strong> {result.data.num_floors}
              </div>

              <div style={{ marginBottom: 12 }}>
                <strong style={{ display: "block", marginBottom: 6 }}>Material Requirements</strong>
                <table className="table">
                  <thead>
                    <tr><th>Material</th><th>Quantity</th><th>Unit</th><th>Est. Cost (INR)</th></tr>
                  </thead>
                  <tbody>
                    {result.data.material_requirements.map((m, i) => (
                      <tr key={i}>
                        <td>{m.material}</td>
                        <td>{m.quantity}</td>
                        <td>{m.unit}</td>
                        <td>\u20B9{m.estimated_cost_inr?.toLocaleString() || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div style={{ marginBottom: 12 }}>
                <strong style={{ display: "block", marginBottom: 6 }}>Cost Estimate (INR)</strong>
                <table className="table">
                  <tbody>
                    <tr><td>Total Material Cost</td><td>\u20B9{result.data.total_material_cost_inr?.toLocaleString()}</td></tr>
                    <tr><td>Labour Cost</td><td>\u20B9{result.data.labour_cost_inr?.toLocaleString()}</td></tr>
                    <tr><td>Contingency</td><td>\u20B9{result.data.contingency_inr?.toLocaleString()}</td></tr>
                    <tr><td><strong>Total Estimated</strong></td><td><strong>\u20B9{result.data.total_estimated_cost_inr?.toLocaleString()}</strong></td></tr>
                  </tbody>
                </table>
              </div>

              {result.data.schedule_phases && result.data.schedule_phases.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Schedule Phases</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.schedule_phases.map((p, i) => (
                      <li key={i}>{p.phase} {p.week != null ? "(Week " + p.week + ")" : ""}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.recommendations && result.data.recommendations.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Recommendations</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.recommendations.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.visualization && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Conceptual Layout</strong>
                  <ConceptualDiagram viz={result.data.visualization} />
                  <p style={{ fontSize: 12, color: "#6b7280", marginTop: 8 }}>
                    {result.data.visualization.note}
                  </p>
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

function ConceptualDiagram({ viz }) {
  const plotW = 340;
  const plotH = 220;
  const margin = 30;
  const buaRatio = viz.built_up_area_sqm && viz.plot_area_sqm
    ? Math.min(viz.built_up_area_sqm / viz.plot_area_sqm, 0.6)
    : 0.4;
  const bW = plotW * buaRatio;
  const bH = plotH * buaRatio;
  const floors = viz.num_floors || 1;
  const floorH = bH / Math.max(floors, 1);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
      <svg width={plotW + margin * 2} height={plotH + margin * 2 + 40} viewBox={`0 0 ${plotW + margin * 2} ${plotH + margin * 2 + 40}`}>
        {/* Plot boundary */}
        <rect
          x={margin}
          y={margin}
          width={plotW}
          height={plotH}
          fill="#e5e7e5"
          stroke="#9ca3af"
          strokeWidth="2"
          strokeDasharray="6 4"
        />
        <text x={margin + plotW / 2} y={margin + plotH + 18} textAnchor="middle" fontSize="12" fill="#6b7280">
          Plot: {viz.plot_area_sqm != null ? viz.plot_area_sqm.toLocaleString() : "-"} sqm
        </text>

        {/* Building footprint */}
        <rect
          x={margin + (plotW - bW) / 2}
          y={margin + (plotH - bH) / 2}
          width={bW}
          height={bH}
          fill="#f97316"
          opacity={0.85}
          stroke="#ea580c"
          strokeWidth="2"
        />

        {/* Floors */}
        {Array.from({ length: Math.min(floors, 4) }).map((_, i) => (
          <rect
            key={i}
            x={margin + (plotW - bW) / 2 + 6}
            y={margin + (plotH - bH) / 2 + i * floorH + 6}
            width={bW - 12}
            height={floorH - 12}
            fill="none"
            stroke="#fff"
            strokeWidth="1"
            strokeDasharray="3 3"
          />
        ))}

        <text x={margin + plotW / 2} y={margin - 8} textAnchor="middle" fontSize="13" fontWeight="700" fill="#1f2937">
          Conceptual Block Layout
        </text>
        <text x={margin + (plotW - bW) / 2 + bW / 2} y={margin + plotH / 2} textAnchor="middle" fontSize="11" fill="#ffffff" fontWeight="700">
          Built-up: {viz.built_up_area_sqm != null ? viz.built_up_area_sqm.toLocaleString() : "-"} sqm
        </text>
        <text x={margin + plotW / 2} y={margin + plotH + 36} textAnchor="middle" fontSize="11" fill="#6b7280">
          {floors} Floor{floors > 1 ? "s" : ""}
        </text>
      </svg>
    </div>
  );
}
