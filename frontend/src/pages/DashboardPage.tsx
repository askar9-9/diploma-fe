import { Activity, Cpu, Home, Zap } from 'lucide-react'
import { AreaCard } from '../components/ui/AreaCard'
import { CompactEntityCard } from '../components/ui/CompactEntityCard'
import { StatCard } from '../components/ui/StatCard'
import { CurrentSceneBadge } from '../components/automation/CurrentSceneBadge'
import { useHomeData } from '../context/HomeDataContext'
import {
  getAreaName,
  getRoomIcon,
  isEntityActive,
  isEntityOnline,
  ROOM_OPTIONS,
  sortAreasByKnownOrder,
} from '../lib/home'
import type { Area } from '../types/home'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { areas, entities, entitiesById, error, loading, currentScene } = useHomeData()

  const fallbackAreas: Area[] = ROOM_OPTIONS.map((room) => ({
    id: room.value,
    name_ru: room.label,
    entities: entities
      .filter((entity) => entity.room === room.value)
      .map((entity) => entity.entity_id),
  }))

  const displayAreas = sortAreasByKnownOrder(areas.length > 0 ? areas : fallbackAreas)
  const totalDevices = entities.length
  const onlineDevices = entities.filter((e) => isEntityOnline(e)).length
  const offlineDevices = totalDevices - onlineDevices
  const activeRooms = displayAreas.filter((area) =>
    area.entities.some((entityId) => {
      const entity = entitiesById[entityId]
      return entity ? isEntityActive(entity) : false
    }),
  ).length
  const currentPowerKw = entities.reduce(
    (sum, entity) => (isEntityActive(entity) ? sum + entity.power_kw : sum),
    0,
  )

  const favoriteEntities = entities
    .filter((e) => isEntityActive(e))
    .slice(0, 8)

  return (
    <div className="flex gap-6">
      <div className="flex-1 min-w-0 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-400">
            Главный обзор HomeIQ: комнаты, активные устройства, ML сцена.
          </p>
        </div>

        {error ? (
          <div
            role="alert"
            className="rounded-xl border border-amber-700 bg-amber-900/30 px-4 py-3 text-sm text-amber-300"
          >
            {error}{' '}
            <button
              type="button"
              className="ml-2 underline hover:no-underline"
              onClick={() => window.location.reload()}
            >
              Повторить
            </button>
          </div>
        ) : null}

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            icon={Cpu}
            label="Всего устройств"
            value={totalDevices}
            sub="Загружено из Backend"
            iconColor="text-sky-400"
            iconBg="bg-sky-900/50"
          />
          <StatCard
            icon={Activity}
            label="Статус сети"
            value={`${onlineDevices} / ${offlineDevices}`}
            sub="Подключены / отключены"
            iconColor="text-green-400"
            iconBg="bg-green-900/50"
          />
          <StatCard
            icon={Home}
            label="Активные комнаты"
            value={activeRooms}
            sub={`Из ${displayAreas.length || ROOM_OPTIONS.length} зон`}
            iconColor="text-purple-400"
            iconBg="bg-purple-900/50"
          />
          <StatCard
            icon={Zap}
            label="Потребление"
            value={`${currentPowerKw.toFixed(2)} кВт`}
            sub="Сумма активных нагрузок"
            iconColor="text-amber-400"
            iconBg="bg-amber-900/50"
          />
        </div>

        {loading && entities.length === 0 ? (
          <div className="flex items-center justify-center py-16">
            <span className="h-8 w-8 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" aria-label="Загрузка..." />
          </div>
        ) : null}

        {favoriteEntities.length > 0 && (
          <section>
            <h2 className="mb-3 text-base font-semibold text-white">Избранное</h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
              {favoriteEntities.map((entity) => (
                <CompactEntityCard key={entity.entity_id} entity={entity} />
              ))}
            </div>
          </section>
        )}

        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold text-white">Комнаты</h2>
            <Link
              to="/areas"
              className="text-xs text-sky-400 hover:text-sky-300 transition-colors"
            >
              Все комнаты →
            </Link>
          </div>
          <div className="grid gap-3 grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
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
        </section>
      </div>

      <aside className="hidden lg:flex lg:w-72 xl:w-80 shrink-0 flex-col gap-4">
        <div className="rounded-xl border border-gray-700 bg-gray-800 p-4">
          <h2 className="mb-3 text-sm font-semibold text-white">Сводка</h2>
          <dl className="space-y-2">
            {[
              { label: 'Всего устройств', value: totalDevices },
              { label: 'Активных', value: entities.filter((e) => isEntityActive(e)).length },
              { label: 'Комнат', value: displayAreas.length },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between">
                <dt className="text-xs text-gray-400">{label}</dt>
                <dd className="text-sm font-semibold text-white">{value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <CurrentSceneBadge currentScene={currentScene} />

        <div className="rounded-xl border border-gray-700 bg-gray-800 p-4">
          <h2 className="mb-3 text-sm font-semibold text-white">Быстрые ссылки</h2>
          <div className="space-y-1">
            {[
              { to: '/devices', label: 'Управление устройствами' },
              { to: '/automation', label: 'ML Автоматизация' },
              { to: '/energy', label: 'Энергопотребление' },
            ].map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className="block rounded-lg px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700 hover:text-white"
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      </aside>
    </div>
  )
}
