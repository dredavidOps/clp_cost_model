import { useEffect, useState } from 'react'
import useStore from '../store'
import * as api from '../api'
import { fmtCurrency } from './Formatters'

function SensitivityPanel() {
  const { config } = useStore()
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!config) return
    api.getSensitivity(config).then(setData)
  }, [config])

  if (!data) return <div className="loading">Loading sensitivity…</div>

  const { grid, break_even_prices, controls } = data
  const priceHeaders = grid[0].map((cell) => cell.average_price)
  const participantLabels = grid.map((row) => row[0].participants)

  function cellColor(surplus) {
    if (surplus >= 0) {
      const intensity = Math.min(1, surplus / 3000)
      return `rgba(34, 197, 94, ${0.1 + intensity * 0.4})`
    }
    const intensity = Math.min(1, Math.abs(surplus) / 3000)
    return `rgba(239, 68, 68, ${0.1 + intensity * 0.4})`
  }

  return (
    <div className="panel sensitivity-panel">
      <div className="card">
        <h3>Price × Participants Heatmap</h3>
        <div className="heatmap-wrapper">
          <table className="heatmap">
            <thead>
              <tr>
                <th>Participants \ Price</th>
                {priceHeaders.map((p) => (
                  <th key={p}>{fmtCurrency(p)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {grid.map((row, i) => (
                <tr key={i}>
                  <td>{participantLabels[i]}</td>
                  {row.map((cell, j) => (
                    <td
                      key={j}
                      style={{ backgroundColor: cellColor(cell.cash_surplus) }}
                      title={`Price ${fmtCurrency(cell.average_price)}, Participants ${cell.participants}`}
                    >
                      {fmtCurrency(cell.cash_surplus)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h3>Break-even Prices</h3>
        <table>
          <thead>
            <tr>
              <th>Participants</th>
              <th>Break-even average price</th>
            </tr>
          </thead>
          <tbody>
            {break_even_prices.map((row, i) => (
              <tr key={i}>
                <td>{row.participants}</td>
                <td>{fmtCurrency(row.break_even_price)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default SensitivityPanel
