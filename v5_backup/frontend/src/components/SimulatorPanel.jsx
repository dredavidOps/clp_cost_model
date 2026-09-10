import useStore from '../store'
import { fmtCurrency, fmtNumber, fmtPercent, statusClass } from './Formatters'

function NumberInput({ label, value, onChange, step = 1 }) {
  return (
    <div className="form-group compact">
      <label>{label}</label>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
      />
    </div>
  )
}

function SimulatorPanel() {
  const { config, result, updateConfig, calculate, isLoading } = useStore()

  if (!config || !result) return <div className="loading">Loading…</div>

  const ws = config.workstreams
  const sm = config.seat_mix
  const dec = result.decisions

  return (
    <div className="panel simulator-panel">
      <div className="panel-grid two-col">
        <div className="card">
          <h3>Workstreams</h3>
          <div className="input-grid four-cols">
            <NumberInput
              label="IT Systems Admin"
              value={ws.it_systems_admin}
              onChange={(v) => updateConfig('workstreams.it_systems_admin', v)}
            />
            <NumberInput
              label="Data, BI & AI"
              value={ws.data_bi_ai}
              onChange={(v) => updateConfig('workstreams.data_bi_ai', v)}
            />
            <NumberInput
              label="Product / Ops"
              value={ws.product_project_ops}
              onChange={(v) => updateConfig('workstreams.product_project_ops', v)}
            />
            <NumberInput
              label="Marketing / Growth"
              value={ws.digital_marketing_growth}
              onChange={(v) => updateConfig('workstreams.digital_marketing_growth', v)}
            />
          </div>
        </div>

        <div className="card">
          <h3>Seat Mix</h3>
          <div className="input-grid two-cols">
            <NumberInput
              label="Early seats"
              value={sm.early_payment_seats}
              onChange={(v) => updateConfig('seat_mix.early_payment_seats', v)}
            />
            <NumberInput
              label="Early price"
              value={sm.early_payment_price}
              step={10}
              onChange={(v) => updateConfig('seat_mix.early_payment_price', v)}
            />
            <NumberInput
              label="Standard seats"
              value={sm.standard_payment_seats}
              onChange={(v) => updateConfig('seat_mix.standard_payment_seats', v)}
            />
            <NumberInput
              label="Standard price"
              value={sm.standard_payment_price}
              step={10}
              onChange={(v) => updateConfig('seat_mix.standard_payment_price', v)}
            />
            <NumberInput
              label="Installment seats"
              value={sm.installment_seats}
              onChange={(v) => updateConfig('seat_mix.installment_seats', v)}
            />
            <NumberInput
              label="Installment price"
              value={sm.installment_price}
              step={10}
              onChange={(v) => updateConfig('seat_mix.installment_price', v)}
            />
          </div>
        </div>
      </div>

      <div className="panel-grid three-col">
        <div className="card">
          <h3>Programme Timing</h3>
          <NumberInput
            label="Delivery weeks"
            value={config.delivery_weeks}
            onChange={(v) => updateConfig('delivery_weeks', v)}
          />
          <NumberInput
            label="M365 pre-launch weeks"
            value={config.m365_access_before_launch_weeks}
            onChange={(v) => updateConfig('m365_access_before_launch_weeks', v)}
          />
          <NumberInput
            label="Extension / wrap-up weeks"
            value={config.extension_wrapup_weeks}
            onChange={(v) => updateConfig('extension_wrapup_weeks', v)}
          />
        </div>

        <div className="card">
          <h3>Financial Controls</h3>
          <NumberInput
            label="VAT rate"
            value={config.vat_rate}
            step={0.01}
            onChange={(v) => updateConfig('vat_rate', v)}
          />
          <NumberInput
            label="Payment processing fee"
            value={config.payment_processing_fee_rate}
            step={0.001}
            onChange={(v) => updateConfig('payment_processing_fee_rate', v)}
          />
          <NumberInput
            label="Contingency rate"
            value={config.external_cost_contingency_rate}
            step={0.01}
            onChange={(v) => updateConfig('external_cost_contingency_rate', v)}
          />
          <NumberInput
            label="Target surplus margin"
            value={config.target_cash_surplus_margin}
            step={0.01}
            onChange={(v) => updateConfig('target_cash_surplus_margin', v)}
          />
        </div>

        <div className="card">
          <h3>Launch Gates</h3>
          <NumberInput
            label="Minimum total participants"
            value={config.minimum_total_participants}
            onChange={(v) => updateConfig('minimum_total_participants', v)}
          />
          <NumberInput
            label="Minimum per workstream"
            value={config.minimum_per_workstream}
            onChange={(v) => updateConfig('minimum_per_workstream', v)}
          />
          <NumberInput
            label="Min secured net revenue"
            value={config.minimum_secured_net_revenue}
            step={100}
            onChange={(v) => updateConfig('minimum_secured_net_revenue', v)}
          />
          <NumberInput
            label="Secured net revenue to date"
            value={config.secured_net_revenue_to_date}
            step={100}
            onChange={(v) => updateConfig('secured_net_revenue_to_date', v)}
          />
        </div>
      </div>

      <div className="card decision-card">
        <div className="decision-row">
          <div>
            <span className="label">Planned participants</span>
            <strong>{fmtNumber(
              ws.it_systems_admin +
                ws.data_bi_ai +
                ws.product_project_ops +
                ws.digital_marketing_growth,
              0
            )}</strong>
          </div>
          <div>
            <span className="label">Average gross price</span>
            <strong>{fmtCurrency(result.revenue.average_gross_price_per_participant)}</strong>
          </div>
          <div>
            <span className="label">Net programme revenue</span>
            <strong>{fmtCurrency(result.revenue.net_programme_revenue)}</strong>
          </div>
          <div>
            <span className="label">Total cash cost</span>
            <strong>{fmtCurrency(result.costs.total_cohort_cash_cost)}</strong>
          </div>
          <div>
            <span className="label">Cash surplus</span>
            <strong className={dec.cash_surplus >= 0 ? 'good' : 'bad'}>
              {fmtCurrency(dec.cash_surplus)}
            </strong>
          </div>
          <div>
            <span className="label">Surplus margin</span>
            <strong className={dec.cash_surplus_margin >= 0 ? 'good' : 'bad'}>
              {fmtPercent(dec.cash_surplus_margin)}
            </strong>
          </div>
          <div>
            <span className="label">Economics</span>
            <strong className={statusClass(dec.projected_economics_status)}>
              {dec.projected_economics_status}
            </strong>
          </div>
          <div>
            <span className="label">Launch readiness</span>
            <strong className={statusClass(dec.actual_launch_readiness)}>
              {dec.actual_launch_readiness}
            </strong>
          </div>
        </div>
      </div>

      <div className="panel-grid two-col">
        <div className="card">
          <h3>Cost Composition</h3>
          <table>
            <tbody>
              <tr><td>Mentors</td><td>{fmtCurrency(result.costs.mentor_cost)}</td></tr>
              <tr><td>M365 licences</td><td>{fmtCurrency(result.costs.m365_licences)}</td></tr>
              <tr><td>Other tools</td><td>{fmtCurrency(result.costs.other_tools)}</td></tr>
              <tr><td>Internal team</td><td>{fmtCurrency(result.costs.internal_team_payments)}</td></tr>
              <tr><td>Other external</td><td>{fmtCurrency(result.costs.other_external_costs)}</td></tr>
              <tr><td>Payment fees</td><td>{fmtCurrency(result.costs.payment_processing_fees)}</td></tr>
              <tr><td>Contingency</td><td>{fmtCurrency(result.costs.contingency_reserve)}</td></tr>
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>Decision Guidance</h3>
          <table>
            <tbody>
              <tr><td>Cash break-even price</td><td>{fmtCurrency(dec.cash_break_even_average_price)}</td></tr>
              <tr><td>Target-margin price</td><td>{fmtCurrency(dec.target_margin_average_price)}</td></tr>
              <tr><td>Price gap to target</td><td>{fmtCurrency(dec.price_gap_to_target)}</td></tr>
              <tr><td>Min additional cash buffer</td><td>{fmtCurrency(dec.minimum_additional_cash_buffer)}</td></tr>
              <tr><td>Cash cost / participant</td><td>{fmtCurrency(result.costs.cash_cost_per_participant)}</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <button
        className="submit-btn wide"
        onClick={calculate}
        disabled={isLoading}
      >
        {isLoading ? 'Calculating…' : 'Recalculate Model'}
      </button>
    </div>
  )
}

export default SimulatorPanel
