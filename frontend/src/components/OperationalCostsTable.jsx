import { operationalLabels, costBasisLabels } from '../config'

function fmtMoney(value) {
  return `€${Number(value).toLocaleString('en-IE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function OperationalCostsTable({ operational, config }) {
  if (!operational) return null

  const rows = Object.entries(operational.breakdown).map(([name, total]) => ({
    name,
    total,
    ...(config ? config[name] : {}),
  }))

  return (
    <div className="card wide">
      <h2>Operational Costs</h2>
      <table>
        <thead>
          <tr>
            <th>Cost item</th>
            <th>Cost basis</th>
            <th>Unit cost</th>
            <th>Quantity / seats</th>
            <th>Active months</th>
            <th>Total cost</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.name}>
              <td>{operationalLabels[item.name] || item.name}</td>
              <td>{costBasisLabels[item.cost_basis] || item.cost_basis || '—'}</td>
              <td>{item.unit_cost !== undefined ? fmtMoney(item.unit_cost) : '—'}</td>
              <td>{item.quantity !== undefined ? item.quantity : '—'}</td>
              <td>{item.active_months !== undefined ? item.active_months : '—'}</td>
              <td>{fmtMoney(item.total)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={5}>Total</th>
            <th>{fmtMoney(operational.total)}</th>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
