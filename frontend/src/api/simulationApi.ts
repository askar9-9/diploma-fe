import { apiClient } from './client'

export interface SimulationStatus {
  running: boolean
  simulated_hour: number
  simulated_minute: number
  speed: number
}

export const simulationApi = {
  status: () => apiClient.get<SimulationStatus>('/simulation/status'),
  start: (speed: number) =>
    apiClient.post<SimulationStatus>('/simulation/start', { speed }),
  stop: () => apiClient.post<SimulationStatus>('/simulation/stop'),
}
