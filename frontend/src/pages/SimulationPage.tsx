import { useEffect, useState } from 'react'
import { Timer, Play, Square, Clock, Sunrise } from 'lucide-react'
import { simulationApi } from '../api/simulationApi'
import type { SimulationStatus } from '../api/simulationApi'
import { useWebSocket } from '../hooks/useWebSocket'

const SPEED_OPTIONS = [10, 30, 60, 120]

const DEFAULT_STATUS: SimulationStatus = {
  running: false,
  simulated_hour: 0,
  simulated_minute: 0,
  speed: 30,
}

interface DayPhase {
  label: string
  start: number
  end: number
  scene: string
  color: string
}

const DAY_PHASES: DayPhase[] = [
  { label: 'Ночь', start: 0, end: 6, scene: 'Ночь', color: 'bg-indigo-900' },
  { label: 'Утро', start: 6, end: 9, scene: 'День', color: 'bg-blue-700' },
  { label: 'День', start: 9, end: 17, scene: 'День', color: 'bg-blue-500' },
  { label: 'Вечер', start: 17, end: 22, scene: 'Кино', color: 'bg-purple-700' },
  { label: 'Поздняя ночь', start: 22, end: 24, scene: 'Ночь', color: 'bg-indigo-900' },
]

function formatSimulatedTime(hour: number, minute: number): string {
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
}

function parseSimulatedTime(time: string): { hour: number; minute: number } | null {
  const match = /^(\d{2}):(\d{2})$/.exec(time.trim())
  if (!match) return null
  const hour = Number(match[1])
  const minute = Number(match[2])
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null
  return { hour, minute }
}

function isSupportedSpeed(speed: number): boolean {
  return SPEED_OPTIONS.includes(speed)
}

function getPhaseLabel(hour: number): string {
  if (hour < 6) return 'Ночь 🌙'
  if (hour < 9) return 'Утро ☀️'
  if (hour < 17) return 'День 🏢'
  if (hour < 22) return 'Вечер 🌆'
  return 'Поздняя ночь 🎬'
}

function getProgressPercent(hour: number, minute: number): number {
  return ((hour * 60 + minute) / (24 * 60)) * 100
}

