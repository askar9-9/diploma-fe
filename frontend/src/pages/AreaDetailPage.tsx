import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { EntityCard } from '../components/ui/EntityCard'
import { useHomeData } from '../context/HomeDataContext'
import { getAreaName, getRoomIcon, isEntityActive, ROOM_OPTIONS } from '../lib/home'
import type { Entity } from '../types/home'

type DomainFilter = 'all' | 'lighting' | 'sensors' | 'devices'

const DOMAIN_FILTERS: Array<{ label: string; value: DomainFilter }> = [
  { label: 'Все', value: 'all' },
  { label: 'Датчики', value: 'sensors' },
  { label: 'Устройства', value: 'devices' },
  { label: 'Освещение', value: 'lighting' },
]

function matchesDomainFilter(entity: Entity, filter: DomainFilter): boolean {
  if (filter === 'all') return true
  if (filter === 'sensors') return entity.domain === 'sensor' || entity.domain === 'binary_sensor'
  if (filter === 'devices') return entity.domain === 'switch' || entity.domain === 'climate'
  return entity.domain === 'light'
}

export default function AreaDetailPage() {
  const { areaId } = useParams<{ areaId: string }>()
  const { areas, entities, deleteEntity, sendEntityCommand } = useHomeData()
  const [domainFilter, setDomainFilter] = useState<DomainFilter>('all')
  const [pendingEntityId, setPendingEntityId] = useState<string | null>(null)

  const area = areas.find((a) => a.id === areaId)
  const fallbackRoom = ROOM_OPTIONS.find((r) => r.value === areaId)

  const areaName = area
    ? getAreaName(area)
    : fallbackRoom?.label ?? areaId ?? 'Комната'

  const areaEntities = entities.filter((e) => e.room === areaId)
  const filteredEntities = areaEntities.filter((e) => matchesDomainFilter(e, domainFilter))
  const activeCount = areaEntities.filter((e) => isEntityActive(e)).length
  const RoomIcon = getRoomIcon(areaId ?? '')

  async function handleToggle(entity: Entity) {
    setPendingEntityId(entity.entity_id)
    try {
      await sendEntityCommand(entity.entity_id, {
        state: isEntityActive(entity) ? 'off' : 'on',
      })
    } finally {
      setPendingEntityId(null)
    }
  }

  async function handleDelete(entity: Entity) {
    try {
      await deleteEntity(entity.entity_id)
    } catch {
      // error handled silently
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          to="/areas"
          className="rounded-xl border border-gray-700 p-2.5 text-gray-400 transition hover:bg-gray-700 hover:text-white focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
          aria-label="Назад к комнатам"
        >
          <ArrowLeft aria-hidden="true" size={18} />
        </Link>
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-sky-900/40 p-3 text-sky-400">
            <RoomIcon aria-hidden="true" size={22} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-white">{areaName}</h1>
            <p className="text-sm text-gray-400">
              {areaEntities.length} устройств · {activeCount} активных
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {DOMAIN_FILTERS.map((filter) => (
          <button
            key={filter.value}
            type="button"
            onClick={() => setDomainFilter(filter.value)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition-colors duration-150 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${
              domainFilter === filter.value
                ? 'bg-sky-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {filteredEntities.length === 0 ? (
        <div className="rounded-xl border border-gray-700 bg-gray-800 px-6 py-12 text-center">
          <p className="text-sm text-gray-500">В этой комнате нет устройств по выбранному фильтру.</p>
        </div>
      ) : (
        <div className="grid gap-4 xl:grid-cols-2">
          {filteredEntities.map((entity) => (
            <EntityCard
              key={entity.entity_id}
              entity={entity}
              onToggle={handleToggle}
              onDelete={handleDelete}
              toggling={pendingEntityId === entity.entity_id}
              showRoom={false}
            />
          ))}
        </div>
      )}
    </div>
  )
}
