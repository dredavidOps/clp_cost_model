import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { workstreamLabels } from '../config'

function fmtMoney(value, currency = 'EUR') {
  const sym = currency === 'USD' ? '$' : '€'
  return `${sym}${Number(value).toLocaleString('en-IE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function WorkstreamToolsTable({ tools }) {
  if (!tools) return null
  const rows = Object.entries(tools.workstream_breakdown).map(([ws, v]) => ({ ...v, key: ws }))

  return (
    <div className="card wide">
      <h2>Workstream Tool Costs</h2>
      <div style={{ width: '100%', height: 240, marginBottom: '1rem' }}>
        <ResponsiveContainer>
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="key" />
            <YAxis />
            <Tooltip formatter={(value) => fmtMoney(value, 'EUR')} />
            <Bar dataKey="workstream_total_eur" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>Workstream</th>
              <th>Monthly $/ppt</th>
              <th>Base $/ppt</th>
              <th>Contingency $/ppt</th>
              <th>Total $/ppt</th>
              <th>Total Workstream $</th>
              <th>Total Workstream €</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key}>
                <td>{workstreamLabels[row.key] || row.key}</td>
                <td>{fmtMoney(row.monthly_per_ppt_usd, 'USD')}</td>
                <td>{fmtMoney(row.base_per_ppt_usd, 'USD')}</td>
                <td>{fmtMoney(row.contingency_per_ppt_usd, 'USD')}</td>
                <td>{fmtMoney(row.total_per_ppt_usd, 'USD')}</td>
                <td>{fmtMoney(row.workstream_total_usd, 'USD')}</td>
                <td>{fmtMoney(row.workstream_total_eur, 'EUR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
