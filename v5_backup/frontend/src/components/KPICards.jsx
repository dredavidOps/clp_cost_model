function fmtCurrency(value) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function fmtPercent(value) {
  return `${value.toFixed(1)}%`
}

function marginClass(marginPct) {
  if (marginPct >= 30) return 'status-healthy'
  if (marginPct >= 15) return 'status-tight'
  return 'status-risk'
}

function KPICards({ result }) {
  const cards = [
    { label: 'Revenue', value: fmtCurrency(result.revenue) },
    { label: 'Total Costs', value: fmtCurrency(result.total_costs) },
    { label: 'Net Margin', value: fmtCurrency(result.net_margin) },
    {
      label: 'Margin %',
      value: fmtPercent(result.margin_pct),
      className: marginClass(result.margin_pct),
    },
    { label: 'Break-even Size', value: result.break_even_size.toFixed(1) },
    { label: 'Profit / Participant', value: fmtCurrency(result.profit_per_participant) },
  ]

  return (
    <div className="kpi-grid">
      {cards.map(({ label, value, className }) => (
        <div className="kpi-card" key={label}>
          <div className="label">{label}</div>
          <div className={`value ${className || ''}`}>{value}</div>
        </div>
      ))}
    </div>
  )
}

export default KPICards
