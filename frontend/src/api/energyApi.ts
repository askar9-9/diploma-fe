import { apiClient } from './client'
import type { EnergyHistory, HemsForecast, HemsStatus } from '../types/home'

export const energyApi = {
  history: () => apiClient.get<EnergyHistory>('/energy/history'),
  forecast: () => apiClient.get<HemsForecast>('/hems/forecast'),
  status: () => apiClient.get<HemsStatus>('/hems/status'),
}
