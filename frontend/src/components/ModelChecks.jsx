function statusColor(status) {
  if (status === 'PASS') return 'var(--success, #16a34a)'
  if (status === 'WARN') return 'var(--warning, #d97706)'
  return 'var(--danger, #dc2626)'
}

export default function ModelChecks({ checks }) {
  if (!checks) return null

  return (
    <div className="card wide">
      <h2>
        Model Checks
        <span style={{ float: 'right', color: checks.overall_status === 'PASS' ? 'var(--success, #16a34a)' : 'var(--danger, #dc2626)' }}>
          {checks.overall_status}
        </span>
      </h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Check</th>
            <th>Actual</th>
            <th>Expected</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {checks.checks.map((check, i) => (
            <tr key={i} title={`Fix in: ${check.where_to_fix} — ${check.why_it_matters}`}>
              <td>{i + 1}</td>
              <td>{check.name}</td>
              <td>{check.actual}</td>
              <td>{check.expected}</td>
              <td style={{ color: statusColor(check.status), fontWeight: 600 }}>{check.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {checks.blocking_gates && checks.blocking_gates.length > 0 && (
        <div style={{ marginTop: '1rem', padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#dc2626', fontSize: '0.875rem' }}>
          <strong>Blocking gates:</strong>
          <ul style={{ margin: '6px 0 0 18px', padding: 0 }}>
            {checks.blocking_gates.map((gate, i) => (
              <li key={i}>{gate}</li>
            ))}
          </ul>
        </div>
      )}
      <div style={{ marginTop: '1rem', fontWeight: 600, color: checks.launch_readiness === 'GO' ? 'var(--success, #16a34a)' : checks.launch_readiness === 'HOLD' ? 'var(--danger, #dc2626)' : 'var(--warning, #d97706)' }}>
        Launch readiness: {checks.launch_readiness}
      </div>
    </div>
  )
}
