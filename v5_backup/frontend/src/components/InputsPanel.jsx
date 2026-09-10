import useStore from '../store'
import { fmtCurrency } from './Formatters'

function InputsPanel() {
  const { config, result, updateConfig } = useStore()

  if (!config || !result) return <div className="loading">Loading…</div>

  const ws = config.workstreams
  const cap = config.mentor_capacity_per_mentor
  const wsRows = [
    {
      name: 'IT Systems Admin',
      key: 'it_systems_admin',
      planned: ws.it_systems_admin,
      mentors: Math.ceil(ws.it_systems_admin / cap),
    },
    {
      name: 'Data, BI & AI',
      key: 'data_bi_ai',
      planned: ws.data_bi_ai,
      mentors: Math.ceil(ws.data_bi_ai / cap),
    },
    {
      name: 'Product / Operations',
      key: 'product_project_ops',
      planned: ws.product_project_ops,
      mentors: Math.ceil(ws.product_project_ops / cap),
    },
    {
      name: 'Digital Marketing / Growth',
      key: 'digital_marketing_growth',
      planned: ws.digital_marketing_growth,
      mentors: Math.ceil(ws.digital_marketing_growth / cap),
    },
  ]

  return (
    <div className="panel inputs-panel">
      <div className="card">
        <h3>Cohort Structure</h3>
        <table>
          <thead>
            <tr>
              <th>Workstream</th>
              <th>Planned</th>
              <th>Minimum</th>
              <th>Capacity / mentor</th>
              <th>Required mentors</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {wsRows.map((row) => (
              <tr key={row.key}>
                <td>{row.name}</td>
                <td>
                  <input
                    type="number"
                    value={row.planned}
                    onChange={(e) =>
                      updateConfig(`workstreams.${row.key}`, parseInt(e.target.value) || 0)
                    }
                  />
                </td>
                <td>{config.minimum_per_workstream}</td>
                <td>{cap}</td>
                <td>{row.mentors}</td>
                <td>{row.planned >= config.minimum_per_workstream ? 'OK' : 'BELOW MIN'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Pricing & Seat Mix</h3>
        <table>
          <thead>
            <tr>
              <th>Place type</th>
              <th>Seats</th>
              <th>Price / seat</th>
              <th>Gross receipts</th>
            </tr>
          </thead>
          <tbody>
            {[
              ['Early payment', 'early_payment_seats', 'early_payment_price'],
              ['Standard payment', 'standard_payment_seats', 'standard_payment_price'],
              ['Installment plan', 'installment_seats', 'installment_price'],
            ].map(([label, seatKey, priceKey]) => {
              const seats = config.seat_mix[seatKey]
              const price = config.seat_mix[priceKey]
              return (
                <tr key={seatKey}>
                  <td>{label}</td>
                  <td>
                    <input
                      type="number"
                      value={seats}
                      onChange={(e) =>
                        updateConfig(`seat_mix.${seatKey}`, parseInt(e.target.value) || 0)
                      }
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step={10}
                      value={price}
                      onChange={(e) =>
                        updateConfig(`seat_mix.${priceKey}`, parseFloat(e.target.value) || 0)
                      }
                    />
                  </td>
                  <td>{fmtCurrency(seats * price)}</td>
                </tr>
              )
            })}
            <tr className="total-row">
              <td>Total</td>
              <td>{result.revenue.participant_gross_receipts / result.revenue.average_gross_price_per_participant}</td>
              <td>Avg {fmtCurrency(result.revenue.average_gross_price_per_participant)}</td>
              <td><strong>{fmtCurrency(result.revenue.participant_gross_receipts)}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Internal Team</h3>
        <table>
          <thead>
            <tr>
              <th>Member</th>
              <th>Include</th>
              <th>Weekly hrs</th>
              <th>Weeks</th>
              <th>Rate</th>
              <th>Payment</th>
              <th>M365</th>
            </tr>
          </thead>
          <tbody>
            {config.internal_team.map((member, idx) => (
              <tr key={member.id}>
                <td>{member.name}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={member.include}
                    onChange={(e) =>
                      updateConfig(`internal_team.${idx}.include`, e.target.checked)
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step={0.5}
                    value={member.weekly_hours}
                    onChange={(e) =>
                      updateConfig(
                        `internal_team.${idx}.weekly_hours`,
                        parseFloat(e.target.value) || 0
                      )
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    value={member.weeks}
                    onChange={(e) =>
                      updateConfig(`internal_team.${idx}.weeks`, parseInt(e.target.value) || 0)
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    value={member.hourly_rate}
                    onChange={(e) =>
                      updateConfig(
                        `internal_team.${idx}.hourly_rate`,
                        parseFloat(e.target.value) || 0
                      )
                    }
                  />
                </td>
                <td>{fmtCurrency(member.weekly_hours * member.weeks * member.hourly_rate)}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={member.m365_account}
                    onChange={(e) =>
                      updateConfig(`internal_team.${idx}.m365_account`, e.target.checked)
                    }
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Mentor Assumptions</h3>
        <table>
          <tbody>
            <tr>
              <td>Contact hours / week</td>
              <td>
                <input
                  type="number"
                  step={0.5}
                  value={config.mentor_contact_hours_per_week}
                  onChange={(e) => updateConfig('mentor_contact_hours_per_week', parseFloat(e.target.value) || 0)}
                />
              </td>
            </tr>
            <tr>
              <td>Prep hours / week</td>
              <td>
                <input
                  type="number"
                  step={0.5}
                  value={config.mentor_prep_hours_per_week}
                  onChange={(e) => updateConfig('mentor_prep_hours_per_week', parseFloat(e.target.value) || 0)}
                />
              </td>
            </tr>
            <tr>
              <td>Setup hours / mentor</td>
              <td>
                <input
                  type="number"
                  value={config.mentor_setup_hours}
                  onChange={(e) => updateConfig('mentor_setup_hours', parseFloat(e.target.value) || 0)}
                />
              </td>
            </tr>
            <tr>
              <td>Hourly rate</td>
              <td>
                <input
                  type="number"
                  value={config.mentor_hourly_rate}
                  onChange={(e) => updateConfig('mentor_hourly_rate', parseFloat(e.target.value) || 0)}
                />
              </td>
            </tr>
            <tr>
              <td>Mentor capacity</td>
              <td>
                <input
                  type="number"
                  value={config.mentor_capacity_per_mentor}
                  onChange={(e) => updateConfig('mentor_capacity_per_mentor', parseInt(e.target.value) || 1)}
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default InputsPanel
