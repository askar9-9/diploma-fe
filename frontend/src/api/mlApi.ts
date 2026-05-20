import { apiClient } from './client'
import type { CurrentScene, FeatureVector, MLHistoryResponse } from '../types/home'

export const mlApi = {
  history: (limit = 20, offset = 0) =>
    apiClient.get<MLHistoryResponse>(`/ml/history?limit=${limit}&offset=${offset}`),

  currentScene: () =>
    apiClient.get<CurrentScene>('/ml/current-scene'),

  featureVector: () =>
    apiClient.get<FeatureVector>('/ml/feature-vector'),
}
