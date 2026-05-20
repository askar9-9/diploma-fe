import { useEffect, useState } from 'react'
import { Brain } from 'lucide-react'
import { mlApi } from '../api/mlApi'
import { CurrentSceneBadge } from '../components/automation/CurrentSceneBadge'
import { FeatureVectorTable } from '../components/automation/FeatureVectorTable'
import { MlHistoryTable } from '../components/automation/MlHistoryTable'
import { SceneActivator } from '../components/automation/SceneActivator'
import { useHomeData } from '../context/HomeDataContext'
import type { FeatureVector, MLHistoryItem } from '../types/home'

const PAGE_SIZE = 20

export default function AutomationPage() {
  const { currentScene, lastMlDecision } = useHomeData()
  const [featureVector, setFeatureVector] = useState<FeatureVector | null>(null)
  const [historyItems, setHistoryItems] = useState<MLHistoryItem[]>([])
  const [historyTotal, setHistoryTotal] = useState(0)
  const [historyPage, setHistoryPage] = useState(0)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function loadFeatureVector() {
    try {
      const res = await mlApi.featureVector()
      setFeatureVector(res.data)
    } catch {
      // silently ignore, use lastMlDecision as fallback
    }
  }

  async function loadHistory(page: number) {
    setLoadingHistory(true)
    try {
      const res = await mlApi.history(PAGE_SIZE, page * PAGE_SIZE)
      setHistoryItems(res.data.items)
      setHistoryTotal(res.data.total)
    } catch {
      setError('Не удалось загрузить историю ML решений.')
    } finally {
      setLoadingHistory(false)
    }
  }

  useEffect(() => {
    void loadFeatureVector()
    void loadHistory(0)
  }, [])

  useEffect(() => {
    void loadHistory(historyPage)
  }, [historyPage])

  const displayVector = featureVector ?? lastMlDecision?.feature_vector ?? null

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-sky-900/40 p-3 text-sky-400 shrink-0">
          <Brain aria-hidden="true" size={22} />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-white">Автоматизация</h1>
          <p className="mt-1 text-sm text-gray-400">
            ML pipeline: датчики → вектор признаков → Random Forest → сцена
          </p>
        </div>
      </div>

      {error && (
        <div role="alert" className="rounded-xl border border-amber-700 bg-amber-900/30 px-4 py-3 text-sm text-amber-300">
          {error}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <CurrentSceneBadge currentScene={currentScene} />
        <SceneActivator activeScene={currentScene.scene} />
      </div>

      {displayVector && (
        <section>
          <h2 className="mb-3 text-base font-semibold text-white">
            Текущий вектор признаков
          </h2>
          <FeatureVectorTable vector={displayVector} />
        </section>
      )}

      {lastMlDecision && (
        <section className="rounded-xl border border-gray-700 bg-gray-800 p-4">
          <h2 className="mb-3 text-base font-semibold text-white">Последнее ML решение</h2>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Object.entries(lastMlDecision.probabilities).map(([scene, prob]) => (
              <div key={scene} className="rounded-lg bg-gray-700/50 px-3 py-2 text-center">
                <p className="text-xs text-gray-400">{scene}</p>
                <p className="mt-1 text-lg font-bold text-white">{Math.round((prob as number) * 100)}%</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-base font-semibold text-white">
          История решений ML
        </h2>
        {loadingHistory ? (
          <div className="flex items-center justify-center py-10">
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" aria-label="Загрузка..." />
          </div>
        ) : (
          <MlHistoryTable
            items={historyItems}
            total={historyTotal}
            page={historyPage}
            onPageChange={setHistoryPage}
            pageSize={PAGE_SIZE}
          />
        )}
      </section>
    </div>
  )
}
