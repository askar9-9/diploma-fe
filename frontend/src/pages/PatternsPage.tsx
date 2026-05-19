import { useEffect, useState } from 'react'
import { Search, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react'
import { patternsApi } from '../api/patternsApi'
import type { SuggestedPattern } from '../api/patternsApi'

type PatternRecord = SuggestedPattern & { discovered_at?: string }
type PatternAction = 'accept' | 'reject'

const STATUS_STYLES: Record<string, string> = {
  pending: 'bg-yellow-700 text-yellow-200',
  accepted: 'bg-green-700 text-green-200',
  rejected: 'bg-red-700 text-red-200',
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'ОЖИДАЕТ',
  accepted: 'ПРИНЯТ',
  rejected: 'ОТКЛОНЁН',
}

function normalizeStatus(status: string): 'pending' | 'accepted' | 'rejected' {
  if (status === 'accepted' || status === 'rejected') return status
  return 'pending'
}

function formatTimestamp(pattern: PatternRecord): string {
  const timestamp = pattern.created_at || pattern.discovered_at
  if (!timestamp) return 'Неизвестно'
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return timestamp
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export default function PatternsPage() {
  const [patterns, setPatterns] = useState<PatternRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [actionLoading, setActionLoading] = useState<Record<number, PatternAction | null>>({})

  const fetchPatterns = (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    else setLoading(true)

    patternsApi.list()
      .then((res) => setPatterns(res.data as PatternRecord[]))
      .catch(() => setPatterns([]))
      .finally(() => {
        setLoading(false)
        setRefreshing(false)
      })
  }

  useEffect(() => {
    fetchPatterns()
  }, [])

  const handleReview = async (id: number, action: PatternAction) => {
    setActionLoading((prev) => ({ ...prev, [id]: action }))
    try {
      if (action === 'accept') {
        await patternsApi.accept(id)
      } else {
        await patternsApi.reject(id)
      }
      setPatterns((prev) => prev.map((pattern) =>
        pattern.id === id
          ? { ...pattern, status: action === 'accept' ? 'accepted' : 'rejected' }
          : pattern
      ))
    } catch {
      // leave stable on error
    } finally {
      setActionLoading((prev) => ({ ...prev, [id]: null }))
    }
  }

  const pendingCount = patterns.filter((p) => normalizeStatus(p.status) === 'pending').length
  const acceptedCount = patterns.filter((p) => normalizeStatus(p.status) === 'accepted').length
  const rejectedCount = patterns.filter((p) => normalizeStatus(p.status) === 'rejected').length
  const hasStats = pendingCount > 0 || acceptedCount > 0 || rejectedCount > 0

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Обзор паттернов</h1>
          <p className="text-gray-400 text-sm mt-1">Обнаружены K-Means кластеризацией</p>
        </div>
        <button
          onClick={() => fetchPatterns(true)}
          disabled={refreshing || loading}
          className="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700 text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
          Обновить
        </button>
      </div>

      <div className="bg-indigo-900/40 rounded-xl p-5 border border-indigo-600/50">
        <p className="text-sm text-indigo-100">
          ML-сервис непрерывно кластеризует показания датчиков для обнаружения новых поведенческих
          паттернов. Принимайте паттерны для улучшения классификатора.
        </p>
      </div>

      {hasStats && (
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-1.5">
              <Clock size={14} className="text-yellow-400" />
              <span className="text-yellow-300 font-semibold">{pendingCount} ожидают</span>
            </span>
            <span className="text-gray-600">·</span>
            <span className="flex items-center gap-1.5">
              <CheckCircle size={14} className="text-green-400" />
              <span className="text-green-300 font-semibold">{acceptedCount} принято</span>
            </span>
            <span className="text-gray-600">·</span>
            <span className="flex items-center gap-1.5">
              <XCircle size={14} className="text-red-400" />
              <span className="text-red-300 font-semibold">{rejectedCount} отклонено</span>
            </span>
          </div>
        </div>
      )}

      {loading ? (
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
          <div className="inline-flex items-center gap-2 text-sm text-gray-400">
            <span className="inline-block w-4 h-4 rounded-full border-2 border-gray-400 border-t-transparent animate-spin" />
            Загрузка паттернов...
          </div>
        </div>
      ) : patterns.length === 0 ? (
        <div className="bg-gray-800 rounded-xl p-8 border border-gray-700 text-center">
          <div className="flex justify-center mb-4">
            <Search size={48} className="text-gray-600" />
          </div>
          <h2 className="text-lg font-semibold text-gray-200 mb-2">Паттерны ещё не обнаружены</h2>
          <p className="text-sm text-gray-400 mb-2">
            Паттерны появятся здесь после накопления ML-сервисом достаточного количества показаний датчиков.
          </p>
          <p className="text-sm text-indigo-400">Запустите симуляцию дня для генерации данных.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {patterns.map((pattern) => {
            const status = normalizeStatus(pattern.status)
            const featureSummary = pattern.feature_summary?.trim()
            const currentAction = actionLoading[pattern.id]
            const isBusy = currentAction != null

            return (
              <div key={pattern.id} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <p className="text-sm font-semibold text-indigo-400">Кластер #{pattern.cluster_id}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${STATUS_STYLES[status]}`}>
                    {STATUS_LABELS[status]}
                  </span>
                </div>

                <p className="text-gray-100 leading-relaxed">{pattern.description}</p>

                {featureSummary && (
                  <div className="mt-4 rounded-lg border border-gray-700 bg-gray-900/50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">
                      Сводка признаков
                    </p>
                    <p className="text-sm text-gray-300">{featureSummary}</p>
                  </div>
                )}

                <div className="mt-4 flex items-center justify-between gap-4 flex-wrap">
                  <p className="text-xs text-gray-500">Создан: {formatTimestamp(pattern)}</p>

                  {status === 'pending' && (
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleReview(pattern.id, 'accept')}
                        disabled={isBusy}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white font-semibold transition-colors disabled:opacity-50"
                      >
                        {currentAction === 'accept' ? (
                          <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <CheckCircle size={14} />
                        )}
                        Принять
                      </button>

                      <button
                        onClick={() => handleReview(pattern.id, 'reject')}
                        disabled={isBusy}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold transition-colors disabled:opacity-50"
                      >
                        {currentAction === 'reject' ? (
                          <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <XCircle size={14} />
                        )}
                        Отклонить
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
