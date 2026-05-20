import { apiClient } from './client'
import type { CreateEntityRequest, Entity, EntityCommandRequest } from '../types/home'

export const entitiesApi = {
  list: () => apiClient.get<Entity[]>('/entities'),
  create: (payload: CreateEntityRequest) => apiClient.post<Entity>('/entities', payload),
  delete: (entityId: string) => apiClient.delete(`/entities/${encodeURIComponent(entityId)}`),
  command: (entityId: string, payload: EntityCommandRequest) =>
    apiClient.post(`/entities/${encodeURIComponent(entityId)}/command`, payload),
}
