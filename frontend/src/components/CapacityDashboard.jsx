// frontend/src/components/CapacityDashboard.jsx
// Q9: Mentor, tool, and team capacity checks

import React from "react";

function StatusBadge({ status }) {
  const colors = {
    OK: { bg: "#f0fdf4", text: "#16a34a", label: "OK" },
    WARNING: { bg: "#fffbeb", text: "#d97706", label: "WARNING" },
    FAIL: { bg: "#fef2f2", text: "#dc2626", label: "FAIL" },
  };
  const c = colors[status] || colors.WARNING;
  return (
    <span style={{ background: c.bg, color: c.text, padding: "3px 10px", borderRadius: "6px", fontSize: "12px", fontWeight: 600, border: `1px solid ${c.text}33` }}>
      {c.label}
    </span>
  );
}

export default function CapacityDashboard({ capacity }) {
  if (!capacity) return null;

  return (
    <div className="panel">
      <h3>Capacity Dashboard</h3>
      <p style={{ fontSize: "13px", color: "#666", marginBottom: "16px" }}>
        Can mentors, tools, and team support the planned cohort size?
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
        {/* Mentor Capacity */}
        <div style={{ padding: "16px", borderRadius: "10px", border: "1px solid #e0e0e0" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <h4 style={{ margin: 0, fontSize: "15px" }}>👨‍🏫 Mentors</h4>
            <StatusBadge status={capacity.mentor_capacity_status} />
          </div>
          <div style={{ fontSize: "13px", color: "#555", lineHeight: 1.5 }}>
            {capacity.mentor_capacity_detail}
          </div>
          <div style={{ marginTop: "10px", height: "8px", background: "#eee", borderRadius: "4px", overflow: "hidden" }}>
            <div
              style={{
                width: `${Math.min(100, (capacity.mentor_current_demand / capacity.mentor_max_capacity) * 100)}%`,
                height: "100%",
                background: capacity.mentor_capacity_status === "OK" ? "#16a34a" : capacity.mentor_capacity_status === "WARNING" ? "#d97706" : "#dc2626",
                borderRadius: "4px",
              }}
            />
          </div>
          <div style={{ fontSize: "11px", color: "#888", marginTop: "4px" }}>
            {capacity.mentor_current_demand} / {capacity.mentor_max_capacity} participants
          </div>
        </div>

        {/* Tool Limits */}
        <div style={{ padding: "16px", borderRadius: "10px", border: "1px solid #e0e0e0" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <h4 style={{ margin: 0, fontSize: "15px" }}>🛠️ Tools</h4>
            <StatusBadge status={capacity.tool_limit_status} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {capacity.tool_limit_details.map((tool, i) => (
              <div key={i} style={{ fontSize: "12px", color: "#555" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>{tool.tool_name}</span>
                  <StatusBadge status={tool.status} />
                </div>
                <div style={{ color: "#888", fontSize: "11px" }}>{tool.detail}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Team Bandwidth */}
        <div style={{ padding: "16px", borderRadius: "10px", border: "1px solid #e0e0e0" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <h4 style={{ margin: 0, fontSize: "15px" }}>👥 Team Bandwidth</h4>
            <StatusBadge status={capacity.team_bandwidth_status} />
          </div>
          <div style={{ fontSize: "13px", color: "#555", lineHeight: 1.5 }}>
            {capacity.team_bandwidth_detail}
          </div>
        </div>
      </div>
    </div>
  );
}