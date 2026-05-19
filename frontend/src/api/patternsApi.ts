import { apiClient } from './client'

export interface SuggestedPattern {
  id: number
  cluster_id: number
  description: string
  feature_summary: string
  status: string
  created_at: string
}

export const patternsApi = {
  list: () => apiClient.get<SuggestedPattern[]>('/patterns'),
  accept: (id: number) => apiClient.post(`/patterns/${id}/accept`),
  reject: (id: number) => apiClient.post(`/patterns/${id}/reject`),
}
