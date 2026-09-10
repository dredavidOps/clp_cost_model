import { useState } from 'react'

const fields = [
  { key: 'participant_fee', label: 'Participant fee (€)', type: 'number' },
  { key: 'cohort_size', label: 'Cohort size', type: 'number' },
  { key: 'duration_months', label: 'Duration (months)', type: 'number' },
  { key: 'num_leads', label: 'Team leads', type: 'number' },
  { key: 'stipend_per_lead', label: 'Stipend per lead (€)', type: 'number' },
  { key: 'overhead_per_participant', label: 'Overhead / participant (€)', type: 'number' },
  { key: 'tool_cost_per_user_per_month', label: 'Tool cost / user / month (€)', type: 'number', hint: 'Auto-derived from career track' },
  { key: 'fixed_tool_cost_per_month', label: 'Fixed tool cost / month (€)', type: 'number' },
  { key: 'placement_bonus_per_lead', label: 'Placement bonus / lead (€)', type: 'number' },
  { key: 'no_show_rate', label: 'No-show rate', type: 'percent' },
  { key: 'refund_rate', label: 'Refund rate', type: 'percent' },
]

function InputForm({ defaults, careerTracks, onSubmit }) {
  const [values, setValues] = useState(defaults)

  const handleChange = (key, type, value) => {
    const parsed = type === 'percent' ? parseFloat(value) / 100 : parseFloat(value)
    setValues((prev) => ({ ...prev, [key]: isNaN(parsed) ? 0 : parsed }))
  }

  const handleTrackChange = (e) => {
    setValues((prev) => ({ ...prev, career_track: e.target.value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(values)
  }

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="career_track">Career track</label>
        <select
          id="career_track"
          value={values.career_track}
          onChange={handleTrackChange}
        >
          {careerTracks.map((track) => (
            <option key={track.key} value={track.key}>
              {track.label}
            </option>
          ))}
        </select>
      </div>

      {fields.map(({ key, label, type, hint }) => (
        <div className="form-group" key={key}>
          <label htmlFor={key}>{label}</label>
          <input
            id={key}
            type="number"
            step={type === 'percent' ? '0.1' : 'any'}
            value={type === 'percent' ? (values[key] * 100).toFixed(1) : values[key]}
            onChange={(e) => handleChange(key, type, e.target.value)}
          />
          {hint && <span className="field-hint">{hint}</span>}
        </div>
      ))}
      <button className="submit-btn" type="submit">
        Update Dashboard
      </button>
    </form>
  )
}

export default InputForm
