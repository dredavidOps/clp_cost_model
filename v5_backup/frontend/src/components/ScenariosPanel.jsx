import { useEffect, useState } from 'react'
import useStore from '../store'
import * as api from '../api'
import { fmtCurrency, fmtPercent, statusClass } from './Formatters'

function ScenarioCard({ scenario }) {
  return (
    <div className="card scenario-card">
      <h3>{scenario.name}</h3>
      <div className="scenario-metric">
        <span className="label">Participants</span>
        <strong>{scenario.participants}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Net revenue</span>
        <strong>{fmtCurrency(scenario.net_revenue)}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Cash cost</span>
        <strong>{fmtCurrency(scenario.cash_cost)}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Cash surplus</span>
        <strong className={scenario.cash_surplus >= 0 ? 'good' : 'bad'}>
          {fmtCurrency(scenario.cash_surplus)}
        </strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Surplus margin</span>
        <strong className={scenario.cash_surplus_margin >= 0 ? 'good' : 'bad'}>
          {fmtPercent(scenario.cash_surplus_margin)}
        </strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Cost / participant</span>
        <strong>{fmtCurrency(scenario.cash_cost_per_participant)}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Average price</span>
        <strong>{fmtCurrency(scenario.average_gross_price)}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Target-margin price</span>
        <strong>{fmtCurrency(scenario.target_margin_price)}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Price gap</span>
        <strong>{fmtCurrency(scenario.price_gap_to_target)}</strong>
      </div>
      <div className="scenario-metric">
        <span className="label">Status</span>
        <strong className={statusClass(scenario.status)}>{scenario.status}</strong>
      </div>
    </div>
  )
}

function ScenariosPanel() {
  const { config } = useStore()
  const [scenarios, setScenarios] = useState(null)

  useEffect(() => {
    if (!config) return
    api.getScenarios(config).then(setScenarios)
  }, [config])

  if (!scenarios) return <div className="loading">Loading scenarios…</div>

  return (
    <div className="panel scenarios-panel">
      <div className="scenario-grid">
        <ScenarioCard scenario={scenarios.conservative} />
        <ScenarioCard scenario={scenarios.base} />
        <ScenarioCard scenario={scenarios.growth} />
        <ScenarioCard scenario={scenarios.custom} />
      </div>
    </div>
  )
}

export default ScenariosPanel
