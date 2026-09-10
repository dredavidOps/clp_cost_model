import useStore from '../store'
import { fmtCurrency, fmtPercent } from './Formatters'

function CalculationsPanel() {
  const { config, result } = useStore()

  if (!config || !result) return <div className="loading">Loading…</div>

  const r = result.revenue
  const c = result.costs
  const d = result.decisions

  return (
    <div className="panel calculations-panel">
      <div className="panel-grid two-col">
        <div className="card">
          <h3>Revenue Calculation</h3>
          <table>
            <tbody>
              <tr>
                <td>Early payment seats</td>
                <td>
                  {config.seat_mix.early_payment_seats} × {fmtCurrency(config.seat_mix.early_payment_price)}
                </td>
                <td>{fmtCurrency(config.seat_mix.early_payment_seats * config.seat_mix.early_payment_price)}</td>
              </tr>
              <tr>
                <td>Standard payment seats</td>
                <td>
                  {config.seat_mix.standard_payment_seats} × {fmtCurrency(config.seat_mix.standard_payment_price)}
                </td>
                <td>{fmtCurrency(config.seat_mix.standard_payment_seats * config.seat_mix.standard_payment_price)}</td>
              </tr>
              <tr>
                <td>Installment seats</td>
                <td>
                  {config.seat_mix.installment_seats} × {fmtCurrency(config.seat_mix.installment_price)}
                </td>
                <td>{fmtCurrency(config.seat_mix.installment_seats * config.seat_mix.installment_price)}</td>
              </tr>
              <tr className="total-row">
                <td>Participant gross receipts</td>
                <td></td>
                <td><strong>{fmtCurrency(r.participant_gross_receipts)}</strong></td>
              </tr>
              <tr>
                <td>VAT payable ({fmtPercent(config.vat_rate, 0)})</td>
                <td></td>
                <td>{fmtCurrency(r.vat_payable)}</td>
              </tr>
              <tr className="total-row">
                <td>Net programme revenue</td>
                <td></td>
                <td><strong>{fmtCurrency(r.net_programme_revenue)}</strong></td>
              </tr>
              <tr>
                <td>Average gross price / participant</td>
                <td></td>
                <td>{fmtCurrency(r.average_gross_price_per_participant)}</td>
              </tr>
              <tr>
                <td>Average net price / participant</td>
                <td></td>
                <td>{fmtCurrency(r.average_net_price_per_participant)}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>Cash Cost Calculation</h3>
          <table>
            <tbody>
              <tr><td>Mentor cost</td><td></td><td>{fmtCurrency(c.mentor_cost)}</td></tr>
              <tr><td>M365 licences</td><td></td><td>{fmtCurrency(c.m365_licences)}</td></tr>
              <tr><td>Other tools</td><td></td><td>{fmtCurrency(c.other_tools)}</td></tr>
              <tr><td>Internal team payments</td><td></td><td>{fmtCurrency(c.internal_team_payments)}</td></tr>
              <tr><td>Other external costs</td><td></td><td>{fmtCurrency(c.other_external_costs)}</td></tr>
              <tr><td>Payment processing fees</td><td></td><td>{fmtCurrency(c.payment_processing_fees)}</td></tr>
              <tr><td>Contingency reserve</td><td></td><td>{fmtCurrency(c.contingency_reserve)}</td></tr>
              <tr className="total-row">
                <td>Total cohort cash cost</td>
                <td></td>
                <td><strong>{fmtCurrency(c.total_cohort_cash_cost)}</strong></td>
              </tr>
              <tr>
                <td>Cash cost / participant</td>
                <td></td>
                <td>{fmtCurrency(c.cash_cost_per_participant)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h3>Decision Outputs</h3>
        <table>
          <tbody>
            <tr>
              <td>Cash surplus</td>
              <td>{fmtCurrency(d.cash_surplus)}</td>
              <td>Net revenue minus total cash cost</td>
            </tr>
            <tr>
              <td>Cash surplus margin</td>
              <td>{fmtPercent(d.cash_surplus_margin)}</td>
              <td>Surplus divided by net programme revenue</td>
            </tr>
            <tr>
              <td>Cash break-even average price</td>
              <td>{fmtCurrency(d.cash_break_even_average_price)}</td>
              <td>Price where surplus equals zero</td>
            </tr>
            <tr>
              <td>Target-margin average price</td>
              <td>{fmtCurrency(d.target_margin_average_price)}</td>
              <td>Price achieving {fmtPercent(config.target_cash_surplus_margin)} surplus margin</td>
            </tr>
            <tr>
              <td>Price gap to target</td>
              <td>{fmtCurrency(d.price_gap_to_target)}</td>
              <td>How much current average price must rise</td>
            </tr>
            <tr>
              <td>Minimum additional cash buffer</td>
              <td>{fmtCurrency(d.minimum_additional_cash_buffer)}</td>
              <td>Shortfall to cover if surplus is negative</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default CalculationsPanel
