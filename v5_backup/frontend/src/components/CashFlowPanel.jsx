import { useEffect, useState } from 'react'
import useStore from '../store'
import * as api from '../api'
import { fmtCurrency } from './Formatters'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'

function CashFlowPanel() {
  const { config } = useStore()
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!config) return
    api.getCashFlow(config).then(setData)
  }, [config])

  if (!data) return <div className="loading">Loading cash flow…</div>

  const chartData = data.monthly_schedule.map((m) => ({
    phase: m.phase,
    opening: m.opening_balance,
    closing: m.closing_balance,
  }))

  return (
    <div className="panel cashflow-panel">
      <div className="card">
        <h3>Monthly Cash Flow Schedule</h3>
        <table>
          <thead>
            <tr>
              <th>Phase</th>
              <th>Net revenue collected</th>
              <th>Cash costs paid</th>
              <th>Net cash movement</th>
              <th>Opening balance</th>
              <th>Closing balance</th>
            </tr>
          </thead>
          <tbody>
            {data.monthly_schedule.map((m, i) => (
              <tr key={i}>
                <td>{m.phase}</td>
                <td>{fmtCurrency(m.net_revenue_collected)}</td>
                <td>{fmtCurrency(m.cash_costs_paid)}</td>
                <td className={m.net_cash_movement >= 0 ? 'good' : 'bad'}>
                  {fmtCurrency(m.net_cash_movement)}
                </td>
                <td>{fmtCurrency(m.opening_balance)}</td>
                <td className={m.closing_balance >= 0 ? 'good' : 'bad'}>
                  {fmtCurrency(m.closing_balance)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="panel-grid two-col">
        <div className="card">
          <h3>Cash Balance Chart</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="phase" />
              <YAxis tickFormatter={(v) => `€${v}`} />
              <Tooltip formatter={(v) => fmtCurrency(v)} />
              <Line type="monotone" dataKey="opening" stroke="#64748b" dot={false} />
              <Line type="monotone" dataKey="closing" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Cash Flow Outputs</h3>
          <table>
            <tbody>
              <tr>
                <td>Minimum funding buffer</td>
                <td>{fmtCurrency(data.minimum_funding_buffer)}</td>
              </tr>
              <tr>
                <td>Lowest projected balance</td>
                <td className={data.lowest_projected_balance >= 0 ? 'good' : 'bad'}>
                  {fmtCurrency(data.lowest_projected_balance)}
                </td>
              </tr>
              <tr>
                <td>Ending balance</td>
                <td className={data.ending_balance >= 0 ? 'good' : 'bad'}>
                  {fmtCurrency(data.ending_balance)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default CashFlowPanel
