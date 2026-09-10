// frontend/src/components/CompleteCostStatement.jsx
// Q1: Complete cost of running one cohort

import React, { useState } from "react";

function fmt(val) {
  return `€${Number(val).toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function CompleteCostStatement({ totalCosts }) {
  if (!totalCosts || !totalCosts.line_items) return null;

  const [expanded, setExpanded] = useState({});

  const categories = ["Tools", "Mentors", "Internal Team", "Operational", "Other Costs"];
  const categoryTotals = {};
  categories.forEach((cat) => {
    categoryTotals[cat] = totalCosts.line_items
      .filter((item) => item.category === cat)
      .reduce((sum, item) => sum + item.amount_eur, 0);
  });

  return (
    <div className="panel">
      <h3>Complete Cost Statement</h3>
      <p style={{ fontSize: "13px", color: "#666", marginBottom: "12px" }}>
        Every line item that makes up the total programme cost.
      </p>

      <table style={{ width: "100%", fontSize: "13px", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
            <th style={{ padding: "8px" }}>Category</th>
            <th style={{ padding: "8px" }}>Item</th>
            <th style={{ padding: "8px" }}>Basis</th>
            <th style={{ padding: "8px", textAlign: "right" }}>EUR</th>
            <th style={{ padding: "8px", textAlign: "right" }}>USD</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((cat) => {
            const items = totalCosts.line_items.filter((item) => item.category === cat);
            const isExpanded = expanded[cat];
            const catTotal = categoryTotals[cat] || 0;

            return (
              <React.Fragment key={cat}>
                <tr
                  style={{ borderBottom: "1px solid #f0f0f0", cursor: items.length > 1 ? "pointer" : "default", background: "#fafafa" }}
                  onClick={() => items.length > 1 && setExpanded((prev) => ({ ...prev, [cat]: !prev[cat] }))}
                >
                  <td style={{ padding: "8px", fontWeight: 600 }}>
                    {cat} {items.length > 1 && (isExpanded ? "▼" : "▶")}
                  </td>
                  <td style={{ padding: "8px", color: "#888" }}>{items.length} item(s)</td>
                  <td style={{ padding: "8px" }}></td>
                  <td style={{ padding: "8px", textAlign: "right", fontWeight: 600 }}>{fmt(catTotal)}</td>
                  <td style={{ padding: "8px" }}></td>
                </tr>
                {isExpanded && items.map((item, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f5f5f5" }}>
                    <td style={{ padding: "8px", paddingLeft: "24px" }}></td>
                    <td style={{ padding: "8px" }}>{item.subcategory || "—"}</td>
                    <td style={{ padding: "8px", color: "#888", fontSize: "12px" }}>{item.basis}</td>
                    <td style={{ padding: "8px", textAlign: "right" }}>{fmt(item.amount_eur)}</td>
                    <td style={{ padding: "8px", textAlign: "right", color: "#888" }}>
                      {item.amount_usd ? fmt(item.amount_usd) : "—"}
                    </td>
                  </tr>
                ))}
              </React.Fragment>
            );
          })}
          <tr style={{ borderTop: "2px solid #333", background: "#f0f0f0", fontWeight: 600 }}>
            <td style={{ padding: "10px 8px" }}>TOTAL</td>
            <td style={{ padding: "10px 8px" }}></td>
            <td style={{ padding: "10px 8px" }}></td>
            <td style={{ padding: "10px 8px", textAlign: "right", fontSize: "16px" }}>{fmt(totalCosts.total)}</td>
            <td style={{ padding: "10px 8px" }}></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}