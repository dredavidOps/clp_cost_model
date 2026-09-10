import useStore from '../store'
import { fmtCurrency } from './Formatters'

function ToolsPanel() {
  const { config, result, updateConfig } = useStore()

  if (!config || !result) return <div className="loading">Loading…</div>

  const tools = config.tools || []

  const scopeTotals = {}
  tools.forEach((tool, idx) => {
    if (tool.include) {
      scopeTotals[tool.scope] = (scopeTotals[tool.scope] || 0) + (tool.included_cost || 0)
    }
  })

  return (
    <div className="panel tools-panel">
      <div className="card">
        <h3>Tool Registry</h3>
        <table>
          <thead>
            <tr>
              <th>Scope</th>
              <th>Tool / Service</th>
              <th>Include</th>
              <th>Basis</th>
              <th>Unit cost</th>
              <th>Qty</th>
              <th>Included cost</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            {tools.map((tool, idx) => (
              <tr key={idx}>
                <td>{tool.scope}</td>
                <td>{tool.name}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={tool.include}
                    onChange={(e) =>
                      updateConfig(`tools.${idx}.include`, e.target.checked)
                    }
                  />
                </td>
                <td>{tool.cost_basis}</td>
                <td>{fmtCurrency(tool.unit_cost)}</td>
                <td>{tool.quantity}</td>
                <td>{fmtCurrency(tool.included_cost)}</td>
                <td>{tool.owner}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="panel-grid two-col">
        <div className="card">
          <h3>Cost Summary by Scope</h3>
          <table>
            <thead>
              <tr>
                <th>Scope</th>
                <th>Included cost</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(scopeTotals).map(([scope, total]) => (
                <tr key={scope}>
                  <td>{scope}</td>
                  <td>{fmtCurrency(total)}</td>
                </tr>
              ))}
              <tr className="total-row">
                <td>Total other tools</td>
                <td><strong>{fmtCurrency(result.costs.other_tools)}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>M365 Licences</h3>
          <table>
            <tbody>
              <tr>
                <td>Price / account / month</td>
                <td>
                  <input
                    type="number"
                    step={0.01}
                    value={config.m365_price_per_account_per_month}
                    onChange={(e) =>
                      updateConfig('m365_price_per_account_per_month', parseFloat(e.target.value) || 0)
                    }
                  />
                </td>
              </tr>
              <tr>
                <td>Total M365 cost</td>
                <td>{fmtCurrency(result.costs.m365_licences)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default ToolsPanel
