import { create } from 'zustand'
import { defaultConfig } from './config'

export const useStore = create((set, get) => ({
  config: defaultConfig,
  result: null,
  summary: null,
  checks: null,
  team: null,
  breakEven: null,
  sensitivity: null,
  loading: false,
  error: null,

  setConfig: (next) => set({ config: next }),

  updateField: (path, value) => {
    const { config } = get()
    const keys = path.split('.')
    const next = structuredClone(config)
    let node = next
    for (let i = 0; i < keys.length - 1; i++) {
      node = node[keys[i]]
    }
    node[keys[keys.length - 1]] = value
    set({ config: next })
  },

  setResult: (result) => set({ result }),
  setSummary: (summary) => set({ summary }),
  setChecks: (checks) => set({ checks }),
  setTeam: (team) => set({ team }),
  setBreakEven: (breakEven) => set({ breakEven }),
  setSensitivity: (sensitivity) => set({ sensitivity }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
