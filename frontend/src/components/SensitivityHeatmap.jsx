function colorForMargin(margin) {
  if (margin >= 0.30) return '#14532d'
  if (margin >= 0.10) return '#86efac'
  if (margin >= 0) return '#fde047'
  return '#f87171'
}

// Q5/Q8: price × cohort-size margin grid with the break-even frontier outlined.
export default function SensitivityHeatmap({ sensitivity }) {
  if (!sensitivity || !sensitivity.grid) return null
  const { grid, break_even_prices, current_reference } = sensitivity

  // rows: cohort sizes (outer), cols: prices (inner)
  const prices = grid[0].map((cell) => cell.average_price)
  const cohortSizes = grid.map((row) => row[0].participants)

  // Per row, the break-even cell is the cheapest price whose surplus is >= 0
  const breakEvenCol = grid.map((row) => row.findIndex((cell) => cell.cash_surplus >= 0))

  return (
    <div className="card wide">
      <h2>Sensitivity Heatmap</h2>
      <p style={{ color: 'var(--muted)', fontSize: '0.875rem', marginTop: 0 }}>
        Cash surplus margin by average price (x) and cohort size (y). Outlined cells mark the break-even frontier (surplus crosses €0).
        {current_reference && (
          <> Current plan: {current_reference.participants} participants @ {`€${current_reference.average_gross_price}`}.</>
        )}
      </p>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ fontSize: '0.75rem', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ padding: 4 }}>Price \ Size</th>
              {prices.map((p) => (
                <th key={p} style={{ padding: 4 }}>€{p}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {grid.map((row, i) => (
              <tr key={cohortSizes[i]}>
                <th style={{ padding: 4 }}>{cohortSizes[i]}</th>
                {row.map((cell, j) => {
                  const isBreakEven = j === breakEvenCol[i]
                  return (
                    <td
                      key={j}
                      style={{
                        background: colorForMargin(cell.cash_surplus_margin),
                        color: cell.cash_surplus_margin >= 0.30 ? '#fff' : '#1e293b',
                        textAlign: 'center',
                        minWidth: 36,
                        padding: 4,
                        outline: isBreakEven ? '2px solid #1e293b' : 'none',
                        outlineOffset: -2,
                        fontWeight: isBreakEven ? 700 : 400,
                      }}
                      title={`Price €${cell.average_price}, Size ${cell.participants}: surplus €${cell.cash_surplus}, margin ${(cell.cash_surplus_margin * 100).toFixed(1)}%${isBreakEven ? ' — break-even frontier' : ''}`}
                    >
                      {(cell.cash_surplus_margin * 100).toFixed(0)}%
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', fontSize: '0.75rem', flexWrap: 'wrap' }}>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, background: '#14532d', marginRight: 4 }}></span>≥30%</span>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, background: '#86efac', marginRight: 4 }}></span>10–30%</span>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, background: '#fde047', marginRight: 4 }}></span>0–10%</span>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, background: '#f87171', marginRight: 4 }}></span>&lt;0%</span>
        <span><span style={{ display: 'inline-block', width: 12, height: 12, border: '2px solid #1e293b', marginRight: 4 }}></span>Break-even frontier</span>
      </div>
      {break_even_prices && break_even_prices.length > 0 && (
        <p style={{ color: 'var(--muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
          Break-even price by cohort size:{' '}
          {break_even_prices.map((b) => `${b.participants} ppt → €${b.break_even_price.toFixed(0)}`).join(' · ')}
        </p>
      )}
    </div>
  )
}
