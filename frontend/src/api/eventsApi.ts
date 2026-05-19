import { apiClient } from './client'

export interface DeviceEvent {
  id: number
  device_id: string
  device_name: string
  new_state: number
  created_at: string
}

export const eventsApi = {
  list: (limit = 20) => apiClient.get<DeviceEvent[]>(`/events?limit=${limit}`),
}
