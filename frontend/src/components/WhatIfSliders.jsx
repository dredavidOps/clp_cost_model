// frontend/src/components/WhatIfSliders.jsx
// Q8: quick what-if sliders that update the whole dashboard

import React from "react";
import { useStore } from "../store";

function Slider({ label, value, min, max, step, display, onChange }) {
  return (
    <div style={{ marginBottom: "14px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
        <span>{label}</span>
        <strong>{display !== undefined ? display : value}</strong>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        style={{ width: "100%" }}
      />
    </div>
  );
}

export default function WhatIfSliders({ summary, onRecalculate }) {
  const { config, updateField } = useStore();
  if (!config || !config.workstreams) return null;

  const totalParticipants = Object.values(config.workstreams).reduce((a, b) => a + b, 0);
  const margin = summary ? summary.margin_pct : null;

  const setParticipants = (total) => {
    // Scale each workstream proportionally, keeping at least 0
    const keys = Object.keys(config.workstreams);
    const per = Math.floor(total / keys.length);
    keys.forEach((k, i) => {
      updateField(`workstreams.${k}`, i === keys.length - 1 ? total - per * (keys.length - 1) : per);
    });
    if (onRecalculate) onRecalculate();
  };

  const setAvgPrice = (price) => {
    ["early", "standard", "installment"].forEach((tier) => updateField(`pricing.${tier}.price`, price));
    if (onRecalculate) onRecalculate();
  };

  return (
    <div className="panel">
      <h3>What-If Sliders</h3>
      <p style={{ fontSize: "13px", color: "#666", marginBottom: "12px" }}>
        Drag to stress-test the model — the whole dashboard recalculates.
        {margin !== null && (
          <> Current margin: <strong style={{ color: margin >= 0 ? "#16a34a" : "#dc2626" }}>{(margin * 100).toFixed(1)}%</strong>.</>
        )}
      </p>

      <Slider
        label="Total participants (spread evenly across workstreams)"
        value={totalParticipants}
        min={8}
        max={80}
        step={4}
        onChange={(e) => setParticipants(parseInt(e.target.value, 10))}
      />
      <Slider
        label="Average price (all tiers, €)"
        value={config.pricing.standard.price}
        min={400}
        max={1200}
        step={10}
        display={`€${config.pricing.standard.price}`}
        onChange={(e) => setAvgPrice(parseInt(e.target.value, 10))}
      />
      <Slider
        label="Mentor hourly rate (€)"
        value={config.assumptions.mentor_hourly_rate_eur}
        min={0}
        max={80}
        step={1}
        display={`€${config.assumptions.mentor_hourly_rate_eur}`}
        onChange={(e) => {
          updateField("assumptions.mentor_hourly_rate_eur", parseInt(e.target.value, 10));
          if (onRecalculate) onRecalculate();
        }}
      />
      <Slider
        label="Tool contingency (%)"
        value={Math.round((config.assumptions.contingency_rate || 0) * 100)}
        min={0}
        max={40}
        step={1}
        display={`${Math.round((config.assumptions.contingency_rate || 0) * 100)}%`}
        onChange={(e) => {
          updateField("assumptions.contingency_rate", (parseInt(e.target.value, 10) || 0) / 100);
          if (onRecalculate) onRecalculate();
        }}
      />
    </div>
  );
}
