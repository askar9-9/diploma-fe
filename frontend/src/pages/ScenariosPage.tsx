import { useEffect, useRef, useState } from 'react'
import { Sun, Moon, Home, Film, CheckCircle2 } from 'lucide-react'
import { scenariosApi } from '../api/scenariosApi'
import type { Scenario } from '../api/scenariosApi'
import { useWebSocket } from '../hooks/useWebSocket'

const SCENARIO_DESCRIPTIONS: Record<string, string> = {
  day: 'Яркое освещение, комфортная температура для дневных активностей.',
  night: 'Приглушённый ночник, пониженная температура для сна.',
  away: 'Весь свет выключен, минимальный обогрев для экономии энергии.',
  movie: 'Приглушённый свет, телевизор включён, комфортная температура.',
}

const SCENARIO_ICONS: Record<string, React.ElementType> = {
  day: Sun,
  night: Moon,
  away: Home,
  movie: Film,
}

const SCENARIO_DISPLAY: Record<string, string> = {
  day: 'День',
  night: 'Ночь',
  away: 'Никого дома',
  movie: 'Кино',
}

const SCENARIO_COLORS: Record<string, string> = {
  day: 'border-blue-500 bg-blue-900/20',
  night: 'border-indigo-500 bg-indigo-900/20',
  away: 'border-gray-500 bg-gray-700/20',
  movie: 'border-purple-500 bg-purple-900/20',
}

const SCENARIO_BTN: Record<string, string> = {
  day: 'bg-blue-600 hover:bg-blue-500',
  night: 'bg-indigo-600 hover:bg-indigo-500',
  away: 'bg-gray-600 hover:bg-gray-500',
  movie: 'bg-purple-600 hover:bg-purple-500',
}

const DEVICE_LABELS: Record<string, string> = {
  ceiling_light: 'Основной свет',
  bedside_light: 'Ночник',
  light_level: 'Освещённость',
  thermostat: 'Термостат',
  tv_on: 'Телевизор',
}

function formatCommandValue(key: string, value: number): string {
  if (key === 'thermostat') return `${value}°C`
  if (key === 'light_level') return `${value}%`
  return value ? 'ВКЛ' : 'ВЫКЛ'
}

export default function ScenariosPage() {
  const { lastMessage } = useWebSocket()
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [activeScene, setActiveScene] = useState<string | null>(null)
  const [loading, setLoading] = useState<Record<string, boolean>>({})
  const [toast, setToast] = useState<string | null>(null)
  const toastTimeoutRef = useRef<number | null>(null)

  useEffect(() => {
    scenariosApi.list().then((res) => setScenarios(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    if (!lastMessage) return
    const msg = lastMessage as unknown as Record<string, unknown>
    if (msg.type === 'scene_confirmed') {
      setActiveScene(msg.scene as string)
    }
  }, [lastMessage])

  const showToast = (message: string) => {
    setToast(message)
    if (toastTimeoutRef.current) clearTimeout(toastTimeoutRef.current)
    toastTimeoutRef.current = window.setTimeout(() => setToast(null), 3000)
  }

  const handleActivate = async (id: string) => {
    setLoading((prev) => ({ ...prev, [id]: true }))
    try {
      await scenariosApi.activate(id)
      setActiveScene(id)
      const displayName = SCENARIO_DISPLAY[id] || id
      showToast(`Сцена "${displayName}" активирована!`)
    } catch {
      showToast('Не удалось активировать сцену.')
    } finally {
      setLoading((prev) => ({ ...prev, [id]: false }))
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-6">
      {toast && (
        <div className="fixed top-4 right-4 bg-indigo-600 text-white px-4 py-2 rounded-lg shadow-lg z-50">
          {toast}
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold">Сценарии</h1>
        <p className="text-gray-400 text-sm mt-1">Активируйте готовый сценарий для управления всеми устройствами сразу.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {scenarios.length === 0 && (
          <p className="text-gray-500 col-span-2">Загрузка сценариев...</p>
        )}
        {scenarios.map((scenario) => {
          const isActive = activeScene === scenario.id
          const isLoading = loading[scenario.id] || false
          const colorClass = SCENARIO_COLORS[scenario.id] || 'border-gray-600 bg-gray-700/20'
          const btnClass = SCENARIO_BTN[scenario.id] || 'bg-gray-600 hover:bg-gray-500'
          const Icon = SCENARIO_ICONS[scenario.id] || Home
          const displayName = SCENARIO_DISPLAY[scenario.id] || scenario.display_name || scenario.id

          return (
            <div
              key={scenario.id}
              className={`bg-gray-800 rounded-xl p-5 border-2 transition-colors ${isActive ? colorClass : 'border-gray-700'}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isActive ? 'bg-indigo-600' : 'bg-gray-700'}`}>
                    <Icon size={20} className={isActive ? 'text-white' : 'text-gray-300'} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold">{displayName}</h3>
                      {isActive && (
                        <span className="inline-flex items-center gap-1 text-xs bg-green-700 text-green-200 px-2 py-0.5 rounded-full font-semibold">
                          <CheckCircle2 size={10} />
                          Активна
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400">{SCENARIO_DESCRIPTIONS[scenario.id] || ''}</p>
                  </div>
                </div>
              </div>

              <div className="mb-4 space-y-1">
                {Object.entries(scenario.commands).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">{DEVICE_LABELS[key] || key}</span>
                    <span className={`font-medium ${value ? 'text-green-400' : 'text-gray-500'}`}>
                      {formatCommandValue(key, value as number)}
                    </span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleActivate(scenario.id)}
                disabled={isLoading || isActive}
                className={`w-full py-2 rounded-lg text-white font-semibold transition-colors disabled:opacity-50 ${btnClass}`}
              >
                {isLoading ? (
                  <span className="inline-flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Активация...
                  </span>
                ) : isActive ? 'Активна сейчас' : 'Активировать'}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
