// frontend/src/components/ScenarioComparison.jsx
// Q8: save up to 3 scenarios and compare side-by-side

import React, { useState } from "react";
import { api } from "../api";
import { useStore } from "../store";

function fmt(val) {
  return `€${Number(val).toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function fmtPct(val) {
  return `${(val * 100).toFixed(1)}%`;
}

const SLOTS = ["A", "B", "C"];

export default function ScenarioComparison() {
  const [saved, setSaved] = useState({}); // { A: {name, config} }
  const [comparisons, setComparisons] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const saveSlot = (slot) => {
    const current = useStore.getState().config;
    setSaved((prev) => ({ ...prev, [slot]: { config: structuredClone(current) } }));
    setComparisons(null);
  };

  const clearSlot = (slot) => {
    setSaved((prev) => {
      const next = { ...prev };
      delete next[slot];
      return next;
    });
    setComparisons(null);
  };

  const runCompare = async () => {
    const slots = SLOTS.filter((s) => saved[s]);
    if (slots.length < 2) {
      setError("Save at least 2 scenarios (A, B, C) to compare.");
      return;
    }
    setError(null);
    setBusy(true);
    try {
      const res = await api.compareScenarios(
        slots.map((s) => saved[s].config),
        slots.map((s) => `Scenario ${s}`)
      );
      setComparisons(res.comparisons);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const rows = comparisons ? [
    { label: "Participants", get: (c) => c.total_participants, fmt: (v) => v, delta: true },
    { label: "Average price", get: (c) => c.average_gross_price, fmt, delta: true },
    { label: "Gross receipts", get: (c) => c.gross_receipts, fmt, delta: true },
    { label: "Net revenue", get: (c) => c.net_programme_revenue, fmt, delta: true },
    { label: "Total cost", get: (c) => c.total_cost, fmt, delta: true },
    { label: "Cash surplus", get: (c) => c.cash_surplus, fmt, delta: true },
    { label: "Margin", get: (c) => c.cash_surplus_margin, fmt: fmtPct, delta: true },
    { label: "Break-even price", get: (c) => c.break_even_price, fmt, delta: true },
    { label: "Economics", get: (c) => c.economics_status, fmt: (v) => v, delta: false },
    { label: "Launch", get: (c) => c.launch_readiness, fmt: (v) => v, delta: false },
  ] : [];

  return (
    <div className="panel">
      <h3>Scenario Comparison</h3>
      <p style={{ fontSize: "13px", color: "#666", marginBottom: "10px" }}>
        Save the current model inputs as a scenario, tweak the inputs, then compare up to 3 side-by-side.
      </p>

      <div style={{ display: "flex", gap: "8px", marginBottom: "12px", flexWrap: "wrap" }}>
        {SLOTS.map((slot) => (
          <span key={slot} style={{ display: "inline-flex", gap: "4px", alignItems: "center" }}>
            <button
              onClick={() => saveSlot(slot)}
              style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #2563eb", background: saved[slot] ? "#2563eb" : "#fff", color: saved[slot] ? "#fff" : "#2563eb", cursor: "pointer", fontSize: "13px" }}
            >
              Save as {slot}
            </button>
            {saved[slot] && (
              <button onClick={() => clearSlot(slot)} style={{ padding: "6px 8px", borderRadius: "6px", border: "1px solid #ccc", background: "#fff", cursor: "pointer", fontSize: "13px" }}>
                ×
              </button>
            )}
          </span>
        ))}
        <button
          onClick={runCompare}
          disabled={busy}
          style={{ padding: "6px 14px", borderRadius: "6px", border: "1px solid #16a34a", background: "#16a34a", color: "#fff", cursor: busy ? "default" : "pointer", fontSize: "13px", opacity: busy ? 0.6 : 1 }}
        >
          {busy ? "Comparing…" : "Compare"}
        </button>
      </div>

      {error && (
        <div style={{ padding: "8px 12px", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", color: "#dc2626", fontSize: "13px", marginBottom: "10px" }}>
          {error}
        </div>
      )}

      {comparisons && (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", fontSize: "13px", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                <th style={{ padding: "8px" }}>Metric</th>
                {comparisons.map((c) => (
                  <th key={c.name} style={{ padding: "8px", textAlign: "right" }}>{c.name}</th>
                ))}
                {comparisons.length > 1 && (
                  <th style={{ padding: "8px", textAlign: "right", color: "#888" }}>Δ B−A{comparisons.length > 2 ? " / C−A" : ""}</th>
                )}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const base = row.get(comparisons[0]);
                return (
                  <tr key={row.label} style={{ borderBottom: "1px solid #f0f0f0" }}>
                    <td style={{ padding: "6px 8px" }}>{row.label}</td>
                    {comparisons.map((c) => (
                      <td key={c.name} style={{ padding: "6px 8px", textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
                        {row.fmt(row.get(c))}
                      </td>
                    ))}
                    {comparisons.length > 1 && (
                      <td style={{ padding: "6px 8px", textAlign: "right", color: "#888", fontVariantNumeric: "tabular-nums" }}>
                        {comparisons.slice(1).map((c, i) => {
                          const d = row.get(c) - base;
                          return <div key={i}>{row.delta ? (d >= 0 ? "+" : "") + (row.fmt === fmtPct ? `${(d * 100).toFixed(1)}pp` : row.fmt(Math.abs(d)).replace("€", d < 0 ? "-€" : "€")) : "—"}</div>;
                        })}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
