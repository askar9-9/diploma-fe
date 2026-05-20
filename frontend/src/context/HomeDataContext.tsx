import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { areasApi } from '../api/areasApi'
import { entitiesApi } from '../api/entitiesApi'
import { useWebSocketContext } from './WebSocketContext'
import type {
  Area,
  CreateEntityRequest,
  CurrentScene,
  Entity,
  EntityCommandRequest,
  SceneName,
  WsMlDecisionMessage,
  WsSceneChangedMessage,
  WsStateChangedMessage,
} from '../types/home'

interface HomeDataContextValue {
  areas: Area[]
  createEntity: (payload: CreateEntityRequest) => Promise<void>
  deleteEntity: (entityId: string) => Promise<void>
  entities: Entity[]
  entitiesById: Record<string, Entity>
  error: string | null
  loading: boolean
  refreshHomeData: () => Promise<void>
  sendEntityCommand: (entityId: string, payload: EntityCommandRequest) => Promise<void>
  currentScene: CurrentScene
  lastMlDecision: WsMlDecisionMessage | null
}

const HomeDataContext = createContext<HomeDataContextValue | null>(null)

const BATCH_DELAY_MS = 100

export function HomeDataProvider({ children }: { children: ReactNode }) {
  const { lastMessage } = useWebSocketContext()
  const [areas, setAreas] = useState<Area[]>([])
  const [entities, setEntities] = useState<Entity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentScene, setCurrentScene] = useState<CurrentScene>({
    scene: null,
    confidence: null,
    last_decision_at: null,
  })
  const [lastMlDecision, setLastMlDecision] = useState<WsMlDecisionMessage | null>(null)

  const pendingUpdates = useRef<Map<string, WsStateChangedMessage>>(new Map())
  const batchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  async function refreshHomeData() {
    setLoading(true)
    const [entitiesResult, areasResult] = await Promise.allSettled([
      entitiesApi.list(),
      areasApi.list(),
    ])

    if (entitiesResult.status === 'fulfilled') {
      setEntities(entitiesResult.value.data)
    }

    if (areasResult.status === 'fulfilled') {
      setAreas(areasResult.value.data)
    }

    setError(
      entitiesResult.status === 'rejected' || areasResult.status === 'rejected'
        ? 'Не удалось загрузить данные умного дома.'
        : null,
    )
    setLoading(false)
  }

  useEffect(() => {
    void refreshHomeData()
  }, [])

  const flushUpdates = useCallback(() => {
    if (pendingUpdates.current.size === 0) return
    const updates = new Map(pendingUpdates.current)
    pendingUpdates.current.clear()

    setEntities((currentEntities) =>
      currentEntities.map((entity) => {
        const msg = updates.get(entity.entity_id)
        if (!msg) return entity
        return {
          ...entity,
          state: msg.state,
          attributes: { ...entity.attributes, ...msg.attributes },
          updated_at: new Date().toISOString(),
        }
      }),
    )
  }, [])

  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'state_changed') {
      const msg = lastMessage as WsStateChangedMessage
      pendingUpdates.current.set(msg.entity_id, msg)

      if (batchTimer.current) clearTimeout(batchTimer.current)
      batchTimer.current = setTimeout(flushUpdates, BATCH_DELAY_MS)
      return
    }

    if (lastMessage.type === 'scene_changed') {
      const msg = lastMessage as unknown as WsSceneChangedMessage
      setCurrentScene({
        scene: msg.scene as SceneName,
        confidence: msg.confidence,
        last_decision_at: new Date().toISOString(),
      })
      return
    }

    if (lastMessage.type === 'ml_decision') {
      setLastMlDecision(lastMessage as unknown as WsMlDecisionMessage)
    }
  }, [lastMessage, flushUpdates])

  useEffect(() => {
    return () => {
      if (batchTimer.current) clearTimeout(batchTimer.current)
    }
  }, [])

  async function createEntity(payload: CreateEntityRequest) {
    await entitiesApi.create(payload)
    await refreshHomeData()
  }

  async function deleteEntity(entityId: string) {
    await entitiesApi.delete(entityId)
    setEntities((currentEntities) => currentEntities.filter((e) => e.entity_id !== entityId))
  }

  async function sendEntityCommand(entityId: string, payload: EntityCommandRequest) {
    await entitiesApi.command(entityId, payload)
    setEntities((currentEntities) =>
      currentEntities.map((entity) =>
        entity.entity_id === entityId
          ? { ...entity, state: payload.state, updated_at: new Date().toISOString() }
          : entity,
      ),
    )
  }

  const entitiesById = entities.reduce<Record<string, Entity>>((acc, entity) => {
    acc[entity.entity_id] = entity
    return acc
  }, {})

  return (
    <HomeDataContext.Provider
      value={{
        areas,
        createEntity,
        deleteEntity,
        entities,
        entitiesById,
        error,
        loading,
        refreshHomeData,
        sendEntityCommand,
        currentScene,
        lastMlDecision,
      }}
    >
      {children}
    </HomeDataContext.Provider>
  )
}

export function useHomeData() {
  const context = useContext(HomeDataContext)
  if (!context) throw new Error('useHomeData must be used within HomeDataProvider')
  return context
}
