import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, ReferenceDot } from 'recharts'

function fmtMoney(value) {
  return `€${Number(value).toLocaleString('en-IE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

// Q3: price-surplus curve with prominent break-even / target / current markers
export default function BreakEvenChart({ breakEven, currentPrice }) {
  if (!breakEven || !breakEven.curve) return null
  const { curve, cash_break_even_price, target_margin_price, gap_current_vs_break_even } = breakEven

  return (
    <div className="card wide">
      <h2>Break-Even Analysis</h2>
      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer>
          <LineChart data={curve}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="average_gross_price" tickFormatter={(v) => `€${v}`} />
            <YAxis tickFormatter={(v) => `€${v}`} />
            <Tooltip formatter={(value) => fmtMoney(value)} />
            <ReferenceLine y={0} stroke="#64748b" strokeDasharray="4 4" />
            {currentPrice > 0 && (
              <ReferenceLine x={currentPrice} stroke="#ca8a04" strokeDasharray="4 4" label={{ value: 'Current', position: 'top' }} />
            )}
            <ReferenceLine x={cash_break_even_price} stroke="#dc2626" strokeDasharray="4 4" label={{ value: 'Break-even', position: 'top' }} />
            <ReferenceLine x={target_margin_price} stroke="#16a34a" strokeDasharray="4 4" label={{ value: 'Target', position: 'top' }} />
            <Line type="monotone" dataKey="cash_surplus" stroke="#2563eb" strokeWidth={2} dot={false} />
            {currentPrice > 0 && (() => {
              const pt = curve.reduce((best, p) =>
                Math.abs(p.average_gross_price - currentPrice) < Math.abs(best.average_gross_price - currentPrice) ? p : best
              , curve[0])
              return <ReferenceDot x={pt.average_gross_price} y={pt.cash_surplus} r={5} fill="#ca8a04" stroke="none" />
            })()}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
        Current blended price {fmtMoney(currentPrice || 0)} · Break-even {fmtMoney(cash_break_even_price)} · Target margin price {fmtMoney(target_margin_price)}
        {gap_current_vs_break_even !== undefined && (
          <>
            {' '}·{' '}
            <span style={{ color: gap_current_vs_break_even >= 0 ? '#16a34a' : '#dc2626', fontWeight: 600 }}>
              {gap_current_vs_break_even >= 0
                ? `${fmtMoney(gap_current_vs_break_even)} above break-even`
                : `${fmtMoney(-gap_current_vs_break_even)} below break-even`}
            </span>
          </>
        )}
      </p>
    </div>
  )
}
