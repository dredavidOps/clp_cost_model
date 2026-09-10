function fmtMoney(value) {
  return `€${Number(value).toLocaleString('en-IE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function TeamCompensationTable({ team }) {
  if (!team) return null

  return (
    <div className="card wide">
      <h2>Internal Team Compensation</h2>
      <table>
        <thead>
          <tr>
            <th>Role</th>
            <th>Monthly stipend</th>
            <th>Active months</th>
            <th>Total stipend</th>
            <th>M365 account?</th>
          </tr>
        </thead>
        <tbody>
          {team.members.map((row) => (
            <tr key={row.role}>
              <td>{row.role}</td>
              <td>{fmtMoney(row.monthly)}</td>
              <td>{row.months}</td>
              <td>{fmtMoney(row.total)}</td>
              <td>{row.m365_account ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={3}>Total</th>
            <th>{fmtMoney(team.total)}</th>
            <th></th>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
