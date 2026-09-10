import { useEffect } from 'react'
import useStore from './store'
import Layout from './components/Layout'
import SimulatorPanel from './components/SimulatorPanel'
import InputsPanel from './components/InputsPanel'
import ToolsPanel from './components/ToolsPanel'
import CalculationsPanel from './components/CalculationsPanel'
import ScenariosPanel from './components/ScenariosPanel'
import SensitivityPanel from './components/SensitivityPanel'
import CashFlowPanel from './components/CashFlowPanel'
import BreakEvenPanel from './components/BreakEvenPanel'
import ChecksPanel from './components/ChecksPanel'

const panels = {
  simulator: <SimulatorPanel />,
  inputs: <InputsPanel />,
  tools: <ToolsPanel />,
  calculations: <CalculationsPanel />,
  scenarios: <ScenariosPanel />,
  sensitivity: <SensitivityPanel />,
  cashflow: <CashFlowPanel />,
  breakeven: <BreakEvenPanel />,
  checks: <ChecksPanel />,
}

function App() {
  const { config, loadDefaults, error } = useStore()

  useEffect(() => {
    loadDefaults()
  }, [loadDefaults])

  if (!config) {
    return <div className="loading">Loading dashboard…</div>
  }

  return (
    <Layout>
      {error && <div className="error">{error}</div>}
      {panels[useStore.getState().activePanel] || panels.simulator}
    </Layout>
  )
}

export default App
