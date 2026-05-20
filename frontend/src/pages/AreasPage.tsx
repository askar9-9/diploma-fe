import { AreaCard } from '../components/ui/AreaCard'
import { useHomeData } from '../context/HomeDataContext'
import {
  getAreaName,
  getRoomIcon,
  isEntityActive,
  ROOM_OPTIONS,
  sortAreasByKnownOrder,
} from '../lib/home'
import type { Area } from '../types/home'

export default function AreasPage() {
  const { areas, entities, entitiesById, loading } = useHomeData()

  const fallbackAreas: Area[] = ROOM_OPTIONS.map((room) => ({
    id: room.value,
    name_ru: room.label,
    entities: entities
      .filter((entity) => entity.room === room.value)
      .map((entity) => entity.entity_id),
  }))

  const displayAreas = sortAreasByKnownOrder(areas.length > 0 ? areas : fallbackAreas)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Комнаты</h1>
        <p className="mt-1 text-sm text-gray-400">
          Зоны дома — нажмите на плитку для просмотра устройств.
        </p>
      </div>

      {loading && entities.length === 0 ? (
        <div className="flex items-center justify-center py-16">
          <span className="h-8 w-8 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" aria-label="Загрузка..." />
        </div>
      ) : (
        <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5">
          {displayAreas.map((area) => {
            const activeCount = area.entities.filter((entityId) => {
              const entity = entitiesById[entityId]
              return entity ? isEntityActive(entity) : false
            }).length

            return (
              <AreaCard
                key={area.id}
                activeCount={activeCount}
                deviceCount={area.entities.length}
                href={`/areas/${area.id}`}
                icon={getRoomIcon(area.id)}
                name={getAreaName(area)}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
