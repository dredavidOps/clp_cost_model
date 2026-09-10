import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#2563eb', '#16a34a', '#ca8a04', '#9333ea', '#dc2626']

function fmtMoney(value) {
  return `€${Number(value).toLocaleString('en-IE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function CostBreakdownChart({ totalCosts }) {
  if (!totalCosts) return null
  const data = [
    { name: 'Tools', value: totalCosts.tools_eur },
    { name: 'Mentors', value: totalCosts.mentors },
    { name: 'Internal Team', value: totalCosts.internal_team },
    { name: 'Operational', value: totalCosts.operational },
    { name: 'Other Costs', value: totalCosts.other },
  ].filter((d) => d.value > 0)

  const total = data.reduce((sum, d) => sum + d.value, 0)

  return (
    <div className="card">
      <h2>Cost Breakdown</h2>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => fmtMoney(value)} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <table>
        <tbody>
          {data.map((d, i) => (
            <tr key={d.name}>
              <td style={{ color: COLORS[i % COLORS.length] }}>● {d.name}</td>
              <td style={{ textAlign: 'right' }}>{fmtMoney(d.value)}</td>
              <td style={{ textAlign: 'right' }}>{total ? `${((d.value / total) * 100).toFixed(1)}%` : '0%'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
