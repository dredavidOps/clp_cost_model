// frontend/src/components/CashFlowPanel.jsx
// Q7: Cash required before launch, cash shortage timing

import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";

function fmt(val) {
  return `€${Number(val).toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function CashFlowPanel({ cashFlow }) {
  if (!cashFlow || !cashFlow.monthly_schedule) return null;

  const data = cashFlow.monthly_schedule.map((m) => ({
    phase: m.phase,
    opening: m.opening_balance,
    closing: m.closing_balance,
    movement: m.net_cash_movement,
  }));

  const fundingRequired = cashFlow.pre_launch_funding_required || 0;
  const lowestBalance = cashFlow.lowest_balance_amount || 0;
  const lowestWeek = cashFlow.lowest_balance_week || "";
  const endingBalance = cashFlow.ending_balance || 0;

  return (
    <div className="panel">
      <h3>Cash Flow & Funding</h3>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", marginBottom: "16px" }}>
        <div style={{ padding: "12px", borderRadius: "8px", background: fundingRequired > 0 ? "#fef2f2" : "#f0fdf4", border: `1px solid ${fundingRequired > 0 ? "#dc2626" : "#16a34a"}` }}>
          <div style={{ fontSize: "12px", color: "#888" }}>Pre-Launch Funding Required</div>
          <div style={{ fontSize: "18px", fontWeight: 600, color: fundingRequired > 0 ? "#dc2626" : "#16a34a" }}>
            {fmt(fundingRequired)}
          </div>
        </div>
        <div style={{ padding: "12px", borderRadius: "8px", background: "#fafafa", border: "1px solid #e0e0e0" }}>
          <div style={{ fontSize: "12px", color: "#888" }}>Lowest Balance</div>
          <div style={{ fontSize: "18px", fontWeight: 600, color: lowestBalance < 0 ? "#dc2626" : "#333" }}>
            {fmt(lowestBalance)}
          </div>
          <div style={{ fontSize: "11px", color: "#888" }}>{lowestWeek}</div>
        </div>
        <div style={{ padding: "12px", borderRadius: "8px", background: "#fafafa", border: "1px solid #e0e0e0" }}>
          <div style={{ fontSize: "12px", color: "#888" }}>Ending Balance</div>
          <div style={{ fontSize: "18px", fontWeight: 600, color: endingBalance >= 0 ? "#16a34a" : "#dc2626" }}>
            {fmt(endingBalance)}
          </div>
        </div>
        <div style={{ padding: "12px", borderRadius: "8px", background: "#fafafa", border: "1px solid #e0e0e0" }}>
          <div style={{ fontSize: "12px", color: "#888" }}>Cash Surplus</div>
          <div style={{ fontSize: "18px", fontWeight: 600, color: endingBalance >= 0 ? "#16a34a" : "#dc2626" }}>
            {fmt(endingBalance)}
          </div>
        </div>
      </div>

      {fundingRequired > 0 && (
        <div style={{ padding: "10px 14px", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", marginBottom: "16px", color: "#dc2626", fontSize: "14px" }}>
          ⚠️ <strong>Cash shortage risk:</strong> You need {fmt(fundingRequired)} in reserve before launching to avoid negative balances during the cohort.
        </div>
      )}

      <div style={{ height: "280px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="phase" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `€${v}`} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v) => fmt(v)} />
            <ReferenceLine y={0} stroke="#dc2626" strokeDasharray="4 4" />
            <Line type="monotone" dataKey="opening" stroke="#8884d8" name="Opening Balance" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="closing" stroke="#16a34a" name="Closing Balance" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <table className="data-table" style={{ marginTop: "16px", width: "100%", fontSize: "13px" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #e0e0e0" }}>
            <th style={{ textAlign: "left", padding: "8px" }}>Phase</th>
            <th style={{ textAlign: "right", padding: "8px" }}>Revenue In</th>
            <th style={{ textAlign: "right", padding: "8px" }}>Costs Out</th>
            <th style={{ textAlign: "right", padding: "8px" }}>Net Movement</th>
            <th style={{ textAlign: "right", padding: "8px" }}>Opening</th>
            <th style={{ textAlign: "right", padding: "8px" }}>Closing</th>
          </tr>
        </thead>
        <tbody>
          {cashFlow.monthly_schedule.map((m, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #f0f0f0" }}>
              <td style={{ padding: "8px" }}>{m.phase}</td>
              <td style={{ textAlign: "right", padding: "8px", color: "#16a34a" }}>{fmt(m.net_revenue_collected)}</td>
              <td style={{ textAlign: "right", padding: "8px", color: "#dc2626" }}>{fmt(m.cash_costs_paid)}</td>
              <td style={{ textAlign: "right", padding: "8px", color: m.net_cash_movement >= 0 ? "#16a34a" : "#dc2626" }}>{fmt(m.net_cash_movement)}</td>
              <td style={{ textAlign: "right", padding: "8px" }}>{fmt(m.opening_balance)}</td>
              <td style={{ textAlign: "right", padding: "8px", fontWeight: 500 }}>{fmt(m.closing_balance)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}