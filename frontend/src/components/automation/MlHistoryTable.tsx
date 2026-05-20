import { CheckCircle, SkipForward } from 'lucide-react'
import type { MLHistoryItem, SceneName } from '../../types/home'

const SCENE_LABELS: Record<SceneName, string> = {
  day: 'День',
  night: 'Ночь',
  away: 'Никого нет',
  movie: 'Кино',
}

const SCENE_COLORS: Record<SceneName, string> = {
  day:   'bg-amber-900/40 text-amber-400',
  night: 'bg-indigo-900/40 text-indigo-400',
  away:  'bg-gray-700 text-gray-400',
  movie: 'bg-purple-900/40 text-purple-400',
}

function formatTime(isoString: string): string {
  try {
    return new Date(isoString).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '—'
  }
}

interface MlHistoryTableProps {
  items: MLHistoryItem[]
  total: number
  page: number
  onPageChange: (page: number) => void
  pageSize?: number
}

export function MlHistoryTable({ items, total, page, onPageChange, pageSize = 20 }: MlHistoryTableProps) {
  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <div className="overflow-x-auto rounded-xl border border-gray-700">
        <table className="min-w-full divide-y divide-gray-700 text-sm">
          <thead className="bg-gray-900/50">
            <tr>
              {(['Время', 'Сцена', 'Уверенность', 'Статус', 'Причина'] as const).map((h) => (
                <th
                  key={h}
                  className="py-3 px-4 text-left text-xs font-medium uppercase tracking-wider text-gray-400"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50 bg-gray-800">
            {items.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-10 text-center text-sm text-gray-500">
                  История решений пуста
                </td>
              </tr>
            ) : (
              items.map((item) => {
                const sceneCfg = SCENE_COLORS[item.scenario] ?? 'bg-gray-700 text-gray-400'
                return (
                  <tr key={item.id} className="hover:bg-gray-700/30 transition-colors">
                    <td className="py-3 px-4 text-gray-400">{formatTime(item.created_at)}</td>
                    <td className="py-3 px-4">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${sceneCfg}`}>
                        {SCENE_LABELS[item.scenario] ?? item.scenario}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-sm font-medium ${
                            item.confidence >= 0.7 ? 'text-green-400' : item.confidence >= 0.5 ? 'text-amber-400' : 'text-red-400'
                          }`}
                        >
                          {Math.round(item.confidence * 100)}%
                        </span>
                        <div className="h-1.5 w-16 rounded-full bg-gray-700 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${item.confidence >= 0.7 ? 'bg-green-500' : item.confidence >= 0.5 ? 'bg-amber-500' : 'bg-red-500'}`}
                            style={{ width: `${Math.round(item.confidence * 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {item.applied ? (
                        <span className="inline-flex items-center gap-1.5 text-green-400">
                          <CheckCircle aria-hidden="true" size={14} />
                          <span className="text-xs">Применено</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-gray-500">
                          <SkipForward aria-hidden="true" size={14} />
                          <span className="text-xs">Пропущено</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-xs text-gray-500">
                      {item.applied ? 'auto' : 'low conf'}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            Всего {total} решений
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onPageChange(page - 1)}
              disabled={page === 0}
              className="rounded-lg border border-gray-700 px-3 py-1.5 text-sm text-gray-300 transition hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Назад
            </button>
            <span className="px-3 py-1.5 text-sm text-gray-400">
              {page + 1} / {totalPages}
            </span>
            <button
              type="button"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages - 1}
              className="rounded-lg border border-gray-700 px-3 py-1.5 text-sm text-gray-300 transition hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Вперёд
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
