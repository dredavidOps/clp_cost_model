function fmtCurrency(value) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function AnnualProjection({ projection }) {
  return (
    <div className="card">
      <h2>Annual Projection ({projection.cohorts_per_year} cohorts/year)</h2>
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="label">Total Participants</div>
          <div className="value">{projection.total_participants}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Annual Revenue</div>
          <div className="value">{fmtCurrency(projection.annual_revenue)}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Annual Costs</div>
          <div className="value">{fmtCurrency(projection.annual_costs)}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Annual Margin</div>
          <div className="value">{fmtCurrency(projection.annual_margin)}</div>
        </div>
      </div>
    </div>
  )
}

export default AnnualProjection
