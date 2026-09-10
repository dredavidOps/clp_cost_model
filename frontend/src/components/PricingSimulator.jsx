import { useStore } from '../store'

function fmtMoney(value) {
  return `€${Number(value).toLocaleString('en-IE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function Field({ label, value, onChange, type = 'number' }) {
  return (
    <div className="form-group">
      <label>{label}</label>
      <input type={type} value={value} onChange={(e) => onChange(type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)} />
    </div>
  )
}

// Q4: pricing tiers + target-margin slider | Q5: minimum participants at this price
export default function PricingSimulator({ pricing, revenue, decisions, onRecalculate }) {
  const { config, updateField } = useStore()
  if (!pricing || !decisions) return null

  const targetMarginPct = Math.round((config.assumptions.target_cash_surplus_margin || 0) * 100)
  const gap = decisions.price_gap_to_target || 0

  return (
    <div className="card">
      <h2>Pricing Simulator</h2>
      <div className="input-form">
        <Field label="Early seats" value={pricing.early.seats} onChange={(v) => updateField('pricing.early.seats', v)} />
        <Field label="Early price (€)" value={pricing.early.price} onChange={(v) => updateField('pricing.early.price', v)} />
        <Field label="Standard seats" value={pricing.standard.seats} onChange={(v) => updateField('pricing.standard.seats', v)} />
        <Field label="Standard price (€)" value={pricing.standard.price} onChange={(v) => updateField('pricing.standard.price', v)} />
        <Field label="Installment seats" value={pricing.installment.seats} onChange={(v) => updateField('pricing.installment.seats', v)} />
        <Field label="Installment price (€)" value={pricing.installment.price} onChange={(v) => updateField('pricing.installment.price', v)} />
        <Field label="Down-payment rate" value={config.assumptions.down_payment_rate} step={0.05} onChange={(v) => updateField('assumptions.down_payment_rate', v)} />
      </div>

      <hr style={{ margin: '1rem 0', border: 'none', borderTop: '1px solid var(--border)' }} />

      <div className="form-group" style={{ marginBottom: '0.5rem' }}>
        <label>Target margin % (current: {targetMarginPct}%)</label>
        <input
          type="range"
          min="0"
          max="50"
          step="1"
          value={targetMarginPct}
          onChange={(e) => {
            updateField('assumptions.target_cash_surplus_margin', (parseInt(e.target.value, 10) || 0) / 100)
            if (onRecalculate) onRecalculate()
          }}
          style={{ width: '100%' }}
        />
      </div>

      {gap > 0 ? (
        <div style={{ padding: '8px 12px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', color: '#b45309', fontSize: '0.875rem', marginBottom: '0.75rem' }}>
          ⚠️ Raise price by {fmtMoney(gap)} to hit a {targetMarginPct}% margin.
        </div>
      ) : (
        <div style={{ padding: '8px 12px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', color: '#15803d', fontSize: '0.875rem', marginBottom: '0.75rem' }}>
          ✅ You exceed the {targetMarginPct}% target margin by {fmtMoney(-gap)}.
        </div>
      )}

      <table>
        <tbody>
          <tr><td>Blended average price</td><td style={{ textAlign: 'right' }}>{fmtMoney(revenue?.average_gross_price)}</td></tr>
          <tr><td>Total gross receipts</td><td style={{ textAlign: 'right' }}>{fmtMoney(revenue?.participant_gross_receipts)}</td></tr>
          <tr><td>Immediate cash (down payments)</td><td style={{ textAlign: 'right' }}>{fmtMoney(revenue?.immediate_receipts)}</td></tr>
          <tr><td>Deferred receipts</td><td style={{ textAlign: 'right' }}>{fmtMoney(revenue?.deferred_receipts)}</td></tr>
          <tr><td>Net revenue (after VAT)</td><td style={{ textAlign: 'right' }}>{fmtMoney(revenue?.net_programme_revenue)}</td></tr>
          <tr><td>Cash surplus</td><td style={{ textAlign: 'right' }}>{fmtMoney(decisions.cash_surplus)}</td></tr>
          <tr>
            <td>Target margin price ({targetMarginPct}%)</td>
            <td style={{ textAlign: 'right', fontWeight: 600, color: '#2563eb' }}>{fmtMoney(decisions.target_margin_average_price)}</td>
          </tr>
          <tr><td>Break-even price</td><td style={{ textAlign: 'right' }}>{fmtMoney(decisions.cash_break_even_average_price)}</td></tr>
          <tr>
            <td>Minimum participants at current avg price</td>
            <td style={{ textAlign: 'right' }}>{decisions.minimum_viable_cohort_size}</td>
          </tr>
        </tbody>
      </table>

      <div style={{ marginTop: '0.75rem', padding: '8px 12px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', color: '#1d4ed8', fontSize: '0.875rem' }}>
        💡 Recommended: {fmtMoney(decisions.target_margin_average_price)} average price for a {targetMarginPct}% margin
        {decisions.break_even_cohort_size > 0 && (
          <> · at the current price you need at least {decisions.minimum_viable_cohort_size} paying participants to break even</>
        )}
      </div>
    </div>
  )
}
