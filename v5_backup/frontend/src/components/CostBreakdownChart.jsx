import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

function fmtCurrency(value) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function CostBreakdownChart({ result }) {
  const data = [
    { name: 'Revenue', amount: result.revenue },
    { name: 'Tool Costs', amount: result.tool_costs },
    { name: 'Overhead', amount: result.overhead },
    { name: 'Lead Costs', amount: result.lead_costs },
    { name: 'Placement Bonuses', amount: result.placement_bonuses },
  ]

  return (
    <div className="card">
      <h2>Revenue & Cost Breakdown</h2>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={(v) => `€${v}`} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value) => fmtCurrency(value)} />
          <Bar dataKey="amount" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default CostBreakdownChart
