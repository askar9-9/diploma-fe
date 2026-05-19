import { apiClient } from './client'

export interface Scenario {
  id: string
  display_name: string
  commands: Record<string, number>
  is_custom: boolean
  created_at: string
}

export const scenariosApi = {
  list: () => apiClient.get<Scenario[]>('/scenarios'),
  activate: (id: string) => apiClient.post(`/scenarios/${id}/activate`),
}
