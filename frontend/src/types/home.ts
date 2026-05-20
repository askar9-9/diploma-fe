export type EntityDomain = 'binary_sensor' | 'sensor' | 'switch' | 'light' | 'climate' | string
export type RoomId = 'hallway' | 'living' | 'kitchen' | 'bedroom' | 'bathroom' | 'outdoor' | 'utility' | string
export type SceneName = 'day' | 'night' | 'away' | 'movie'

export interface Entity {
  entity_id: string
  name: string
  model: string
  domain: EntityDomain
  room: RoomId
  room_ru: string
  state: string
  attributes: Record<string, unknown>
  doc_url: string
  power_kw: number
  updated_at: string
}

export interface CreateEntityRequest {
  entity_id: string
  name: string
  model: string
  domain: EntityDomain
  room: RoomId
  doc_url: string
  power_kw?: number
}

export interface EntityCommandRequest {
  state: string
}

export interface Area {
  id: string
  name_ru: string
  entities: string[]
}

export interface HemsForecast {
  load_forecast: number[]
  solar_forecast: number[]
  hours: number[]
}

export interface HemsStatus {
  current_hour: number
  tariff_zone: 'day' | 'night' | string
  tariff_price: number
  optimizer_action: 'charge' | 'discharge' | 'idle' | string
  recommendation: string
  battery_soc?: number
}

export interface EnergyHistoryDay {
  date: string
  total_kwh: number
}

export interface EnergyHistory {
  days: EnergyHistoryDay[]
}

export interface FeatureVector {
  hour_of_day: number
  weekday: number
  motion_hall: number
  motion_living: number
  temperature: number
  light_level: number
  tv_on: number
  minutes_idle: number
}

export interface MLHistoryItem {
  id: number
  scenario: SceneName
  confidence: number
  probabilities: Record<SceneName, number>
  applied: boolean
  feature_vector: FeatureVector
  created_at: string
}

export interface MLHistoryResponse {
  items: MLHistoryItem[]
  total: number
}

export interface CurrentScene {
  scene: SceneName | null
  confidence: number | null
  last_decision_at: string | null
}

// WebSocket message types
export interface WsStateChangedMessage {
  type: 'state_changed'
  entity_id: string
  state: string
  attributes: Record<string, unknown>
}

export interface WsSceneChangedMessage {
  type: 'scene_changed'
  scene: SceneName
  confidence: number
  triggered_by: 'auto' | 'manual'
}

export interface WsMlDecisionMessage {
  type: 'ml_decision'
  scenario: SceneName
  confidence: number
  probabilities: Record<SceneName, number>
  applied: boolean
  feature_vector: FeatureVector
}

export type WsMessage = WsStateChangedMessage | WsSceneChangedMessage | WsMlDecisionMessage
