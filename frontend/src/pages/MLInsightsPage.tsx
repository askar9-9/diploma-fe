import { useEffect, useState } from 'react'
import {
  BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line,
} from 'recharts'
import { Brain, Zap, History, Radio } from 'lucide-react'
import { mlApi } from '../api/mlApi'
import type { MLDecision, EnergyForecast } from '../api/mlApi'
import { useWebSocket } from '../hooks/useWebSocket'

const SCENARIO_COLORS: Record<string, string> = {
  day: '#3b82f6',
  night: '#6366f1',
  away: '#6b7280',
  movie: '#8b5cf6',
}

const SCENARIO_BADGE: Record<string, string> = {
  day: 'bg-blue-600',
  night: 'bg-indigo-600',
  away: 'bg-gray-600',
  movie: 'bg-purple-600',
}

const SCENARIO_NAMES: Record<string, string> = {
  day: 'День',
  night: 'Ночь',
  away: 'Нет дома',
  movie: 'Кино',
}

function confidenceBadge(conf: number | null, source?: string): string {
  if (conf == null || source === 'clusterer') return 'bg-gray-600 text-gray-300'
  if (conf >= 0.8) return 'bg-green-700 text-green-200'
  if (conf >= 0.6) return 'bg-yellow-700 text-yellow-200'
  return 'bg-red-700 text-red-200'
}

