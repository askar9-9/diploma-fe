import { AlertCircle, ExternalLink, MoreVertical, Power, Trash2 } from 'lucide-react'
import { useState } from 'react'
import type { Entity } from '../../types/home'
import {
  formatEntityState,
  formatUpdatedAt,
  getEntityIcon,
  getEntityStateDotClass,
  getRoomLabel,
  isEntityActive,
  isEntityControllable,
} from '../../lib/home'

interface EntityCardProps {
  entity: Entity
  onToggle?: (entity: Entity) => void
  onDelete?: (entity: Entity) => void
  showActions?: boolean
  showRoom?: boolean
  toggling?: boolean
}

export function EntityCard({
  entity,
  onToggle,
  onDelete,
  showActions = true,
  showRoom = true,
  toggling = false,
}: EntityCardProps) {
  const Icon = getEntityIcon(entity)
  const isActive = isEntityActive(entity)
  const isControllable = isEntityControllable(entity)
  const roomLabel = getRoomLabel(entity.room, entity.room_ru)
  const [menuOpen, setMenuOpen] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const isUnavailable = entity.state === 'unavailable'

  return (
    <article className="rounded-xl border border-gray-700 bg-gray-800 p-4 shadow-sm transition-colors duration-150">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div
            className={`rounded-xl p-3 transition-colors duration-150 ${
              isActive
                ? 'bg-sky-900/50 text-sky-400'
                : 'bg-gray-700 text-gray-400'
            }`}
          >
            <Icon aria-hidden="true" size={20} />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-sm font-medium text-white">{entity.name}</p>
              <span className="rounded-full bg-gray-700 px-2.5 py-0.5 text-[11px] font-medium text-gray-300">
                {entity.domain}
              </span>
              {showRoom && (
                <span className="rounded-full bg-sky-900/30 px-2.5 py-0.5 text-[11px] font-medium text-sky-400">
                  {roomLabel}
                </span>
              )}
            </div>
            <p className="mt-1 font-mono text-xs text-gray-500 break-all">{entity.entity_id}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span
            className="inline-flex items-center gap-1.5 rounded-full bg-gray-700 px-2.5 py-1 text-xs font-medium text-gray-300"
            aria-live="polite"
          >
            <span aria-hidden="true" className={`h-2 w-2 rounded-full ${getEntityStateDotClass(entity)}`} />
            {formatEntityState(entity)}
          </span>

          {showActions && onDelete && (
            <div className="relative">
              <button
                type="button"
                aria-label="Меню устройства"
                onClick={() => setMenuOpen((v) => !v)}
                className="rounded-lg p-1.5 text-gray-400 transition hover:bg-gray-700 hover:text-white focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
              >
                <MoreVertical aria-hidden="true" size={16} />
              </button>
              {menuOpen && (
                <>
                  <button
                    type="button"
                    aria-label="Закрыть меню"
                    className="fixed inset-0 z-10"
                    onClick={() => setMenuOpen(false)}
                  />
                  <div className="absolute right-0 top-8 z-20 min-w-[140px] rounded-xl border border-gray-700 bg-gray-800 py-1 shadow-xl">
                    <button
                      type="button"
                      onClick={() => { setMenuOpen(false); setConfirmDelete(true) }}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-400 transition hover:bg-gray-700"
                    >
                      <Trash2 aria-hidden="true" size={14} />
                      Удалить
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-gray-500">
        <span>{entity.power_kw.toFixed(2)} кВт</span>
        <span aria-hidden="true" className="text-gray-700">•</span>
        <span>Обновлено: {formatUpdatedAt(entity.updated_at)}</span>
        {entity.model && (
          <>
            <span aria-hidden="true" className="text-gray-700">•</span>
            <span>{entity.model}</span>
          </>
        )}
      </div>

      {showActions && (
        <div className="mt-4 flex flex-wrap items-center gap-3">
          {entity.doc_url ? (
            <a
              href={entity.doc_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-600 px-3 py-2 text-sm font-medium text-gray-300 transition-colors duration-150 hover:border-gray-500 hover:bg-gray-700 hover:text-white focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              <ExternalLink aria-hidden="true" size={14} />
              Документация
            </a>
          ) : null}
          {isControllable && onToggle ? (
            <button
              type="button"
              onClick={() => onToggle(entity)}
              disabled={toggling || isUnavailable}
              className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-white transition-colors duration-150 disabled:cursor-not-allowed focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${
                isUnavailable
                  ? 'bg-gray-700 opacity-30 cursor-not-allowed'
                  : toggling
                  ? 'bg-sky-500/60'
                  : isActive
                  ? 'bg-gray-700 hover:bg-gray-600'
                  : 'bg-sky-500 hover:bg-sky-600'
              }`}
              aria-label={isActive ? 'Выключить' : 'Включить'}
            >
              {toggling ? (
                <span aria-label="Загрузка..." className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <Power aria-hidden="true" size={14} />
              )}
              {isActive ? 'Выключить' : 'Включить'}
            </button>
          ) : null}
        </div>
      )}

      {confirmDelete && (
        <div className="mt-4 rounded-xl border border-red-800 bg-red-900/30 p-4">
          <p className="text-sm text-red-300 font-medium">
            Удалить «{entity.name}»? Это действие необратимо.
          </p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={() => { setConfirmDelete(false); onDelete?.(entity) }}
              className="rounded-lg bg-red-600 px-3 py-1.5 text-sm font-semibold text-white transition hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              Удалить
            </button>
            <button
              type="button"
              onClick={() => setConfirmDelete(false)}
              className="rounded-lg border border-gray-600 px-3 py-1.5 text-sm font-semibold text-gray-300 transition hover:bg-gray-700 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {!showActions && isControllable && (
        <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-500">
          <AlertCircle aria-hidden="true" size={12} />
          <span>Управляемое устройство</span>
        </div>
      )}
    </article>
  )
}
