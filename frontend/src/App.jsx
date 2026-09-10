// frontend/src/App.jsx
// Integrates all 10 business question components

import React, { useEffect } from "react";
import { useStore } from "./store.js";
import { api } from "./api.js";
import Layout from "./components/Layout.jsx";
import InputForm from "./components/InputForm.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import CostBreakdownChart from "./components/CostBreakdownChart.jsx";
import WorkstreamToolsTable from "./components/WorkstreamToolsTable.jsx";
import PricingSimulator from "./components/PricingSimulator.jsx";
import BreakEvenChart from "./components/BreakEvenChart.jsx";
import SensitivityHeatmap from "./components/SensitivityHeatmap.jsx";
import TeamCompensationTable from "./components/TeamCompensationTable.jsx";
import OperationalCostsTable from "./components/OperationalCostsTable.jsx";
import ModelChecks from "./components/ModelChecks.jsx";

// Q10, Q7, Q9, Q1, Q6, Q2, Q8 components
import LaunchControlPanel from "./components/LaunchControlPanel.jsx";
import CashFlowPanel from "./components/CashFlowPanel.jsx";
import CapacityDashboard from "./components/CapacityDashboard.jsx";
import CompleteCostStatement from "./components/CompleteCostStatement.jsx";
import FinancialOutcomePanel from "./components/FinancialOutcomePanel.jsx";
import CostPerParticipantDetail from "./components/CostPerParticipantDetail.jsx";
import ScenarioComparison from "./components/ScenarioComparison.jsx";
import WhatIfSliders from "./components/WhatIfSliders.jsx";

export default function App() {
  const { setResult, setSummary, setChecks, setTeam, setBreakEven, setSensitivity, setLoading, setError } = useStore();

  useEffect(() => {
    async function loadDefaults() {
      try {
        setLoading(true);
        const defaults = await api.getDefaults();
        useStore.setState({ config: defaults });
        await runCalculations(defaults);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadDefaults();
  }, []);

  async function runCalculations(cfg) {
    try {
      setLoading(true);
      setError(null);

      const [result, summary, checks, team, breakEven, sensitivity] = await Promise.all([
        api.calculate(cfg),
        api.calculateSummary(cfg),
        api.calculateChecks(cfg),
        api.calculateTeam(cfg),
        api.calculateBreakEven(cfg),
        api.calculateSensitivity(cfg),
      ]);

      setResult(result);
      setSummary(summary);
      setChecks(checks);
      setTeam(team);
      setBreakEven(breakEven);
      setSensitivity(sensitivity);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const handleRecalculate = () => {
    const currentConfig = useStore.getState().config;
    runCalculations(currentConfig);
  };

  // Q10: editing launch gates updates the store and recalculates immediately
  const handleGateChange = (path, value) => {
    useStore.getState().updateField(path, value);
    const currentConfig = useStore.getState().config;
    runCalculations(currentConfig);
  };

  const state = useStore();

  return (
    <Layout>
      {state.error && (
        <div className="error" style={{ marginBottom: "1rem" }}>
          Error: {state.error}
        </div>
      )}

      {state.loading && !state.result && <div className="loading">Loading model…</div>}

      <div className="layout">
        {/* Left pane: model parameters */}
        <aside>
          <InputForm onRecalculate={handleRecalculate} />
        </aside>

        {/* Right pane: dashboard */}
        <main>
          {/* Q10: Launch Control — at the TOP */}
          <LaunchControlPanel
            checks={state.checks}
            decisions={state.result?.decisions}
            launchGates={state.config?.launch_gates}
            onGateChange={handleGateChange}
          />

          {/* Q3, Q5, Q6: Summary KPIs */}
          <SummaryCards
            summary={state.summary}
            decisions={state.result?.decisions}
            revenue={state.result?.revenue}
            totalCosts={state.result?.total_costs}
          />

          {/* Q6: Financial Outcome */}
          <FinancialOutcomePanel
            revenue={state.result?.revenue}
            totalCosts={state.result?.total_costs}
            decisions={state.result?.decisions}
          />

          {/* Q1: Complete Cost Statement */}
          <CompleteCostStatement totalCosts={state.result?.total_costs} />

          {/* Q2: Cost Per Participant detail */}
          <CostPerParticipantDetail totalCosts={state.result?.total_costs} />

          {/* Q8: What-if sliders */}
          <WhatIfSliders summary={state.summary} onRecalculate={handleRecalculate} />

          {/* Charts & tables */}
          <CostBreakdownChart totalCosts={state.result?.total_costs} />
          <WorkstreamToolsTable tools={state.result?.tools} />
          <PricingSimulator
            pricing={state.config?.pricing}
            revenue={state.result?.revenue}
            decisions={state.result?.decisions}
            onRecalculate={handleRecalculate}
          />
          <BreakEvenChart breakEven={state.breakEven} currentPrice={state.result?.revenue?.average_gross_price} />
          <SensitivityHeatmap sensitivity={state.sensitivity} />

          {/* Q8: Scenario comparison */}
          <ScenarioComparison />

          {/* Q7: Cash Flow */}
          <CashFlowPanel cashFlow={state.result?.cash_flow} />

          {/* Q9: Capacity */}
          <CapacityDashboard capacity={state.result?.capacity} />

          <TeamCompensationTable team={state.team} />
          <OperationalCostsTable operational={state.result?.operational} config={state.config?.operational} />
          <ModelChecks checks={state.checks} />
        </main>
      </div>
    </Layout>
  );
}
