import { Clock, Zap } from 'lucide-react'
import type { CurrentScene, SceneName } from '../../types/home'

const SCENE_CONFIG: Record<SceneName, { label: string; color: string; bg: string }> = {
  day:   { label: 'День',      color: 'text-amber-400',  bg: 'bg-amber-900/40' },
  night: { label: 'Ночь',      color: 'text-indigo-400', bg: 'bg-indigo-900/40' },
  away:  { label: 'Никого нет', color: 'text-gray-400',   bg: 'bg-gray-700/60' },
  movie: { label: 'Кино',      color: 'text-purple-400', bg: 'bg-purple-900/40' },
}

function formatRelativeTime(isoString: string | null): string {
  if (!isoString) return '—'
  const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000)
  if (diff < 60) return `${diff} сек назад`
  if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`
  return `${Math.floor(diff / 3600)} ч назад`
}

interface CurrentSceneBadgeProps {
  currentScene: CurrentScene
  compact?: boolean
}

export function CurrentSceneBadge({ currentScene, compact = false }: CurrentSceneBadgeProps) {
  const { scene, confidence, last_decision_at } = currentScene
  const cfg = scene ? SCENE_CONFIG[scene] : null

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Zap aria-hidden="true" size={14} className="text-sky-400 shrink-0" />
        {cfg ? (
          <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${cfg.bg} ${cfg.color}`}>
            {cfg.label}
          </span>
        ) : (
          <span className="text-xs text-gray-500">Нет данных</span>
        )}
        {confidence != null && (
          <span className="text-xs text-gray-400">{Math.round(confidence * 100)}%</span>
        )}
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-800 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Zap aria-hidden="true" size={16} className="text-sky-400" />
        <h3 className="text-sm font-semibold text-white">Активная сцена</h3>
      </div>

      {cfg ? (
        <>
          <div className="flex items-center justify-between mb-3">
            <span className={`rounded-xl px-3 py-1.5 text-sm font-bold ${cfg.bg} ${cfg.color}`}>
              {cfg.label}
            </span>
            {confidence != null && (
              <span className="text-lg font-bold text-white">
                {Math.round(confidence * 100)}%
              </span>
            )}
          </div>

          {confidence != null && (
            <div className="mb-3">
              <div className="h-2 rounded-full bg-gray-700 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    confidence >= 0.7 ? 'bg-green-500' : confidence >= 0.5 ? 'bg-amber-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.round(confidence * 100)}%` }}
                  aria-label={`Уверенность: ${Math.round(confidence * 100)}%`}
                />
              </div>
            </div>
          )}

          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <Clock aria-hidden="true" size={11} />
            <span>Последнее решение: {formatRelativeTime(last_decision_at)}</span>
          </div>
        </>
      ) : (
        <p className="text-sm text-gray-500">ML не приняла решение ещё.</p>
      )}
    </div>
  )
}
