import { apiClient } from './client'
import type { SceneName } from '../types/home'

export const scenesApi = {
  activate: (scene: SceneName) =>
    apiClient.post<{ status: string; scene: SceneName }>('/scenes/activate', { scene }),
}
