import { useState } from "react";

const KNOWLEDGE_CATEGORIES = [
  {
    id: "materials",
    title: "Construction Materials",
    items: [
      {
        term: "Cement",
        description:
          "A binding material used in concrete and mortar. Ordinary Portland Cement (OPC) is the most common type. Typically supplied in 50 kg bags.",
      },
      {
        term: "Sand",
        description:
          "Fine aggregate used in concrete, mortar, and plastering. Should be clean, free from clay and organic impurities. River sand or M-sand (manufactured sand) are common.",
      },
      {
        term: "Aggregate",
        description:
          "Coarse aggregate (crushed stone, gravel) provides bulk and strength to concrete. Typically graded by nominal size (e.g., 20 mm, 12 mm).",
      },
      {
        term: "Steel (Rebar)",
        description:
          "Reinforcing steel bars used in RCC (reinforced cement concrete) to carry tensile loads. Common grades include Fe415 and Fe500.",
      },
      {
        term: "Bricks / Blocks",
        description:
          "Masonry units for walls. Clay bricks, fly ash bricks, and concrete blocks (solid/hollow) are widely used in Indian construction.",
      },
    ],
  },
  {
    id: "practices",
    title: "Building Practices",
    items: [
      {
        term: "Curing",
        description:
          "The process of maintaining adequate moisture and temperature in freshly placed concrete to ensure proper hydration and strength development. Typically 7–14 days.",
      },
      {
        term: "Formwork",
        description:
          "Temporary or permanent molds into which concrete is poured. Must be strong, watertight, and properly braced before concreting.",
      },
      {
        term: "Scaffolding",
        description:
          "Temporary structure used to support workers and materials at height. Must be stable, fully planked, with guardrails and toe boards.",
      },
      {
        term: "RCC Work",
        description:
          "Reinforced Cement Concrete combines concrete (compression) with steel reinforcement (tension). Proper cover, spacing, and placement of rebar are critical.",
      },
      {
        term: "Plastering",
        description:
          "Application of cement mortar to walls and ceilings for a smooth, protective finish. Typical thickness: 12–20 mm depending on surface.",
      },
    ],
  },
  {
    id: "terminology",
    title: "Common Terminology",
    items: [
      {
        term: "Plot Area",
        description:
          "The total area of the land parcel as recorded in land documents. Distinct from built-up area.",
      },
      {
        term: "Built-up Area",
        description:
          "The total floor area of the building including walls, measured at floor level. Distinct from plot area.",
      },
      {
        term: "FSI / FAR",
        description:
          "Floor Space Index (Floor Area Ratio) — the ratio of total built-up area to plot area. Determines maximum allowable construction.",
      },
      {
        term: "RCC",
        description:
          "Reinforced Cement Concrete — concrete with embedded steel reinforcement to resist tensile stresses.",
      },
      {
        term: "PCC",
        description:
          "Plain Cement Concrete — concrete without reinforcement, used for foundations, flooring, and bedding.",
      },
    ],
  },
  {
    id: "safety",
    title: "Safety Procedures",
    items: [
      {
        term: "PPE",
        description:
          "Personal Protective Equipment: hard hat, safety boots, high-visibility vest, safety glasses, gloves, and fall protection where required.",
      },
      {
        term: "Work at Height",
        description:
          "Any work above 1.8–2 meters requires edge protection, guardrails, toe boards, and/or a fall arrest system. Never work on unguarded edges.",
      },
      {
        term: "LOTO",
        description:
          "Lockout/Tagout — procedure to isolate energy sources (electrical, mechanical) before maintenance to prevent accidental startup.",
      },
      {
        term: "Toolbox Talk",
        description:
          "A short daily safety meeting before work begins to review hazards, tasks, and precautions for the day.",
      },
      {
        term: "Emergency Assembly Point",
        description:
          "A designated safe area where workers gather in case of fire, accident, or evacuation. Must be marked and known to all.",
      },
    ],
  },
];

export default function KnowledgeBase() {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");

  const filteredItems = KNOWLEDGE_CATEGORIES.flatMap((cat) =>
    cat.items.filter(
      (item) =>
        (activeCategory === "all" || activeCategory === cat.id) &&
        (item.term.toLowerCase().includes(search.toLowerCase()) ||
          item.description.toLowerCase().includes(search.toLowerCase()))
    )
  );

  return (
    <div className="page">
      <div className="page-header">
        <h2>Construction Knowledge Base</h2>
        <p>
          Reference information on construction materials, building practices,
          terminology, and safety procedures.
        </p>
      </div>

      <div className="card" style={{ maxWidth: 900, marginBottom: 24 }}>
        <div className="field">
          <label>Search terms, materials, or practices</label>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="e.g. cement, curing, PPE, FSI..."
          />
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
          <button
            className={`btn btn-outline btn-sm ${activeCategory === "all" ? "btn-primary" : ""}`}
            onClick={() => setActiveCategory("all")}
          >
            All
          </button>
          {KNOWLEDGE_CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              className={`btn btn-outline btn-sm ${activeCategory === cat.id ? "btn-primary" : ""}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              {cat.title}
            </button>
          ))}
        </div>
      </div>

      <div className="grid-2">
        {KNOWLEDGE_CATEGORIES.map((cat) => (
          <div key={cat.id} className="card">
            <div className="card-header">
              <h3>{cat.title}</h3>
            </div>
            {cat.items
              .filter(
                (item) =>
                  (activeCategory === "all" || activeCategory === cat.id) &&
                  (item.term.toLowerCase().includes(search.toLowerCase()) ||
                    item.description.toLowerCase().includes(search.toLowerCase()))
              )
              .map((item) => (
                <div key={item.term} style={{ marginBottom: 14, paddingBottom: 14, borderBottom: "1px solid #e5e7e5" }}>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{item.term}</div>
                  <div style={{ fontSize: 13, color: "#4b5563" }}>{item.description}</div>
                </div>
              ))}
            {cat.items.filter(
                (item) =>
                  (activeCategory === "all" || activeCategory === cat.id) &&
                  (item.term.toLowerCase().includes(search.toLowerCase()) ||
                    item.description.toLowerCase().includes(search.toLowerCase()))
              ).length === 0 && (
              <div className="empty-state" style={{ padding: 24 }}>
                <h3>No results found</h3>
                <p>Try a different search term or category.</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredItems.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-header">
            <h3>Search Results ({filteredItems.length})</h3>
          </div>
          {filteredItems.map((item) => (
            <div key={item.term} style={{ padding: 14, borderBottom: "1px solid #e5e7e5" }}>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{item.term}</div>
              <div style={{ fontSize: 13, color: "#4b5563" }}>{item.description}</div>
            </div>
          ))}
        </div>
      )}

      <div className="disclaimer">
        Reference information only. Not a substitute for qualified professional advice on structural,
        regulatory, or safety-critical construction decisions.
      </div>
    </div>
  );
}
