import { useState } from "react";

const NAV = [
  { key: "dashboard", label: "Dashboard", icon: "\u2630" },
  { key: "safety", label: "Safety Monitor", icon: "\u26A1" },
  { key: "crack", label: "Crack Detection", icon: "\uD83E\uDEAA" },
  { key: "planning", label: "Project Planner", icon: "\uD83D\uDCCB" },
  { key: "valuation", label: "Real Estate Valuation", icon: "\uD83D\uDCB0" },
  { key: "daily", label: "Daily Site Assistant", icon: "\uD83D\uDCC5" },
  { key: "weather", label: "Weather Advisor", icon: "\uD83C\uDF24" },
  { key: "knowledgebase", label: "Knowledge Base", icon: "\uD83D\uDCDA" },
  { key: "chatbot", label: "Construction Chatbot", icon: "\uD83D\uDCAC" },
];

export default function Sidebar({ active, onSelect }) {
  const [scrolled, setScrolled] = useState(false);
  return (
    <aside className="sidebar" onScroll={() => setScrolled(true)}>
      <div className="brand">
        <span className="mark">C</span>
        <span>CONSTRUCT<span style={{ color: "#f97316", fontWeight: 900 }}>AI</span></span>
        <span style={{ marginLeft: "auto", fontSize: 11, opacity: 0.7 }}>v1.0.0</span>
      </div>
      <nav className="nav">
        {NAV.map((item) => (
          <button
            key={item.key}
            className={`nav-item ${active === item.key ? "active" : ""}`}
            onClick={() => onSelect(item.key)}
            title={item.label}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        AI-assisted preliminary assessments.<br />
        Not a substitute for certified professional inspection.
      </div>
    </aside>
  );
}
