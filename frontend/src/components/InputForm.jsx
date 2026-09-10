import { useStore } from '../store'
import { workstreamLabels, toolLabels, operationalLabels, otherCostLabels, costBasisLabels } from '../config'

function NumberInput({ label, value, onChange, step = 1 }) {
  return (
    <div className="form-group">
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

function SelectInput({ label, value, options, onChange }) {
  return (
    <div className="form-group">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )
}

function BooleanInput({ label, value, onChange }) {
  return (
    <div className="form-group checkbox">
      <label>
        <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
        {label}
      </label>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <details className="form-section" open>
      <summary>{title}</summary>
      <div className="section-body">{children}</div>
    </details>
  )
}

export default function InputForm({ onRecalculate }) {
  const { config, updateField } = useStore()

  return (
    <div className="card">
      <h2>Model Inputs</h2>
      <form
        className="input-form"
        onSubmit={(e) => {
          e.preventDefault()
          if (onRecalculate) onRecalculate()
        }}
      >
        <Section title="Global Assumptions">
          <NumberInput label="Tool access period (months)" value={config.assumptions.tool_access_period_months} onChange={(v) => updateField('assumptions.tool_access_period_months', v)} />
          <NumberInput label="Contingency rate" value={config.assumptions.contingency_rate} step={0.01} onChange={(v) => updateField('assumptions.contingency_rate', v)} />
          <NumberInput label="Mentor hours / week (per workstream)" value={config.assumptions.mentor_hours_per_week} step={0.5} onChange={(v) => updateField('assumptions.mentor_hours_per_week', v)} />
          <NumberInput label="Mentor delivery weeks" value={config.assumptions.mentor_delivery_weeks} onChange={(v) => updateField('assumptions.mentor_delivery_weeks', v)} />
          <NumberInput label="Mentor hourly rate (€)" value={config.assumptions.mentor_hourly_rate_eur} step={5} onChange={(v) => updateField('assumptions.mentor_hourly_rate_eur', v)} />
          <NumberInput label="Internal team active months" value={config.assumptions.internal_team_active_months} onChange={(v) => updateField('assumptions.internal_team_active_months', v)} />
          <NumberInput label="USD→EUR rate" value={config.assumptions.usd_to_eur_rate} step={0.01} onChange={(v) => updateField('assumptions.usd_to_eur_rate', v)} />
          <NumberInput label="VAT rate" value={config.assumptions.vat_rate} step={0.01} onChange={(v) => updateField('assumptions.vat_rate', v)} />
          <SelectInput
            label="VAT treatment"
            value={config.assumptions.vat_treatment}
            options={[
              { value: 'small_business', label: 'Small business' },
              { value: 'taxable', label: 'Taxable' },
              { value: 'exempt', label: 'VAT exempt' },
            ]}
            onChange={(v) => updateField('assumptions.vat_treatment', v)}
          />
          <NumberInput label="Payment processing fee rate" value={config.assumptions.payment_processing_fee_rate} step={0.001} onChange={(v) => updateField('assumptions.payment_processing_fee_rate', v)} />
          <NumberInput label="Target cash surplus margin" value={config.assumptions.target_cash_surplus_margin} step={0.01} onChange={(v) => updateField('assumptions.target_cash_surplus_margin', v)} />
          <NumberInput label="Down-payment rate (standard & installment)" value={config.assumptions.down_payment_rate} step={0.05} onChange={(v) => updateField('assumptions.down_payment_rate', v)} />
          <BooleanInput label="Displayed price includes VAT" value={config.assumptions.displayed_price_includes_vat} onChange={(v) => updateField('assumptions.displayed_price_includes_vat', v)} />
        </Section>

        <Section title="Workstreams (participants)">
          {Object.entries(config.workstreams).map(([key, count]) => (
            <div key={key} className="subsection">
              <NumberInput label={workstreamLabels[key] || key} value={count} onChange={(v) => updateField(`workstreams.${key}`, Math.round(v))} />
            </div>
          ))}
        </Section>

        <Section title="Tool Cost Matrix ($/ppt/month)">
          {Object.entries(config.tools).map(([ws, tools]) => (
            <div key={ws} className="subsection">
              <strong>{workstreamLabels[ws] || ws}</strong>
              {Object.entries(tools).map(([tool, cost]) => (
                <NumberInput
                  key={tool}
                  label={toolLabels[tool] || tool}
                  value={cost}
                  step={1}
                  onChange={(v) => updateField(`tools.${ws}.${tool}`, v)}
                />
              ))}
            </div>
          ))}
        </Section>

        <Section title="Internal Team">
          <NumberInput label="Solomon monthly (€)" value={config.internal_team.founder_solomon.monthly} step={50} onChange={(v) => updateField('internal_team.founder_solomon.monthly', v)} />
          <NumberInput label="David monthly (€)" value={config.internal_team.founder_david.monthly} step={50} onChange={(v) => updateField('internal_team.founder_david.monthly', v)} />
          <NumberInput label="Akua monthly (€)" value={config.internal_team.founder_akua.monthly} step={50} onChange={(v) => updateField('internal_team.founder_akua.monthly', v)} />
          <NumberInput label="Volunteers count" value={config.internal_team.volunteers.count} onChange={(v) => updateField('internal_team.volunteers.count', v)} />
          <NumberInput label="Volunteer monthly each (€)" value={config.internal_team.volunteers.monthly_each} step={10} onChange={(v) => updateField('internal_team.volunteers.monthly_each', v)} />
          <NumberInput label="Intern count" value={config.internal_team.intern.count} onChange={(v) => updateField('internal_team.intern.count', v)} />
          <NumberInput label="Intern monthly (€)" value={config.internal_team.intern.monthly} step={10} onChange={(v) => updateField('internal_team.intern.monthly', v)} />
          <NumberInput label="Active months" value={config.internal_team.active_months} onChange={(v) => updateField('internal_team.active_months', v)} />
        </Section>

        <Section title="Operational Costs">
          {Object.entries(config.operational).map(([name, item]) => (
            <div key={name} className="subsection">
              <strong>{operationalLabels[name] || name}</strong>
              <SelectInput
                label="Cost basis"
                value={item.cost_basis}
                options={Object.entries(costBasisLabels).map(([value, label]) => ({ value, label }))}
                onChange={(v) => updateField(`operational.${name}.cost_basis`, v)}
              />
              <NumberInput label={item.cost_basis === 'fixed_annual' ? 'Annual cost (€)' : 'Unit cost (€)'} value={item.unit_cost} step={0.5} onChange={(v) => updateField(`operational.${name}.unit_cost`, v)} />
              {item.cost_basis !== 'fixed_annual' && (
                <NumberInput label={item.cost_basis === 'per_user_month' ? 'Seats / quantity' : 'Quantity'} value={item.quantity} onChange={(v) => updateField(`operational.${name}.quantity`, v)} />
              )}
              {item.cost_basis !== 'fixed_annual' && (
                <NumberInput label="Active months" value={item.active_months} onChange={(v) => updateField(`operational.${name}.active_months`, v)} />
              )}
            </div>
          ))}
        </Section>

        <Section title="Other Costs & Compliance">
          {Object.entries(config.other_costs).map(([name, item]) => (
            <div key={name} className="subsection">
              {item.is_percentage_of_revenue ? (
                <NumberInput
                  label={`${otherCostLabels[name] || name} (rate, ×100 for %)`}
                  value={(item.percentage_rate || 0) * 100}
                  step={0.1}
                  onChange={(v) => updateField(`other_costs.${name}.percentage_rate`, v / 100)}
                />
              ) : (
                <NumberInput label={`${otherCostLabels[name] || name} (€)`} value={item.amount} step={50} onChange={(v) => updateField(`other_costs.${name}.amount`, v)} />
              )}
            </div>
          ))}
        </Section>

        <Section title="Pricing & Seat Mix">
          <div className="subsection"><strong>Early</strong></div>
          <NumberInput label="Seats" value={config.pricing.early.seats} onChange={(v) => updateField('pricing.early.seats', v)} />
          <NumberInput label="Price (€)" value={config.pricing.early.price} step={10} onChange={(v) => updateField('pricing.early.price', v)} />

          <div className="subsection"><strong>Standard</strong></div>
          <NumberInput label="Seats" value={config.pricing.standard.seats} onChange={(v) => updateField('pricing.standard.seats', v)} />
          <NumberInput label="Price (€)" value={config.pricing.standard.price} step={10} onChange={(v) => updateField('pricing.standard.price', v)} />

          <div className="subsection"><strong>Installment</strong></div>
          <NumberInput label="Seats" value={config.pricing.installment.seats} onChange={(v) => updateField('pricing.installment.seats', v)} />
          <NumberInput label="Price (€)" value={config.pricing.installment.price} step={10} onChange={(v) => updateField('pricing.installment.price', v)} />
        </Section>

        <Section title="Launch Gates (Q10)">
          <NumberInput label="Confirmed participants" value={config.launch_gates.confirmed_participants} onChange={(v) => updateField('launch_gates.confirmed_participants', Math.round(v))} />
          <NumberInput label="Minimum confirmed to launch" value={config.launch_gates.minimum_confirmed_participants} onChange={(v) => updateField('launch_gates.minimum_confirmed_participants', Math.round(v))} />
          <NumberInput label="Secured revenue to date (€)" value={config.launch_gates.secured_revenue_to_date} step={100} onChange={(v) => updateField('launch_gates.secured_revenue_to_date', v)} />
          <NumberInput label="Minimum secured revenue (€)" value={config.launch_gates.minimum_secured_revenue} step={500} onChange={(v) => updateField('launch_gates.minimum_secured_revenue', v)} />
        </Section>

        <button className="submit-btn" type="submit">Recalculate</button>
      </form>
    </div>
  )
}
