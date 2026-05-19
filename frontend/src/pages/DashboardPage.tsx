import { useEffect, useRef, useState } from 'react'
import {
  PersonStanding, Sofa, Thermometer, Sun, Lightbulb, Lamp, Tv, Activity,
  Wifi, WifiOff,
} from 'lucide-react'
import { devicesApi } from '../api/devicesApi'
import type { Device } from '../api/devicesApi'
import { eventsApi } from '../api/eventsApi'
import type { DeviceEvent } from '../api/eventsApi'
import { mlApi } from '../api/mlApi'
import { useWebSocket } from '../hooks/useWebSocket'

const DEVICE_ICONS: Record<string, React.ElementType> = {
  motion_hall: PersonStanding,
  motion_living: Sofa,
  temperature: Thermometer,
  light_level: Sun,
  ceiling_light: Lightbulb,
  bedside_light: Lamp,
  thermostat: Thermometer,
  tv_on: Tv,
}

const DEVICE_NAMES: Record<string, string> = {
  motion_hall: 'Датчик коридора',
  motion_living: 'Датчик гостиной',
  temperature: 'Температура',
  light_level: 'Освещённость',
  ceiling_light: 'Основной свет',
  bedside_light: 'Ночник',
  thermostat: 'Термостат',
  tv_on: 'Телевизор',
}

const FLOAT_DEVICES = new Set(['temperature', 'light_level', 'thermostat'])

const SCENARIO_COLORS: Record<string, string> = {
  day: 'bg-blue-600',
  night: 'bg-indigo-600',
  away: 'bg-gray-600',
  movie: 'bg-purple-600',
}

const SCENARIO_NAMES: Record<string, string> = {
  day: 'ДЕНЬ',
  night: 'НОЧЬ',
  away: 'НЕТ ДОМА',
  movie: 'КИНО',
}

