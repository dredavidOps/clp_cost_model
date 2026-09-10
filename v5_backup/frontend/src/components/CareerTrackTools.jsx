function fmtCurrency(value) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 2,
  }).format(value)
}

function fmtBillingModel(model) {
  const labels = {
    per_user_per_month: 'per user/mo',
    fixed_monthly: 'fixed monthly',
    free_tier: 'free tier',
    free: 'free',
    open_source: 'open source',
    bundled: 'bundled',
  }
  return labels[model] || model
}

function CareerTrackTools({ careerTrack }) {
  return (
    <div className="card">
      <h2>{careerTrack.label} — Tools & Pricing</h2>

      <p className="track-role">{careerTrack.role_in_simulation}</p>

      <div className="track-skills">
        <h3>Skills</h3>
        <div className="skill-tags">
          {careerTrack.skills.map((skill) => (
            <span key={skill} className="skill-tag">{skill}</span>
          ))}
        </div>
      </div>

      <div className="track-tools">
        <h3>Tools</h3>
        <ul className="tools-list">
          {careerTrack.tools.map((tool) => (
            <li key={tool.name} className="tool-item">
              <div className="tool-header">
                <span className="tool-name">{tool.name}</span>
                <span className="tool-price">
                  {fmtCurrency(tool.cost_per_user_per_month)}/user/mo
                </span>
              </div>
              <div className="tool-meta">
                <span className="tool-category">{tool.category}</span>
                <span className="tool-billing">{fmtBillingModel(tool.billing_model)}</span>
                {tool.free_tier_limit && (
                  <span className="tool-free-tier">({tool.free_tier_limit})</span>
                )}
              </div>
              <p className="tool-why">{tool.why_chosen}</p>
              {(tool.source_url || tool.last_verified) && (
                <div className="tool-verification">
                  {tool.source_url && (
                    <a
                      href={tool.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="tool-source-link"
                    >
                      View pricing
                    </a>
                  )}
                  {tool.last_verified && (
                    <span className="tool-last-verified">
                      Last verified: {tool.last_verified}
                    </span>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>

      <div className="tool-total">
        <span>Total per user</span>
        <span>{fmtCurrency(careerTrack.total_tool_cost_per_user_per_month)}/mo</span>
      </div>
      <div className="tool-total">
        <span>Cost per participant</span>
        <span>{fmtCurrency(careerTrack.track_cost_per_participant)}</span>
      </div>
    </div>
  )
}

export default CareerTrackTools
