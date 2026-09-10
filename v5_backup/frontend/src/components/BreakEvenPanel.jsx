import { useEffect, useState } from 'react'
import useStore from '../store'
import * as api from '../api'
import { fmtCurrency, statusClass } from './Formatters'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

function BreakEvenPanel() {
  const { config, result } = useStore()
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!config) return
    api.getBreakEven(config).then(setData)
  }, [config])

  if (!data || !result) return <div className="loading">Loading break-even…</div>

  const current = data.current_model

  return (
    <div className="panel breakeven-panel">
      <div className="card">
        <h3>Current Model Snapshot</h3>
        <div className="decision-row">
          <div>
            <span className="label">Planned participants</span>
            <strong>{current.planned_participants}</strong>
          </div>
          <div>
            <span className="label">Current average price</span>
            <strong>{fmtCurrency(current.current_average_price)}</strong>
          </div>
          <div>
            <span className="label">Current cash surplus</span>
            <strong className={current.current_cash_surplus >= 0 ? 'good' : 'bad'}>
              {fmtCurrency(current.current_cash_surplus)}
            </strong>
          </div>
          <div>
            <span className="label">Economics</span>
            <strong className={statusClass(current.projected_economics_status)}>
              {current.projected_economics_status}
            </strong>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Break-even Curve</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data.curve}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="average_gross_price"
              tickFormatter={(v) => `€${v}`}
              type="number"
              domain={['dataMin', 'dataMax']}
            />
            <YAxis tickFormatter={(v) => `€${v}`} />
            <Tooltip formatter={(v) => fmtCurrency(v)} />
            <ReferenceLine y={0} stroke="#dc2626" strokeDasharray="3 3" />
            <ReferenceLine
              x={data.cash_break_even_price}
              stroke="#16a34a"
              label="Break-even"
            />
            <ReferenceLine
              x={current.current_average_price}
              stroke="#2563eb"
              label="Current"
            />
            <Line
              type="monotone"
              dataKey="cash_surplus"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3>Curve Data</h3>
        <table>
          <thead>
            <tr>
              <th>Price</th>
              <th>Gross receipts</th>
              <th>Net revenue</th>
              <th>Cash cost</th>
              <th>Surplus</th>
              <th>Margin</th>
            </tr>
          </thead>
          <tbody>
            {data.curve.map((p, i) => (
              <tr key={i}>
                <td>{fmtCurrency(p.average_gross_price)}</td>
                <td>{fmtCurrency(p.gross_receipts)}</td>
                <td>{fmtCurrency(p.net_programme_revenue)}</td>
                <td>{fmtCurrency(p.total_cohort_cash_cost)}</td>
                <td className={p.cash_surplus >= 0 ? 'good' : 'bad'}>
                  {fmtCurrency(p.cash_surplus)}
                </td>
                <td>{(p.cash_surplus_margin * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default BreakEvenPanel
