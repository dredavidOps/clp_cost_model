import { useEffect, useState } from 'react'
import useStore from '../store'
import * as api from '../api'
import { statusClass } from './Formatters'

function ChecksPanel() {
  const { config } = useStore()
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!config) return
    api.getChecks(config).then(setData)
  }, [config])

  if (!data) return <div className="loading">Running model checks…</div>

  return (
    <div className="panel checks-panel">
      <div className={`status-banner ${statusClass(data.overall_status)}`}>
        Overall Status: <strong>{data.overall_status}</strong>
      </div>
      <div className={`status-banner ${statusClass(data.launch_readiness)}`}>
        Launch Readiness: <strong>{data.launch_readiness}</strong>
      </div>

      <div className="card">
        <h3>Model Validation Checks</h3>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Check</th>
              <th>Actual</th>
              <th>Expected</th>
              <th>Difference</th>
              <th>Tol</th>
              <th>Status</th>
              <th>Where to fix</th>
              <th>Why it matters</th>
            </tr>
          </thead>
          <tbody>
            {data.checks.map((check, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{check.name}</td>
                <td>{check.actual}</td>
                <td>{check.expected}</td>
                <td>{check.difference}</td>
                <td>{check.tolerance}</td>
                <td className={statusClass(check.status)}>{check.status}</td>
                <td>{check.where_to_fix}</td>
                <td>{check.why_it_matters}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ChecksPanel
