import { create } from 'zustand'
import * as api from './api'

function setPath(obj, path, value) {
  const keys = Array.isArray(path) ? path : path.split('.')
  const next = { ...obj }
  let cursor = next
  for (let i = 0; i < keys.length - 1; i++) {
    cursor[keys[i]] = { ...cursor[keys[i]] }
    cursor = cursor[keys[i]]
  }
  cursor[keys[keys.length - 1]] = value
  return next
}

const useStore = create((set, get) => ({
  config: null,
  result: null,
  careerTracks: [],
  activePanel: 'simulator',
  lastSaved: null,
  isLoading: false,
  error: null,

  setConfig: (config) => set({ config }),
  updateConfig: (path, value) =>
    set((state) => ({ config: setPath(state.config, path, value) })),
  setPanel: (panel) => set({ activePanel: panel }),

  loadDefaults: async () => {
    try {
      const [config, careerTracks] = await Promise.all([
        api.getDefaults(),
        api.getCareerTracks(),
      ])
      set({ config, careerTracks, error: null })
      await get().calculate()
    } catch (err) {
      set({ error: err.message })
    }
  },

  calculate: async () => {
    const { config } = get()
    if (!config) return
    set({ isLoading: true, error: null })
    try {
      const result = await api.calculate(config)
      set({
        result,
        lastSaved: new Date().toISOString(),
        isLoading: false,
      })
    } catch (err) {
      set({ error: err.message, isLoading: false })
    }
  },

  exportCSV: async () => {
    const { config } = get()
    if (!config) return
    const blob = await api.exportCSV(config)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'careerleap_export.csv'
    a.click()
    window.URL.revokeObjectURL(url)
  },
}))

export default useStore
