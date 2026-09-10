// frontend/src/components/FinancialOutcomePanel.jsx
// Q6: Revenue, cash surplus, pre-tax profit, margin

import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

function fmt(val) {
  return `€${Number(val).toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function fmtPct(val) {
  return `${(val * 100).toFixed(1)}%`;
}

export default function FinancialOutcomePanel({ revenue, totalCosts, decisions }) {
  if (!revenue || !totalCosts || !decisions) return null;

  const chartData = [
    { name: "Gross Receipts", value: revenue.participant_gross_receipts || 0, color: "#16a34a" },
    { name: "VAT Payable", value: -(revenue.vat_payable || 0), color: "#d97706" },
    { name: "Net Revenue", value: revenue.net_programme_revenue || 0, color: "#2563eb" },
    { name: "Total Costs", value: -(totalCosts.total || 0), color: "#dc2626" },
    { name: "Cash Surplus", value: decisions.cash_surplus || 0, color: decisions.cash_surplus >= 0 ? "#16a34a" : "#dc2626" },
  ];

  const metrics = [
    { label: "Gross Revenue", value: fmt(revenue.participant_gross_receipts), color: "#333" },
    { label: "Net Revenue", value: fmt(revenue.net_programme_revenue), color: "#2563eb" },
    { label: "Pre-Tax Profit", value: fmt(decisions.cash_surplus), color: decisions.cash_surplus >= 0 ? "#16a34a" : "#dc2626" },
    { label: "Margin", value: fmtPct(decisions.cash_surplus_margin), color: decisions.cash_surplus_margin >= 0 ? "#16a34a" : "#dc2626" },
  ];

  return (
    <div className="panel">
      <h3>Financial Outcome</h3>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", marginBottom: "16px" }}>
        {metrics.map((m, i) => (
          <div key={i} style={{ padding: "14px", borderRadius: "10px", border: "1px solid #e0e0e0", textAlign: "center" }}>
            <div style={{ fontSize: "12px", color: "#888", marginBottom: "6px" }}>{m.label}</div>
            <div style={{ fontSize: "22px", fontWeight: 600, color: m.color, fontVariantNumeric: "tabular-nums" }}>
              {m.value}
            </div>
          </div>
        ))}
      </div>

      <div style={{ height: "240px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={(v) => `€${v/1000}k`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => fmt(Math.abs(v))} />
            <Bar dataKey="value">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: "12px", fontSize: "12px", color: "#888" }}>
        Note: "Pre-tax profit" = "Cash surplus" in this model (before business income/trade tax).
      </div>
    </div>
  );
}