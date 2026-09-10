// frontend/src/components/SummaryCards.jsx
// Q3: Break-even price | Q5: Break-even cohort size | Q6: Financial outcome

import React from "react";
import { workstreamLabels } from "../config";

function fmt(val) {
  if (val === undefined || val === null) return "€0.00";
  return `€${Number(val).toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function fmtPct(val) {
  if (val === undefined || val === null) return "0.0%";
  return `${(val * 100).toFixed(1)}%`;
}

export default function SummaryCards({ summary, decisions, revenue, totalCosts }) {
  if (!summary || !decisions) return null;

  const cards = [
    {
      label: "Total Participants",
      value: summary.total_participants || 0,
      sub: "planned",
      color: "#333",
    },
    {
      label: "Total Programme Cost",
      value: fmt(summary.total_cost),
      sub: `€${(summary.cost_per_participant || 0).toFixed(2)} per participant`,
      color: "#333",
    },
    {
      label: "Net Revenue",
      value: fmt(summary.total_revenue),
      sub: "after VAT if applicable",
      color: "#333",
    },
    {
      label: "Cash Surplus",
      value: fmt(summary.net_margin),
      sub: fmtPct(summary.margin_pct),
      color: summary.net_margin >= 0 ? "#16a34a" : "#dc2626",
    },
    {
      label: "Break-Even Price",
      value: fmt(decisions.cash_break_even_average_price),
      sub: (() => {
        const avg = revenue?.average_gross_price || 0;
        const be = decisions.cash_break_even_average_price || 0;
        const diff = avg - be;
        if (avg <= 0) return "Minimum average price to cover all costs";
        return diff >= 0
          ? `Your price ${fmt(avg)} is ${fmt(diff)} above break-even ✅`
          : `Your price ${fmt(avg)} is ${fmt(-diff)} below break-even ⚠️`;
      })(),
      color: decisions.cash_break_even_average_price <= (revenue?.average_gross_price || 0) ? "#16a34a" : "#dc2626",
    },
    {
      label: "Break-Even Participants",
      value: `${(decisions.break_even_cohort_size || 0).toFixed(1)}`,
      sub: (() => {
        const needed = decisions.minimum_viable_cohort_size || 0;
        const planned = summary.total_participants || 0;
        const avg = revenue?.average_gross_price || 0;
        const ok = planned >= needed;
        return `At ${fmt(avg)} avg price you need ${needed} · Current plan: ${planned} ${ok ? "✅" : "❌"}`;
      })(),
      color: (decisions.minimum_viable_cohort_size || 0) <= (summary.total_participants || 0) ? "#16a34a" : "#dc2626",
    },
    {
      label: "Target Margin Price",
      value: fmt(decisions.target_margin_average_price),
      sub: `Gap: ${fmt(decisions.price_gap_to_target || 0)}`,
      color: "#2563eb",
    },
    {
      label: "Launch Status",
      value: summary.launch_status || "REVIEW",
      sub: summary.launch_status === "GO" ? "Ready to launch" : "See blocking issues",
      color: summary.launch_status === "GO" ? "#16a34a" : summary.launch_status === "HOLD" ? "#dc2626" : "#d97706",
    },
  ];

  return (
    <div className="panel">
      <h3>Summary</h3>
      <div className="cards-grid" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px" }}>
        {cards.map((card, i) => (
          <div
            key={i}
            style={{
              padding: "14px",
              borderRadius: "10px",
              border: "1px solid #e0e0e0",
              background: "#fafafa",
            }}
          >
            <div style={{ fontSize: "12px", color: "#888", marginBottom: "4px", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              {card.label}
            </div>
            <div style={{ fontSize: "20px", fontWeight: 600, color: card.color, fontVariantNumeric: "tabular-nums" }}>
              {card.value}
            </div>
            <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>
              {card.sub}
            </div>
          </div>
        ))}

        {/* Cost per workstream (per cohort slice + per participant) */}
        {totalCosts?.cost_by_workstream && Object.keys(totalCosts.cost_by_workstream).length > 0 && (
          <div
            style={{
              gridColumn: "span 2",
              padding: "14px",
              borderRadius: "10px",
              border: "1px solid #e0e0e0",
              background: "#fafafa",
            }}
          >
            <div style={{ fontSize: "12px", color: "#888", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Cost per Workstream
            </div>
            {Object.entries(totalCosts.cost_by_workstream).map(([ws, cost]) => (
              <div key={ws} style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", padding: "2px 0", fontVariantNumeric: "tabular-nums" }}>
                <span style={{ color: "#555" }}>{workstreamLabels[ws] || ws}</span>
                <span>
                  <strong>{fmt(cost)}</strong>
                  <span style={{ color: "#888", fontSize: "12px" }}>
                    {" "}({fmt(totalCosts.per_participant_by_workstream?.[ws])}/ppt)
                  </span>
                </span>
              </div>
            ))}
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", paddingTop: "4px", marginTop: "4px", borderTop: "1px solid #e0e0e0", fontVariantNumeric: "tabular-nums" }}>
              <span style={{ color: "#555", fontWeight: 600 }}>Total cohort</span>
              <strong>{fmt(totalCosts.total)}</strong>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}