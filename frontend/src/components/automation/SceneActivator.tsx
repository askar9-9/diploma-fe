import { useState } from 'react'
import type { SceneName } from '../../types/home'
import { scenesApi } from '../../api/scenesApi'

const SCENES: Array<{ id: SceneName; label: string; emoji: string; color: string; activeColor: string }> = [
  { id: 'day',   label: 'День',       emoji: '🌞', color: 'border-gray-700 bg-gray-800 hover:bg-gray-700', activeColor: 'border-amber-500 bg-amber-900/40 text-amber-300' },
  { id: 'night', label: 'Ночь',       emoji: '🌙', color: 'border-gray-700 bg-gray-800 hover:bg-gray-700', activeColor: 'border-indigo-500 bg-indigo-900/40 text-indigo-300' },
  { id: 'away',  label: 'Никого нет', emoji: '🏠', color: 'border-gray-700 bg-gray-800 hover:bg-gray-700', activeColor: 'border-gray-500 bg-gray-700 text-gray-300' },
  { id: 'movie', label: 'Кино',       emoji: '🎬', color: 'border-gray-700 bg-gray-800 hover:bg-gray-700', activeColor: 'border-purple-500 bg-purple-900/40 text-purple-300' },
]

interface SceneActivatorProps {
  activeScene: SceneName | null
  onSceneActivated?: (scene: SceneName) => void
}

export function SceneActivator({ activeScene, onSceneActivated }: SceneActivatorProps) {
  const [pending, setPending] = useState<SceneName | null>(null)
  const [confirm, setConfirm] = useState<SceneName | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function activate(scene: SceneName) {
    setPending(scene)
    setError(null)
    setConfirm(null)
    try {
      await scenesApi.activate(scene)
      onSceneActivated?.(scene)
    } catch {
      setError('Не удалось активировать сцену. Проверьте соединение.')
    } finally {
      setPending(null)
    }
  }

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-800 p-4">
      <h3 className="mb-3 text-sm font-semibold text-white">Активировать сцену вручную</h3>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {SCENES.map((scene) => {
          const isActive = activeScene === scene.id
          const isLoading = pending === scene.id
          return (
            <button
              key={scene.id}
              type="button"
              onClick={() => setConfirm(scene.id)}
              disabled={isLoading}
              className={`flex flex-col items-center gap-1.5 rounded-xl border px-3 py-3 text-sm font-medium transition-colors duration-150 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-60 ${
                isActive ? scene.activeColor : `text-gray-300 ${scene.color}`
              } ${isActive ? 'ring-2 ring-current ring-offset-2 ring-offset-gray-800' : ''}`}
            >
              <span className="text-xl" aria-hidden="true">{scene.emoji}</span>
              {isLoading ? (
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
              ) : (
                <span>{scene.label}</span>
              )}
            </button>
          )
        })}
      </div>

      {confirm && (
        <div className="mt-3 rounded-xl border border-sky-800 bg-sky-900/30 p-3">
          <p className="text-sm text-sky-300">
            Активировать сцену «{SCENES.find((s) => s.id === confirm)?.label}»?
          </p>
          <div className="mt-2 flex gap-2">
            <button
              type="button"
              onClick={() => activate(confirm)}
              className="rounded-lg bg-sky-500 px-3 py-1.5 text-sm font-semibold text-white transition hover:bg-sky-600 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              Активировать
            </button>
            <button
              type="button"
              onClick={() => setConfirm(null)}
              className="rounded-lg border border-gray-600 px-3 py-1.5 text-sm font-semibold text-gray-300 transition hover:bg-gray-700 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-3 rounded-xl border border-red-800 bg-red-900/30 px-3 py-2 text-sm text-red-400">
          {error}
        </p>
      )}
    </div>
  )
}
