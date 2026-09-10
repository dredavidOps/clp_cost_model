// frontend/src/components/LaunchControlPanel.jsx
// Q10: Launch GO / HOLD / REVIEW decision panel

import React from "react";

export default function LaunchControlPanel({ checks, decisions, launchGates, onGateChange }) {
  if (!checks || !decisions) return null;

  const status = checks.launch_readiness || "REVIEW";
  const gates = checks.launch_gates_status || {};
  const blocking = checks.blocking_gates || [];

  const statusConfig = {
    GO: { color: "#16a34a", bg: "#f0fdf4", label: "LAUNCH STATUS: GO 🚀" },
    HOLD: { color: "#dc2626", bg: "#fef2f2", label: "LAUNCH STATUS: HOLD 🛑" },
    REVIEW: { color: "#d97706", bg: "#fffbeb", label: "LAUNCH STATUS: REVIEW ⚠️" },
  };

  const config = statusConfig[status] || statusConfig.REVIEW;

  const gateItems = [
    { key: "economics_viable", label: "Economics VIABLE", icon: "💰" },
    { key: "confirmed_participants", label: "Confirmed Participants", icon: "👥" },
    { key: "secured_revenue", label: "Secured Revenue", icon: "💶" },
    { key: "model_checks", label: "Model Checks PASS", icon: "✅" },
    { key: "seat_reconciliation", label: "Priced Seats = Participants", icon: "🎫" },
  ];

  return (
    <div className="panel launch-panel">
      <div
        className="launch-banner"
        style={{
          background: config.bg,
          border: `2px solid ${config.color}`,
          borderRadius: "12px",
          padding: "16px 20px",
          marginBottom: "16px",
        }}
      >
        <h2 style={{ color: config.color, margin: 0, fontSize: "22px" }}>
          {config.label}
        </h2>
        {blocking.length > 0 && (
          <div style={{ marginTop: "10px", color: "#555", fontSize: "14px" }}>
            <strong>Blocking issues:</strong>
            <ul style={{ margin: "6px 0 0 18px", padding: 0 }}>
              {blocking.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="gates-grid" style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "10px" }}>
        {gateItems.map((gate) => {
          const gateStatus = gates[gate.key] || "FAIL";
          const isPass = gateStatus === "PASS";
          return (
            <div
              key={gate.key}
              style={{
                textAlign: "center",
                padding: "12px",
                borderRadius: "10px",
                background: isPass ? "#f0fdf4" : "#fef2f2",
                border: `2px solid ${isPass ? "#16a34a" : "#dc2626"}`,
              }}
            >
              <div style={{ fontSize: "24px", marginBottom: "6px" }}>{gate.icon}</div>
              <div style={{ fontSize: "12px", fontWeight: 500, color: "#333" }}>{gate.label}</div>
              <div style={{ fontSize: "12px", color: isPass ? "#16a34a" : "#dc2626", fontWeight: 600 }}>
                {gateStatus}
              </div>
            </div>
          );
        })}
      </div>

      {launchGates && onGateChange && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px", marginTop: "14px" }}>
          <div>
            <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
              Confirmed participants (min {launchGates.minimum_confirmed_participants})
            </label>
            <input
              type="number"
              min="0"
              value={launchGates.confirmed_participants}
              onChange={(e) => onGateChange("launch_gates.confirmed_participants", Math.max(0, Math.round(parseFloat(e.target.value) || 0)))}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #ccc", fontSize: "14px" }}
            />
          </div>
          <div>
            <label style={{ fontSize: "12px", color: "#666", display: "block", marginBottom: "4px" }}>
              Secured revenue to date (min €{Number(launchGates.minimum_secured_revenue).toLocaleString("en-IE")})
            </label>
            <input
              type="number"
              min="0"
              step="100"
              value={launchGates.secured_revenue_to_date}
              onChange={(e) => onGateChange("launch_gates.secured_revenue_to_date", Math.max(0, parseFloat(e.target.value) || 0))}
              style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid #ccc", fontSize: "14px" }}
            />
          </div>
        </div>
      )}
    </div>
  );
}