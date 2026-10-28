import { useState } from "react";
import { api } from "../api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

export default function RealEstateValuation() {
  const [form, setForm] = useState({
    city: "Pune",
    locality: "",
    property_type: "residential",
    area_value: "",
    area_unit: "sqft",
    property_age_years: "",
    condition: "average",
    amenities: "",
    parking: false,
    floor_number: "",
    total_floors: "",
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
      area_value: form.area_value ? Number(form.area_value) : undefined,
      property_age_years: form.property_age_years ? Number(form.property_age_years) : undefined,
      parking: form.parking === true || form.parking === "true",
      floor_number: form.floor_number ? Number(form.floor_number) : undefined,
      total_floors: form.total_floors ? Number(form.total_floors) : undefined,
    };

    try {
      const body = await api.valuation(payload);
      setResult(body);
    } catch (err) {
      setError(err.message || "Property valuation failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Real Estate Valuation (India)</h2>
        <p>
          Indicative property valuation in Indian Rupees with price per sq ft,
          rental yield, and ROI scenarios.
        </p>
      </div>

      <div className="grid-2">
        <div className="card" style={{ maxWidth: 720 }}>
          <div className="card-header">
            <h3>Property Details</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>City</label>
              <input value={form.city} onChange={(e) => handleChange("city", e.target.value)} />
            </div>
            <div className="field">
              <label>Locality / Neighbourhood</label>
              <input value={form.locality} onChange={(e) => handleChange("locality", e.target.value)} />
            </div>
            <div className="form-row">
              <div className="field">
                <label>Property Type</label>
                <select value={form.property_type} onChange={(e) => handleChange("property_type", e.target.value)}>
                  <option value="residential">Residential</option>
                  <option value="commercial">Commercial</option>
                  <option value="industrial">Industrial</option>
                  <option value="land">Land</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="field">
                <label>Condition</label>
                <select value={form.condition} onChange={(e) => handleChange("condition", e.target.value)}>
                  <option value="excellent">Excellent</option>
                  <option value="good">Good</option>
                  <option value="average">Average</option>
                  <option value="fair">Fair</option>
                  <option value="poor">Poor</option>
                </select>
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label>Area Value</label>
                <input type="number" value={form.area_value} onChange={(e) => handleChange("area_value", e.target.value)} />
              </div>
              <div className="field">
                <label>Area Unit</label>
                <select value={form.area_unit} onChange={(e) => handleChange("area_unit", e.target.value)}>
                  <option value="sqft">sqft</option>
                  <option value="sqm">sqm</option>
                  <option value="sqyard">sqyard</option>
                  <option value="acre">acre</option>
                  <option value="hectare">hectare</option>
                </select>
              </div>
            </div>
            <div className="field">
              <label>Property Age (Years)</label>
              <input type="number" value={form.property_age_years} onChange={(e) => handleChange("property_age_years", e.target.value)} />
            </div>
            <div className="field">
              <label>Amenities (comma-separated)</label>
              <input value={form.amenities} onChange={(e) => handleChange("amenities", e.target.value)} />
            </div>
            <div className="field" style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <input
                type="checkbox"
                checked={form.parking === true}
                onChange={(e) => handleChange("parking", e.target.checked)}
              />
              <label style={{ margin: 0, fontWeight: 600 }}>Parking Available</label>
            </div>
            <div style={{ marginTop: 20 }}>
              <button className="btn btn-primary" disabled={loading} style={{ width: "100%", padding: 12 }}>
                {loading ? <LoadingSpinner text="Valuing property..." /> : "Generate Valuation"}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Valuation Result</h3>
          </div>
          {!result && !loading && !error ? (
            <div className="empty-state">
              <h3>Waiting for input...</h3>
              <p>Enter property details to generate an indicative valuation.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Valuing property..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Indicative Market Value (INR):</strong>
                <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4 }}>
                  \u20B9{result.data.indicative_value_mid_inr?.toLocaleString()}
                </div>
                <div style={{ fontSize: 13, color: "#6b7280" }}>
                  Range: \u20B9{result.data.indicative_value_min_inr?.toLocaleString()} \u2013
                  \u20B9{result.data.indicative_value_max_inr?.toLocaleString()}
                </div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Estimated Price per Sq Ft:</strong> \u20B9{result.data.estimated_price_per_sqft_inr?.toLocaleString()}
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Area (sq ft):</strong> {result.data.area_sqft?.toLocaleString()} &nbsp;|&nbsp;
                <strong>Condition:</strong> {result.data.condition} &nbsp;|&nbsp;
                <strong>Age:</strong> {result.data.property_age_years ?? "Not provided"} years
              </div>

              {result.data.estimated_monthly_rent_inr != null && (
                <div style={{ marginBottom: 12 }}>
                  <strong>Estimated Monthly Rent:</strong> \u20B9{result.data.estimated_monthly_rent_inr?.toLocaleString()} &nbsp;|&nbsp;
                  <strong>Annual Rental Yield:</strong> {result.data.estimated_annual_rental_yield_percent?.toFixed(2)}%
                </div>
              )}

              {result.data.roi_scenarios && result.data.roi_scenarios.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>ROI Scenarios</strong>
                  <table className="table">
                    <thead>
                      <tr><th>Scenario</th><th>Annual Rent (INR)</th><th>Net Annual Income (INR)</th><th>ROI %</th></tr>
                    </thead>
                    <tbody>
                      {result.data.roi_scenarios.map((s, i) => (
                        <tr key={i}>
                          <td>{s.scenario}</td>
                          <td>\u20B9{s.annual_rental_income_inr?.toLocaleString()}</td>
                          <td>\u20B9{s.net_annual_income_inr?.toLocaleString()}</td>
                          <td>{s.roi_percent?.toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {result.data.market_assumptions && result.data.market_assumptions.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Market Assumptions</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.market_assumptions.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.appreciation_outlook && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 4 }}>Appreciation Outlook</strong>
                  <p style={{ fontSize: 13 }}>{result.data.appreciation_outlook}</p>
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
