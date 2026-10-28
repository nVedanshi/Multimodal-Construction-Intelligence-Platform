import { useEffect, useState } from "react";
import { api } from "../api";

const statCards = [
  { label: "Site Safety Assessments", value: "--", icon: "\u26A1" },
  { label: "Crack Analyses", value: "--", icon: "\uD83E\uDEAA" },
  { label: "Project Plans", value: "--", icon: "\uD83D\uDCCB" },
  { label: "Property Valuations", value: "--", icon: "\uD83D\uDCB0" },
  { label: "Knowledge Articles", value: "--", icon: "\uD83D\uDCDA" },
  { label: "Chat Sessions", value: "--", icon: "\uD83D\uDCAC" },
];

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.health()
      .then(setStatus)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of construction intelligence features and system status.</p>
      </div>

      {error && (
        <div className="alert alert-error">
          Backend unreachable: {error}. Start the FastAPI backend to use the platform.
        </div>
      )}

      <div className="summary-grid">
        {statCards.map((card) => (
          <div key={card.label} className="summary-card">
            <div className="label">{card.label}</div>
            <div className="value">{card.value}</div>
          </div>
        ))}
      </div>

      <div className="grid-3">
        <CardWithAction
          title="Site Safety Monitoring"
          icon="\u26A1"
          description="Upload a site photograph and optional observation log to receive a structured safety hazard report."
          to="safety"
        />
        <CardWithAction
          title="Structural Crack Detection"
          icon="\uD83E\uDEAA"
          description="Analyse crack photographs and receive a preliminary crack classification and severity report."
          to="crack"
        />
        <CardWithAction
          title="Project Planner"
          icon="\uD83D\uDCCB"
          description="Generate a project plan with material requirements, INR cost estimate, and schedule."
          to="planning"
        />
        <CardWithAction
          title="Real Estate Valuation"
          icon="\uD83D\uDCB0"
          description="Indicative property valuation in Indian Rupees with rental yield and ROI scenarios."
          to="valuation"
        />
        <CardWithAction
          title="Daily Site Assistant"
          icon="\uD83D\uDCC5"
          description="Generate a structured daily site action plan with prioritized tasks and safety checks."
          to="daily"
        />
        <CardWithAction
          title="Weather Advisor"
          icon="\uD83C\uDF24"
          description="Weather-aware GO / NO-GO / REVIEW advisories for construction activities."
          to="weather"
        />
        <CardWithAction
          title="Knowledge Base"
          icon="\uD83D\uDCDA"
          description="Reference information on construction materials, building practices, terminology, and safety procedures."
          to="knowledgebase"
        />
        <CardWithAction
          title="Construction Chatbot"
          icon="\uD83D\uDCAC"
          description="Conversational AI assistant for construction questions with session history."
          to="chatbot"
        />
      </div>

      {status && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-header">
            <h3>Backend Status</h3>
            <span className={`mode-tag ${status.demo_mode ? "demo" : ""}`}>
              {status.demo_mode ? "DEMO MODE" : "LIVE"}
            </span>
          </div>
          <table className="table">
            <tbody>
              <tr><td>Service</td><td>{status.name}</td></tr>
              <tr><td>Version</td><td>{status.version}</td></tr>
              <tr><td>Environment</td><td>{status.environment}</td></tr>
              <tr><td>Groq configured</td><td>{String(status.groq_configured)}</td></tr>
              <tr><td>Vision available</td><td>{String(status.vision_available)}</td></tr>
              <tr><td>Demo mode</td><td>{String(status.demo_mode)}</td></tr>
            </tbody>
          </table>
          <p className="disclaimer">
            In demo mode, all AI results are deterministic samples. No live provider is called.
            Configure GROQ_API_KEY and set DEMO_MODE=false for live analysis.
          </p>
        </div>
      )}
    </div>
  );
}

function CardWithAction({ title, icon, description, to }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 style={{ display: "flex", alignItems: "center", gap: 8, margin: 0 }}>
          {icon} {title}
        </h3>
      </div>
      <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 16 }}>{description}</p>
      <button
        className="btn btn-outline btn-sm"
        onClick={() => (window.location.hash = "#/" + to)}
      >
        Open {title}
      </button>
    </div>
  );
}
