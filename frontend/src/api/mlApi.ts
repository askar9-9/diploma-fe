import { apiClient } from './client'

export interface MLDecision {
  id: number
  hour_of_day: number
  weekday: number
  motion_hall: number
  motion_living: number
  temperature: number
  light_level: number
  tv_on: number
  minutes_idle: number
  predicted_scenario: string | null
  confidence: number | null
  decision_source: string
  created_at: string
}

export interface EnergyForecast {
  current_hour: number
  weekday: number
  forecast: Array<{ hour: number; kwh: number; scenario: string }>
  total_kwh: number
  peak_hour: number
}

export interface AnomalyResult {
  anomaly: boolean
  score: number
  reason: string
}

export const mlApi = {
  decisions: (limit = 50) => apiClient.get<MLDecision[]>(`/ml-decisions?limit=${limit}`),
  latestDecision: () => apiClient.get<MLDecision | Record<string, never>>('/ml-decisions/latest'),
  energyForecast: () => apiClient.get<EnergyForecast>('/energy/forecast'),
}
