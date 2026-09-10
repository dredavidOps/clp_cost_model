import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

function fmtCurrency(value) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(value)
}

function marginStatus(marginPct) {
  if (marginPct >= 30) return 'healthy'
  if (marginPct >= 15) return 'tight'
  return 'risk'
}

function SensitivityLine({ title, data, dataKey, xFormatter, valueLabel }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={dataKey} tickFormatter={xFormatter} tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={(v) => `${v.toFixed(0)}%`} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value) => [`${value.toFixed(1)}%`, 'Margin %']}
            labelFormatter={(label) => `${valueLabel}: ${xFormatter(label)}`}
          />
          <Line type="monotone" dataKey="margin_pct" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function SensitivityCharts({ sensitivity }) {
  const feeData = sensitivity.participant_fee.map((point) => ({
    ...point,
    status: marginStatus(point.margin_pct),
  }))

  const sizeData = sensitivity.cohort_size.map((point) => ({
    ...point,
    status: marginStatus(point.margin_pct),
  }))

  return (
    <>
      <SensitivityLine
        title="Sensitivity: Participant Fee"
        data={feeData}
        dataKey="value"
        xFormatter={(v) => fmtCurrency(v)}
        valueLabel="Fee"
      />
      <SensitivityLine
        title="Sensitivity: Cohort Size"
        data={sizeData}
        dataKey="value"
        xFormatter={(v) => Math.round(v)}
        valueLabel="Size"
      />
    </>
  )
}

export default SensitivityCharts
