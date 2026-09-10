// frontend/src/components/CostPerParticipantDetail.jsx
// Q2: cost per participant by category and by workstream

import React, { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { workstreamLabels } from "../config";

function fmt(val) {
  return `€${Number(val).toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

const CATEGORY_META = [
  { key: "tools", label: "Tools", color: "#2563eb" },
  { key: "mentors", label: "Mentors", color: "#16a34a" },
  { key: "internal_team", label: "Internal Team", color: "#ca8a04" },
  { key: "operational", label: "Operational", color: "#9333ea" },
];

export default function CostPerParticipantDetail({ totalCosts }) {
  const [tab, setTab] = useState("category");
  if (!totalCosts || !totalCosts.per_participant_breakdown) return null;

  const bd = totalCosts.per_participant_breakdown;
  const byWs = totalCosts.per_participant_by_workstream || {};

  const categoryData = CATEGORY_META
    .filter((c) => bd[c.key] !== undefined)
    .map((c) => ({ name: c.label, value: bd[c.key], color: c.color }));

  const coreTotal = CATEGORY_META.reduce((sum, c) => sum + (bd[c.key] || 0), 0);
  const otherPerPpt = bd.other || 0;

  const wsData = Object.entries(byWs).map(([ws, value]) => ({
    name: workstreamLabels[ws] || ws,
    value,
  }));

  const tabStyle = (active) => ({
    padding: "6px 14px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    background: active ? "#2563eb" : "#fff",
    color: active ? "#fff" : "#333",
    cursor: "pointer",
    fontSize: "13px",
    marginRight: "8px",
  });

  return (
    <div className="panel">
      <h3>Cost Per Participant</h3>

      <div style={{ marginBottom: "14px" }}>
        <button style={tabStyle(tab === "category")} onClick={() => setTab("category")}>By Category</button>
        <button style={tabStyle(tab === "workstream")} onClick={() => setTab("workstream")}>By Workstream</button>
      </div>

      {tab === "category" && (
        <>
          <div style={{ height: "200px", marginBottom: "12px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(v) => `€${v}`} />
                <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => fmt(v)} />
                <Bar dataKey="value" fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <table style={{ width: "100%", fontSize: "13px", borderCollapse: "collapse" }}>
            <tbody>
              {categoryData.map((c) => (
                <tr key={c.name} style={{ borderBottom: "1px solid #f0f0f0" }}>
                  <td style={{ padding: "6px 8px" }}>
                    <span style={{ display: "inline-block", width: 10, height: 10, background: c.color, borderRadius: 2, marginRight: 8 }} />
                    {c.name}
                  </td>
                  <td style={{ padding: "6px 8px", textAlign: "right" }}>{fmt(c.value)}</td>
                  <td style={{ padding: "6px 8px", textAlign: "right", color: "#888" }}>
                    {coreTotal > 0 ? `${((c.value / coreTotal) * 100).toFixed(1)}%` : "—"}
                  </td>
                </tr>
              ))}
              {otherPerPpt > 0 && (
                <tr style={{ borderBottom: "1px solid #f0f0f0", color: "#888" }}>
                  <td style={{ padding: "6px 8px" }}>Other (tracked separately)</td>
                  <td style={{ padding: "6px 8px", textAlign: "right" }}>{fmt(otherPerPpt)}</td>
                  <td style={{ padding: "6px 8px", textAlign: "right" }}>—</td>
                </tr>
              )}
              <tr style={{ fontWeight: 600, background: "#fafafa" }}>
                <td style={{ padding: "8px" }}>Total per participant</td>
                <td style={{ padding: "8px", textAlign: "right" }}>{fmt(totalCosts.per_participant)}</td>
                <td style={{ padding: "8px" }}></td>
              </tr>
            </tbody>
          </table>
        </>
      )}

      {tab === "workstream" && (
        <>
          <p style={{ fontSize: "12px", color: "#888", marginBottom: "8px" }}>
            What a participant costs on average in each workstream (workstream tools + mentors + share of team &amp; ops).
          </p>
          <div style={{ height: "220px", marginBottom: "12px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={wsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => `€${v}`} />
                <Tooltip formatter={(v) => fmt(v)} />
                <Bar dataKey="value" fill="#16a34a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <table style={{ width: "100%", fontSize: "13px", borderCollapse: "collapse" }}>
            <tbody>
              {wsData.map((w) => (
                <tr key={w.name} style={{ borderBottom: "1px solid #f0f0f0" }}>
                  <td style={{ padding: "6px 8px" }}>{w.name}</td>
                  <td style={{ padding: "6px 8px", textAlign: "right" }}>{fmt(w.value)}</td>
                </tr>
              ))}
              <tr style={{ fontWeight: 600, background: "#fafafa" }}>
                <td style={{ padding: "8px" }}>Overall average</td>
                <td style={{ padding: "8px", textAlign: "right" }}>{fmt(totalCosts.per_participant)}</td>
              </tr>
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
