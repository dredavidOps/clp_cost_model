export function fmtCurrency(value) {
  if (value === undefined || value === null) return '—'
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function fmtNumber(value, digits = 2) {
  if (value === undefined || value === null) return '—'
  return new Intl.NumberFormat('en-IE', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value)
}

export function fmtPercent(value, digits = 2) {
  if (value === undefined || value === null) return '—'
  return new Intl.NumberFormat('en-IE', {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value)
}

export function statusClass(status) {
  if (status === 'GO' || status === 'PASS' || status === 'VIABLE' || status === 'OK' || status === 'surplus') {
    return 'status-good'
  }
  if (status === 'REVIEW' || status === 'HOLD' || status === 'deficit') {
    return 'status-warn'
  }
  return 'status-bad'
}
