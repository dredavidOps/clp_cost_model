function fmtCurrency(value) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function statusIcon(marginPct) {
  if (marginPct >= 30) return '✓'
  if (marginPct >= 15) return '⚠'
  return '✗'
}

function PricingTiersTable({ tiers }) {
  return (
    <div className="card">
      <h2>Recommended Pricing Tiers</h2>
      <table>
        <thead>
          <tr>
            <th>Tier</th>
            <th>Fee</th>
            <th>Projected Margin</th>
            <th>Margin %</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {tiers.map((tier) => (
            <tr key={tier.name}>
              <td>{tier.name}</td>
              <td>{fmtCurrency(tier.fee)}</td>
              <td>{fmtCurrency(tier.projected_margin)}</td>
              <td>{tier.projected_margin_pct.toFixed(1)}%</td>
              <td>{statusIcon(tier.projected_margin_pct)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default PricingTiersTable
