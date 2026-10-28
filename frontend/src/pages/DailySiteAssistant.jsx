import { useState, useEffect } from "react";
import { api } from "../api";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorMessage from "../components/common/ErrorMessage";

const PRIORITY_STYLE = {
  high: { bg: "#fee2e2", text: "#991b1b" },
  medium: { bg: "#fef3c7", text: "#92400e" },
  low: { bg: "#dcfce7", text: "#166534" },
};

export default function DailySiteAssistant() {
  const [form, setForm] = useState({
    date: new Date().toISOString().slice(0, 10),
    project_phase: "",
    planned_activities: "",
    workforce_availability: "",
    materials: "",
    equipment: "",
    site_conditions: "",
    constraints: "",
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  // Fetch persisted tasks when the date changes so completion survives refreshes.
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const body = await api.getDailySiteTasks(form.date);
        if (body && body.data && Array.isArray(body.data)) {
          setResult((prev) => {
            if (!prev) return prev;
            const persisted = new Map(
              body.data.map((t) => [t.task_id, t.completed])
            );
            return {
              ...prev,
              data: {
                ...prev.data,
                prioritized_tasks: prev.data.prioritized_tasks.map((t) => ({
                  ...t,
                  completed: persisted.has(t.id) ? persisted.get(t.id) : t.completed,
                })),
              },
            };
          });
        }
      } catch (err) {
        // Non-fatal: continue without persisted tasks.
      }
    };
    fetchTasks();
  }, [form.date]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const body = await api.dailySite(form);
      setResult(body);
    } catch (err) {
      setError(err.message || "Daily site planning failed.");
    } finally {
      setLoading(false);
    }
  };

  const toggleTask = async (id) => {
    if (!result) return;
    const task = result.data.prioritized_tasks.find((t) => t.id === id);
    if (!task) return;
    const nextCompleted = !task.completed;

    // Optimistically update UI.
    setResult((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        data: {
          ...prev.data,
          prioritized_tasks: prev.data.prioritized_tasks.map((t) =>
            t.id === id ? { ...t, completed: nextCompleted } : t
          ),
        },
      };
    });

    try {
      await api.patchDailyTaskComplete(form.date, id, nextCompleted);
    } catch (err) {
      // Revert on failure.
      setResult((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          data: {
            ...prev.data,
            prioritized_tasks: prev.data.prioritized_tasks.map((t) =>
              t.id === id ? { ...t, completed: task.completed } : t
            ),
          },
        };
      });
      setError(err.message || "Failed to update task completion.");
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Daily Site Assistant</h2>
        <p>
          Generate a structured daily site action plan with prioritized tasks, workforce
          and equipment requirements, safety checks, and follow-up actions.
        </p>
      </div>

      <div className="grid-2">
        <div className="card" style={{ maxWidth: 720 }}>
          <div className="card-header">
            <h3>Site Inputs</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Date</label>
              <input type="date" value={form.date} onChange={(e) => handleChange("date", e.target.value)} />
            </div>
            <div className="field">
              <label>Project Phase</label>
              <input value={form.project_phase} onChange={(e) => handleChange("project_phase", e.target.value)} />
            </div>
            <div className="field">
              <label>Planned Activities</label>
              <textarea rows="2" value={form.planned_activities} onChange={(e) => handleChange("planned_activities", e.target.value)} />
            </div>
            <div className="form-row">
              <div className="field">
                <label>Workforce Availability</label>
                <input value={form.workforce_availability} onChange={(e) => handleChange("workforce_availability", e.target.value)} />
              </div>
              <div className="field">
                <label>Available Equipment</label>
                <input value={form.equipment} onChange={(e) => handleChange("equipment", e.target.value)} />
              </div>
            </div>
            <div className="field">
              <label>Available Materials</label>
              <input value={form.materials} onChange={(e) => handleChange("materials", e.target.value)} />
            </div>
            <div className="field">
              <label>Site Conditions</label>
              <input value={form.site_conditions} onChange={(e) => handleChange("site_conditions", e.target.value)} />
            </div>
            <div className="field">
              <label>Constraints</label>
              <textarea rows="2" value={form.constraints} onChange={(e) => handleChange("constraints", e.target.value)} />
            </div>
            <div style={{ marginTop: 20 }}>
              <button className="btn btn-primary" disabled={loading} style={{ width: "100%", padding: 12 }}>
                {loading ? <LoadingSpinner text="Generating daily plan..." /> : "Generate Daily Plan"}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Daily Action Plan</h3>
          </div>
          {!result && !loading && !error ? (
            <div className="empty-state">
              <h3>Waiting for input...</h3>
              <p>Enter site details to generate a daily plan.</p>
            </div>
          ) : null}
          {loading && <div className="empty-state"><LoadingSpinner text="Generating plan..." /></div>}
          {error && <ErrorMessage message={error} />}
          {result && (
            <div>
              <div className="field-hint" style={{ marginBottom: 10 }}>
                <span className={`mode-tag ${result.meta.mode}`}>{result.meta.mode.toUpperCase()}</span>{" "}
                <span style={{ fontSize: 12, color: "#6b7280" }}>{result.data.date}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <strong>Phase:</strong> {result.data.project_phase}
              </div>

              <div style={{ marginBottom: 12 }}>
                <strong style={{ display: "block", marginBottom: 6 }}>Prioritized Tasks</strong>
                {result.data.prioritized_tasks.map((t) => (
                  <div key={t.id} className="task-card">
                    <div className="info">
                      <div className="title">{t.title}</div>
                      <div className="meta">
                        <span style={{ ...PRIORITY_STYLE[t.priority || "low"], padding: "2px 6px", borderRadius: 4, fontSize: 11 }}>
                          {t.priority}
                        </span>{" "}
                        {t.category && <span style={{ marginLeft: 6, fontSize: 11 }}>{t.category}</span>}
                      </div>
                      <div style={{ marginTop: 4, fontSize: 13 }}>{t.description}</div>
                      {t.workforce_required && <div style={{ marginTop: 2, fontSize: 12, color: "#6b7280" }}>Workforce: {t.workforce_required}</div>}
                      {t.equipment_required && <div style={{ marginTop: 2, fontSize: 12, color: "#6b7280" }}>Equipment: {t.equipment_required}</div>}
                      {t.materials && <div style={{ marginTop: 2, fontSize: 12, color: "#6b7280" }}>Materials: {t.materials}</div>}
                    </div>
                    <div className="task-actions">
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => toggleTask(t.id)}
                      >
                        {t.completed ? "Undo" : "Done"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {result.data.safety_checks && result.data.safety_checks.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Safety Checks</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.safety_checks.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.possible_risks && result.data.possible_risks.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Possible Risks</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.possible_risks.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.recommended_follow_up && result.data.recommended_follow_up.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 6 }}>Follow-up Actions</strong>
                  <ul style={{ marginLeft: 20 }}>
                    {result.data.recommended_follow_up.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.data.assumptions && result.data.assumptions.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <strong style={{ display: "block", marginBottom: 4 }}>Assumptions</strong>
                  <p style={{ fontSize: 12, color: "#6b7280" }}>{result.data.assumptions.join(" ")}</p>
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
