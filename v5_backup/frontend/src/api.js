const API_BASE = '/api'

async function post(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const error = await response.text()
    throw new Error(`API error ${response.status}: ${error}`)
  }
  return response.json()
}

export async function getDefaults() {
  const response = await fetch(`${API_BASE}/defaults`)
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}

export async function getCareerTracks() {
  const response = await fetch(`${API_BASE}/career-tracks`)
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}

export async function getTeamRoster() {
  const response = await fetch(`${API_BASE}/team-roster`)
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}

export async function getPricingTiers() {
  const response = await fetch(`${API_BASE}/pricing-tiers`)
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}

export async function calculate(config) {
  return post('/calculate', config)
}

export async function getScenarios(config) {
  return post('/scenarios', config)
}

export async function getSensitivity(config) {
  return post('/sensitivity', config)
}

export async function getCashFlow(config) {
  return post('/cash-flow', config)
}

export async function getBreakEven(config) {
  return post('/break-even', config)
}

export async function getChecks(config) {
  return post('/checks', config)
}

export async function exportCSV(config) {
  const response = await fetch(`${API_BASE}/export/csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!response.ok) {
    const error = await response.text()
    throw new Error(`API error ${response.status}: ${error}`)
  }
  return response.blob()
}
