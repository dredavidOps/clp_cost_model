const API_BASE = 'http://127.0.0.1:8000'

async function post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  return res.json()
}

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  return res.json()
}

export const getDefaults = () => get('/api/config/defaults')
export const calculate = (config) => post('/api/calculate', config)
export const calculateSummary = (config) => post('/api/calculate/summary', config)
export const calculateBreakEven = (config) => post('/api/calculate/break-even', config)
export const calculateSensitivity = (config) => post('/api/calculate/sensitivity', config)
export const calculateTeam = (config) => post('/api/calculate/team', config)
export const calculateChecks = (config) => post('/api/calculate/checks', config)
export const compareScenarios = (scenarios, names) => post('/api/scenarios/compare', { scenarios, names })

export async function exportCsv(config) {
  const res = await fetch(`${API_BASE}/api/export/csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'careerleap_pricing_scenario.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export const api = {
  getDefaults,
  calculate,
  calculateSummary,
  calculateBreakEven,
  calculateSensitivity,
  calculateTeam,
  calculateChecks,
  compareScenarios,
  exportCsv,
}