function formatTime(isoString: string): string {
  const d = new Date(isoString)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function formatStateValue(deviceId: string, value: number): string {
  if (FLOAT_DEVICES.has(deviceId)) {
    if (deviceId === 'light_level') return `${value.toFixed(1)}%`
    return `${value.toFixed(1)}°C`
  }
  return value ? 'ВКЛ' : 'ВЫКЛ'
}

interface MLStatus {
  scenario: string | null
  confidence: number | null
  probabilities: Record<string, number>
  source: string
}

export default function DashboardPage() {
  const { connected, lastMessage } = useWebSocket()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [devices, setDevices] = useState<Record<string, Device>>({})
  const [events, setEvents] = useState<DeviceEvent[]>([])
  const [mlStatus, setMlStatus] = useState<MLStatus>({
    scenario: null,
    confidence: null,
    probabilities: {},
    source: '',
  })
  const [sceneNotification, setSceneNotification] = useState<string | null>(null)
  const notifTimeoutRef = useRef<number | null>(null)

  useEffect(() => {
    const id = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    devicesApi.list().then((res) => {
      const map: Record<string, Device> = {}
      res.data.forEach((d) => { map[d.id] = d })
      setDevices(map)
    }).catch(() => {})

    eventsApi.list(20).then((res) => {
      setEvents(res.data)
    }).catch(() => {})

    mlApi.latestDecision().then((res) => {
      const data = res.data as Record<string, unknown>
      if (data && 'predicted_scenario' in data) {
        setMlStatus({
          scenario: data.predicted_scenario as string | null,
          confidence: data.confidence as number | null,
          probabilities: {},
          source: data.decision_source as string || '',
        })
      }
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!lastMessage) return
    const msg = lastMessage as unknown as Record<string, unknown>
    const type = msg.type as string

    if (type === 'device_update') {
      const deviceId = msg.device_id as string
      const value = msg.value as number
      setDevices((prev) => {
        if (!prev[deviceId]) return prev
        return {
          ...prev,
          [deviceId]: { ...prev[deviceId], state: value, updated_at: new Date().toISOString() },
        }
      })
      const newEvent: DeviceEvent = {
        id: Date.now(),
        device_id: deviceId,
        device_name: DEVICE_NAMES[deviceId] || deviceId,
        new_state: value,
        created_at: new Date().toISOString(),
      }
      setEvents((prev) => [newEvent, ...prev].slice(0, 20))
    }

    if (type === 'ml_decision') {
      setMlStatus({
        scenario: msg.scenario as string | null,
        confidence: msg.confidence as number | null,
        probabilities: (msg.probabilities as Record<string, number>) || {},
        source: msg.source as string || '',
      })
    }

    if (type === 'scene_confirmed') {
      const scene = msg.scene as string
      const sceneName = SCENARIO_NAMES[scene] || scene.toUpperCase()
      setSceneNotification(`Сцена активирована: ${sceneName}`)
      if (notifTimeoutRef.current) clearTimeout(notifTimeoutRef.current)
      notifTimeoutRef.current = window.setTimeout(() => setSceneNotification(null), 3000)
    }
  }, [lastMessage])

  const deviceOrder = [
    'motion_hall', 'motion_living', 'temperature', 'light_level',
    'ceiling_light', 'bedside_light', 'thermostat', 'tv_on',
  ]

  const confidencePct = mlStatus.confidence != null ? Math.round(mlStatus.confidence * 100) : null

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-6">
      {sceneNotification && (
        <div className="fixed top-4 right-4 bg-indigo-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity">
          {sceneNotification}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Дашборд</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-400 text-sm font-mono">
            {currentTime.toLocaleTimeString('ru-RU')}
          </span>
          <div className="flex items-center gap-2">
            {connected ? (
              <Wifi size={14} className="text-green-400" />
            ) : (
              <WifiOff size={14} className="text-red-500" />
            )}
            <span className="text-sm text-gray-400">{connected ? 'Подключено' : 'Отключено'}</span>
          </div>
        </div>
      </div>

      {/* ML Status */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-200">ML Предсказание сцены</h2>
          {mlStatus.source && (
            <span className="text-xs text-gray-500 uppercase tracking-wide">{mlStatus.source}</span>
          )}
        </div>
        <div className="flex items-center gap-4">
          {mlStatus.scenario ? (
            <span className={`px-3 py-1 rounded-full text-sm font-bold ${SCENARIO_COLORS[mlStatus.scenario] || 'bg-gray-600'}`}>
              {SCENARIO_NAMES[mlStatus.scenario] || mlStatus.scenario.toUpperCase()}
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full text-sm font-semibold bg-gray-600 text-gray-300">
              Нет данных
            </span>
          )}
          {confidencePct != null && (
            <div className="flex-1 flex items-center gap-3">
              <div className="flex-1 bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-indigo-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
              <span className="text-sm text-gray-300 w-28 text-right">{confidencePct}% уверенность</span>
            </div>
          )}
        </div>
      </div>

      {/* Device cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {deviceOrder.map((deviceId) => {
          const device = devices[deviceId]
          const Icon = DEVICE_ICONS[deviceId]
          return (
            <div key={deviceId} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                {Icon && <Icon size={20} className="text-indigo-400 shrink-0" />}
                <span className="text-sm font-medium text-gray-300 leading-tight">{DEVICE_NAMES[deviceId]}</span>
              </div>
              {device ? (
                <>
                  <div className="text-xl font-bold">
                    {FLOAT_DEVICES.has(deviceId) ? (
                      <span className="text-indigo-400">{formatStateValue(deviceId, device.state)}</span>
                    ) : (
                      <span className={device.state ? 'text-green-400' : 'text-gray-500'}>
                        {device.state ? 'ВКЛ' : 'ВЫКЛ'}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">{formatTime(device.updated_at)}</div>
                </>
              ) : (
                <div className="text-gray-500 text-sm">Загрузка...</div>
              )}
            </div>
          )
        })}
      </div>

      {/* Event log */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="flex items-center gap-2 mb-3">
          <Activity size={16} className="text-indigo-400" />
          <h2 className="text-lg font-semibold text-gray-200">Журнал событий</h2>
        </div>
        <div className="space-y-1 max-h-60 overflow-y-auto pr-1">
          {events.length === 0 && (
            <p className="text-gray-500 text-sm">Событий пока нет.</p>
          )}
          {events.map((ev) => (
            <div key={ev.id} className="flex items-center gap-3 text-sm py-1.5 border-b border-gray-700/60 last:border-0">
              <span className="text-gray-500 font-mono w-20 shrink-0">{formatTime(ev.created_at)}</span>
              <span className="text-gray-300 flex-1">{ev.device_name || DEVICE_NAMES[ev.device_id] || ev.device_id}</span>
              <span className={`font-semibold ${FLOAT_DEVICES.has(ev.device_id)
                ? 'text-indigo-400'
                : ev.new_state ? 'text-green-400' : 'text-gray-500'}`}>
                {formatStateValue(ev.device_id, ev.new_state)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
