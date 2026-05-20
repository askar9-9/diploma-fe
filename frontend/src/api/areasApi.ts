import { apiClient } from './client'
import type { Area } from '../types/home'

export const areasApi = {
  list: () => apiClient.get<Area[]>('/areas'),
}
