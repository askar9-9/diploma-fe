import { apiClient } from './client'

export interface Device {
  id: string
  name: string
  device_type: string  // 'binary' | 'float'
  state: number
  updated_at: string
}

export const devicesApi = {
  list: () => apiClient.get<Device[]>('/devices'),
  command: (deviceId: string, value: number) =>
    apiClient.post(`/devices/${deviceId}/command`, { value }),
}