export default function SimulationPage() {
  const { lastMessage } = useWebSocket()
  const [status, setStatus] = useState<SimulationStatus>(DEFAULT_STATUS)
  const [selectedSpeed, setSelectedSpeed] = useState(30)
  const [commandLoading, setCommandLoading] = useState<'start' | 'stop' | null>(null)
  const [statusLoading, setStatusLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    simulationApi.status().then((res) => {
      if (!active) return
      setStatus(res.data)
      if (isSupportedSpeed(res.data.speed)) setSelectedSpeed(res.data.speed)
      setError(null)
    }).catch(() => {
      if (!active) return
      setError('Не удалось загрузить статус симуляции.')
    }).finally(() => {
      if (active) setStatusLoading(false)
    })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!lastMessage) return
    const message = lastMessage as unknown as Record<string, unknown>
    if (message.type !== 'simulation_status' || typeof message.time !== 'string') return
    const parsedTime = parseSimulatedTime(message.time)
    if (!parsedTime) return
    setStatus((prev) => ({
      ...prev,
      simulated_hour: parsedTime.hour,
      simulated_minute: parsedTime.minute,
      running: typeof message.running === 'boolean' ? message.running : prev.running,
      speed: typeof message.speed === 'number' ? message.speed : prev.speed,
    }))
  }, [lastMessage])

  useEffect(() => {
    if (!status.running) return
    const intervalId = window.setInterval(() => {
      simulationApi.status().then((res) => {
        setStatus(res.data)
        if (isSupportedSpeed(res.data.speed)) setSelectedSpeed(res.data.speed)
        setError(null)
      }).catch(() => {})
    }, 3000)
    return () => window.clearInterval(intervalId)
  }, [status.running])

  const handleToggleSimulation = async () => {
    const action = status.running ? 'stop' : 'start'
    setCommandLoading(action)
    setError(null)
    try {
      const response = action === 'start'
        ? await simulationApi.start(selectedSpeed)
        : await simulationApi.stop()
      setStatus(response.data)
      if (isSupportedSpeed(response.data.speed)) setSelectedSpeed(response.data.speed)
    } catch {
      setError(`Не удалось ${action === 'start' ? 'запустить' : 'остановить'} симуляцию.`)
    } finally {
      setCommandLoading(null)
    }
  }

  const simulatedTime = formatSimulatedTime(status.simulated_hour, status.simulated_minute)
  const phaseLabel = getPhaseLabel(status.simulated_hour)
  const progressPercent = getProgressPercent(status.simulated_hour, status.simulated_minute)
  const isBusy = statusLoading || commandLoading !== null

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <Timer size={22} className="text-indigo-400" />
          <div>
            <h1 className="text-2xl font-bold">Симуляция</h1>
            <p className="text-sm text-gray-400">Управление симулированным суточным циклом HomeIQ.</p>
          </div>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-800 px-4 py-3 text-right">
          <div className="flex items-center gap-1.5 justify-end mb-0.5">
            <Clock size={12} className="text-gray-400" />
            <span className="text-xs uppercase tracking-[0.15em] text-gray-400">Виртуальное время</span>
          </div>
          <div className="font-mono text-3xl font-bold text-white">{simulatedTime}</div>
        </div>
      </div>

      <section className="rounded-2xl border border-gray-700 bg-gray-800 p-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1 space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Управление</h2>
              <p className="text-sm text-gray-400">Выберите скорость и запустите симулятор.</p>
            </div>

            <div>
              <div className="mb-3 text-sm font-medium text-gray-300">Скорость симуляции</div>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {SPEED_OPTIONS.map((speed) => (
                  <label
                    key={speed}
                    className={`rounded-xl border px-4 py-3 transition-colors ${
                      selectedSpeed === speed
                        ? 'border-indigo-500 bg-indigo-600/20 text-white'
                        : 'border-gray-700 bg-gray-900 text-gray-300'
                    } ${status.running || isBusy ? 'cursor-not-allowed opacity-60' : 'cursor-pointer hover:border-indigo-400'}`}
                  >
                    <input
                      type="radio"
                      name="simulation-speed"
                      value={speed}
                      checked={selectedSpeed === speed}
                      onChange={() => setSelectedSpeed(speed)}
                      disabled={status.running || isBusy}
                      className="sr-only"
                    />
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full border-2 flex items-center justify-center ${
                        selectedSpeed === speed ? 'border-indigo-400' : 'border-gray-500'
                      }`}>
                        {selectedSpeed === speed && <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />}
                      </div>
                      <span className="text-lg font-semibold">{speed}x</span>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">{speed} мин / сек</div>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="w-full max-w-md space-y-4 rounded-2xl border border-gray-700 bg-gray-900 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`h-3 w-3 rounded-full ${status.running ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
                <span className="text-sm font-medium text-gray-200">
                  {status.running ? 'Запущена' : 'Остановлена'}
                </span>
              </div>
              <span className="text-sm text-gray-400">
                {status.running ? `Текущая скорость: ${status.speed}x` : `Выбранная скорость: ${selectedSpeed}x`}
              </span>
            </div>

            <button
              onClick={handleToggleSimulation}
              disabled={isBusy}
              className={`flex w-full items-center justify-center gap-2 rounded-xl px-5 py-4 text-lg font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                status.running ? 'bg-red-600 hover:bg-red-500' : 'bg-green-600 hover:bg-green-500'
              }`}
            >
              {commandLoading ? (
                <>
                  <span className="inline-block h-5 w-5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  {commandLoading === 'start' ? 'Запуск...' : 'Остановка...'}
                </>
              ) : status.running ? (
                <>
                  <Square size={20} />
                  Остановить симуляцию
                </>
              ) : (
                <>
                  <Play size={20} />
                  Запустить симуляцию
                </>
              )}
            </button>

            {statusLoading && (
              <p className="text-sm text-gray-400">Загрузка статуса...</p>
            )}
            {error && (
              <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                {error}
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Day Profile Preview — always visible */}
      <section className="rounded-2xl border border-gray-700 bg-gray-800 p-6 space-y-5">
        <div className="flex items-center gap-2">
          <Sunrise size={18} className="text-yellow-400" />
          <h2 className="text-lg font-semibold text-white">Профиль дня</h2>
          <span className="text-xs text-gray-500 ml-1">— распределение сцен по 24 часам</span>
        </div>

        {/* Timeline visual */}
        <div className="flex rounded-xl overflow-hidden h-10">
          {DAY_PHASES.map((phase) => {
            const widthPct = ((phase.end - phase.start) / 24) * 100
            const currentHour = status.simulated_hour
            const isActive = currentHour >= phase.start && currentHour < phase.end
            return (
              <div
                key={phase.label}
                className={`${phase.color} flex items-center justify-center text-xs font-medium transition-all ${
                  isActive ? 'ring-2 ring-white/60 ring-inset' : 'opacity-70'
                }`}
                style={{ width: `${widthPct}%` }}
                title={`${phase.label}: ${phase.start}:00–${phase.end}:00`}
              >
                <span className="truncate px-1 text-white/90">{phase.label}</span>
              </div>
            )
          })}
        </div>
        <div className="flex justify-between text-xs font-mono text-gray-500">
          <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span>
        </div>

        {/* Phase table */}
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 border-b border-gray-700">
              <th className="text-left pb-2 font-medium">Фаза</th>
              <th className="text-left pb-2 font-medium">Период</th>
              <th className="text-left pb-2 font-medium">Сцена</th>
              <th className="text-left pb-2 font-medium">Длительность</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {DAY_PHASES.map((phase) => {
              const currentHour = status.simulated_hour
              const isActive = currentHour >= phase.start && currentHour < phase.end
              return (
                <tr key={phase.label} className={isActive ? 'bg-indigo-900/20' : ''}>
                  <td className="py-2 pr-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-2.5 h-2.5 rounded-sm ${phase.color}`} />
                      <span className={isActive ? 'text-white font-semibold' : 'text-gray-300'}>{phase.label}</span>
                      {isActive && status.running && (
                        <span className="text-xs text-green-400 font-semibold">← сейчас</span>
                      )}
                    </div>
                  </td>
                  <td className="py-2 pr-4 font-mono text-gray-400">
                    {String(phase.start).padStart(2, '0')}:00 – {String(phase.end).padStart(2, '0')}:00
                  </td>
                  <td className="py-2 pr-4 text-indigo-300">{phase.scene}</td>
                  <td className="py-2 text-gray-500">{phase.end - phase.start} ч</td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {status.running && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">{phaseLabel}</span>
              <span className="text-gray-300 font-mono">{simulatedTime}</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-gray-700">
              <div
                className="h-full rounded-full bg-indigo-600 transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-xs font-mono text-gray-500">
              <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>23:59</span>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
