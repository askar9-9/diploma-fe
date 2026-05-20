import type { Entity } from '../../types/home'
import { formatEntityState, getEntityIcon, getRoomLabel, isEntityActive } from '../../lib/home'

interface CompactEntityCardProps {
  entity: Entity
}

export function CompactEntityCard({ entity }: CompactEntityCardProps) {
  const Icon = getEntityIcon(entity)
  const isActive = isEntityActive(entity)
  const roomLabel = getRoomLabel(entity.room, entity.room_ru)

  return (
    <div className="flex items-center gap-3 rounded-xl border border-gray-700 bg-gray-800 p-3 transition-colors duration-150">
      <div
        className={`shrink-0 rounded-lg p-2 ${
          isActive ? 'bg-sky-900/50 text-sky-400' : 'bg-gray-700 text-gray-400'
        }`}
      >
        <Icon aria-hidden="true" size={16} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-white">{entity.name}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-gray-500">{roomLabel}</span>
          <span
            className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
              isActive ? 'bg-sky-900/40 text-sky-400' : 'bg-gray-700 text-gray-500'
            }`}
          >
            {formatEntityState(entity)}
          </span>
        </div>
      </div>
    </div>
  )
}
