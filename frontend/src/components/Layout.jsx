export default function Layout({ children }) {
  return (
    <div className="app">
      <header>
        <h1>CareerLeap Pricing Dashboard</h1>
        <p>Interactive pricing, cost, and launch-readiness model for CareerLeap Academy.</p>
      </header>
      {children}
    </div>
  )
}
