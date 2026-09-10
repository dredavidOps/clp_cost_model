import useStore from '../store'

const panels = [
  { id: 'simulator', label: 'Simulator' },
  { id: 'inputs', label: 'Inputs' },
  { id: 'tools', label: 'Tools' },
  { id: 'calculations', label: 'Calculations' },
  { id: 'scenarios', label: 'Scenarios' },
  { id: 'sensitivity', label: 'Sensitivity' },
  { id: 'cashflow', label: 'Cash Flow' },
  { id: 'breakeven', label: 'Break-even' },
  { id: 'checks', label: 'Checks' },
]

function Layout({ children }) {
  const { activePanel, setPanel, lastSaved, exportCSV } = useStore()

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>CareerLeap</h1>
          <span className="sidebar-sub">Business Model v5</span>
        </div>
        <nav className="sidebar-nav">
          {panels.map((p) => (
            <button
              key={p.id}
              className={activePanel === p.id ? 'active' : ''}
              onClick={() => setPanel(p.id)}
            >
              {p.label}
            </button>
          ))}
        </nav>
      </aside>

      <div className="main-area">
        <header className="top-bar">
          <h2>{panels.find((p) => p.id === activePanel)?.label}</h2>
          <div className="top-bar-actions">
            {lastSaved && (
              <span className="last-saved">
                Last calculated: {new Date(lastSaved).toLocaleTimeString()}
              </span>
            )}
            <button className="export-btn" onClick={exportCSV}>
              Export CSV
            </button>
          </div>
        </header>
        <main className="panel-content">{children}</main>
      </div>
    </div>
  )
}

export default Layout