function formatTime(isoString: string): string {
  const d = new Date(isoString)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const SCENARIO_KEYS = ['day', 'night', 'away', 'movie']

interface ProbabilityEntry { name: string; value: number; fill: string }

export default function MLInsightsPage() {
  const { lastMessage } = useWebSocket()
  const [probData, setProbData] = useState<ProbabilityEntry[]>(
    SCENARIO_KEYS.map((k) => ({ name: k, value: 0, fill: SCENARIO_COLORS[k] }))
  )
  const [liveProbs, setLiveProbs] = useState(false)
  const [decisions, setDecisions] = useState<MLDecision[]>([])
  const [energyForecast, setEnergyForecast] = useState<EnergyForecast | null>(null)
  const [energyLoading, setEnergyLoading] = useState(true)

  useEffect(() => {
    mlApi.decisions(20).then((res) => setDecisions(res.data)).catch(() => {})

    mlApi.latestDecision().then((res) => {
      const data = res.data as Record<string, unknown>
      // probabilities not stored in DB — leave zeros until WebSocket fires
      if (data && 'predicted_scenario' in data) {
        // scenario known but probs not available yet
      }
    }).catch(() => {})

    mlApi.energyForecast().then((res) => {
      setEnergyForecast(res.data)
    }).catch(() => {}).finally(() => setEnergyLoading(false))
  }, [])

  useEffect(() => {
    if (!lastMessage) return
    const msg = lastMessage as unknown as Record<string, unknown>
    if (msg.type === 'ml_decision') {
      const probs = (msg.probabilities as Record<string, number>) || {}
      setProbData(SCENARIO_KEYS.map((k) => ({
        name: k,
        value: probs[k] ?? 0,
        fill: SCENARIO_COLORS[k],
      })))
      setLiveProbs(true)
    }
    if (msg.type === 'ml_decisions_updated') {
      mlApi.decisions(20).then((res) => setDecisions(res.data)).catch(() => {})
    }
  }, [lastMessage])

  // Sort energy forecast by hour 0→23
  const sortedForecast = energyForecast
    ? { ...energyForecast, forecast: [...energyForecast.forecast].sort((a, b) => a.hour - b.hour) }
    : null

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-6">
      <h1 className="text-2xl font-bold">ML Аналитика</h1>

      {/* Scenario Probability Chart */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-indigo-400" />
            <h2 className="text-lg font-semibold text-gray-200">Вероятности сценариев</h2>
          </div>
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${liveProbs ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
            <span className="text-xs text-gray-400">{liveProbs ? 'В реальном времени' : 'Ожидание данных...'}</span>
          </div>
        </div>
        {!liveProbs ? (
          <div className="flex items-center justify-center h-40 text-gray-400 gap-3">
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm">Ожидание ML решений через WebSocket...</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={probData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="name"
                stroke="#9ca3af"
                tick={{ fill: '#d1d5db' }}
                tickFormatter={(v: string) => SCENARIO_NAMES[v] || v}
              />
              <YAxis domain={[0, 1]} stroke="#9ca3af" tick={{ fill: '#d1d5db' }}
                tickFormatter={(v: number) => `${Math.round(v * 100)}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                formatter={(value: number | string | readonly (number | string)[] | undefined) => {
                  const num = typeof value === 'number' ? value : 0
                  return [`${Math.round(num * 100)}%`, 'Вероятность'] as [string, string]
                }}
                labelFormatter={(label: unknown) => SCENARIO_NAMES[label as string] || String(label)}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {probData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Energy Forecast Chart */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <Zap size={18} className="text-yellow-400" />
          <h2 className="text-lg font-semibold text-gray-200">Прогноз энергопотребления (24ч)</h2>
        </div>
        {energyLoading ? (
          <div className="text-gray-400 text-sm flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
            Загрузка...
          </div>
        ) : sortedForecast ? (
          <>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={sortedForecast.forecast} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="hour"
                  stroke="#9ca3af"
                  tick={{ fill: '#d1d5db' }}
                  label={{ value: 'Час', position: 'insideBottom', offset: -2, fill: '#9ca3af' }}
                />
                <YAxis stroke="#9ca3af" tick={{ fill: '#d1d5db' }}
                  label={{ value: 'кВт·ч', angle: -90, position: 'insideLeft', fill: '#9ca3af' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                  formatter={(value: number | string | readonly (number | string)[] | undefined) => {
                    const num = typeof value === 'number' ? value : 0
                    return [`${num.toFixed(3)} кВт·ч`, 'Энергия'] as [string, string]
                  }}
                  labelFormatter={(label: unknown) => `${label}:00`}
                />
                <Line type="monotone" dataKey="kwh" stroke="#6366f1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div className="flex gap-6 mt-3 text-sm text-gray-300">
              <span>Итого: <span className="text-indigo-400 font-semibold">{sortedForecast.total_kwh.toFixed(3)} кВт·ч</span></span>
              <span>Пиковый час: <span className="text-indigo-400 font-semibold">{sortedForecast.peak_hour}:00</span></span>
            </div>
          </>
        ) : (
          <div className="text-gray-500 text-sm">Прогноз энергопотребления недоступен.</div>
        )}
      </div>

      {/* ML Decisions Table */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <History size={18} className="text-indigo-400" />
          <h2 className="text-lg font-semibold text-gray-200">История ML решений</h2>
          <div className="ml-auto flex items-center gap-1.5">
            <Radio size={12} className="text-green-400" />
            <span className="text-xs text-gray-400">Обновляется в реальном времени</span>
          </div>
        </div>
        <div className="overflow-x-auto max-h-72 overflow-y-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-gray-400 border-b border-gray-700 sticky top-0 bg-gray-800">
              <tr>
                <th className="pb-2 pr-4">Время</th>
                <th className="pb-2 pr-4">Час</th>
                <th className="pb-2 pr-4">Сценарий</th>
                <th className="pb-2 pr-4">Уверенность</th>
                <th className="pb-2">Источник</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {decisions.length === 0 && (
                <tr><td colSpan={5} className="py-4 text-gray-500 text-center">Решений пока нет.</td></tr>
              )}
              {decisions.map((d) => (
                <tr key={d.id} className="hover:bg-gray-750">
                  <td className="py-2 pr-4 text-gray-400 font-mono">{formatTime(d.created_at)}</td>
                  <td className="py-2 pr-4 text-gray-300">{d.hour_of_day}:00</td>
                  <td className="py-2 pr-4">
                    {d.predicted_scenario ? (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${SCENARIO_BADGE[d.predicted_scenario] || 'bg-gray-600'}`}>
                        {SCENARIO_NAMES[d.predicted_scenario] || d.predicted_scenario}
                      </span>
                    ) : (
                      <span className="text-gray-500">—</span>
                    )}
                  </td>
                  <td className="py-2 pr-4">
                    {d.decision_source === 'clusterer' ? (
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-600 text-gray-300">N/A</span>
                    ) : d.confidence != null ? (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${confidenceBadge(d.confidence, d.decision_source)}`}>
                        {Math.round(d.confidence * 100)}%
                      </span>
                    ) : (
                      <span className="text-gray-500">—</span>
                    )}
                  </td>
                  <td className="py-2 text-gray-400 text-xs">{d.decision_source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
