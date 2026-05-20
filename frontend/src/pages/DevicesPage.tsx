import { Plus, X } from 'lucide-react'
import { useState, type ChangeEvent, type FormEvent } from 'react'
import { EntityCard } from '../components/ui/EntityCard'
import { useHomeData } from '../context/HomeDataContext'
import { DOMAIN_OPTIONS, getRoomLabel, isEntityActive, ROOM_OPTIONS } from '../lib/home'
import type { CreateEntityRequest, Entity } from '../types/home'

type DomainFilter = 'all' | 'lighting' | 'sensors' | 'devices'
type RoomFilter = 'all' | (typeof ROOM_OPTIONS)[number]['value']

const DEVICE_FORM_INITIAL: CreateEntityRequest = {
  entity_id: '',
  name: '',
  model: '',
  domain: 'binary_sensor',
  room: 'hallway',
  doc_url: '',
}

const ROOM_FILTERS: Array<{ label: string; value: RoomFilter }> = [
  { label: 'Все', value: 'all' },
  ...ROOM_OPTIONS.map((room) => ({ label: room.label, value: room.value })),
]

const DOMAIN_FILTERS: Array<{ label: string; value: DomainFilter }> = [
  { label: 'Все', value: 'all' },
  { label: 'Датчики', value: 'sensors' },
  { label: 'Устройства', value: 'devices' },
  { label: 'Освещение', value: 'lighting' },
]

function matchesDomainFilter(entity: Entity, filter: DomainFilter) {
  if (filter === 'all') return true
  if (filter === 'sensors') return entity.domain === 'sensor' || entity.domain === 'binary_sensor'
  if (filter === 'devices') return entity.domain === 'switch' || entity.domain === 'climate'
  return entity.domain === 'light'
}

const ENTITY_ID_REGEX = /^(binary_sensor|sensor|switch|light|climate)\.[a-z][a-z0-9_]{2,63}$/

export default function DevicesPage() {
  const { createEntity, deleteEntity, entities, error, loading, sendEntityCommand } = useHomeData()
  const [roomFilter, setRoomFilter] = useState<RoomFilter>('all')
  const [domainFilter, setDomainFilter] = useState<DomainFilter>('all')
  const [formState, setFormState] = useState<CreateEntityRequest>(DEVICE_FORM_INITIAL)
  const [formError, setFormError] = useState<string | null>(null)
  const [entityIdError, setEntityIdError] = useState<string | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [pendingEntityId, setPendingEntityId] = useState<string | null>(null)

  const filteredEntities = entities.filter(
    (entity) =>
      (roomFilter === 'all' || entity.room === roomFilter) &&
      matchesDomainFilter(entity, domainFilter),
  )

  const deviceCountsByRoom = ROOM_OPTIONS.map((room) => ({
    ...room,
    count: entities.filter((entity) => entity.room === room.value).length,
  }))

  function handleFormChange(event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value } = event.target
    setFormState((s) => ({ ...s, [name]: value }))

    if (name === 'entity_id') {
      if (value && !ENTITY_ID_REGEX.test(value)) {
        setEntityIdError('Формат: {domain}.{name} — только строчные буквы и цифры')
      } else {
        setEntityIdError(null)
      }
    }
  }

  function closeDialog() {
    setIsDialogOpen(false)
    setFormError(null)
    setEntityIdError(null)
    setFormState(DEVICE_FORM_INITIAL)
  }

  async function handleCreateEntity(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (entityIdError) return
    setIsSubmitting(true)
    setFormError(null)

    try {
      await createEntity(formState)
      closeDialog()
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 409) {
        setFormError('Entity ID уже занят. Выберите другой.')
      } else {
        setFormError('Не удалось добавить устройство. Проверьте данные и повторите попытку.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

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
      // silently ignore
    }
  }

  const inputClass =
    'w-full rounded-xl border border-gray-600 bg-gray-700 px-4 py-3 text-white placeholder-gray-500 focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800 text-sm'
  const selectClass =
    'w-full rounded-xl border border-gray-600 bg-gray-700 px-4 py-3 text-white focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800 text-sm'

  return (
    <div className="space-y-6 pb-24">
      <div>
        <h1 className="text-2xl font-semibold text-white">Устройства</h1>
        <p className="mt-1 text-sm text-gray-400">
          Устройства умного дома с фильтрами по комнате и домену.
        </p>
      </div>

      {error ? (
        <div role="alert" className="rounded-xl border border-amber-700 bg-amber-900/30 px-4 py-3 text-sm text-amber-300">
          {error}
        </div>
      ) : null}

      <section className="space-y-4 rounded-xl border border-gray-700 bg-gray-800 p-4">
        <h2 className="text-sm font-semibold text-white">Фильтр по комнате</h2>
        <div className="flex flex-wrap gap-2">
          {ROOM_FILTERS.map((room) => (
            <button
              key={room.value}
              type="button"
              onClick={() => setRoomFilter(room.value)}
              className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors duration-150 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${
                roomFilter === room.value
                  ? 'bg-sky-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {room.label}
            </button>
          ))}
        </div>
        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
          {deviceCountsByRoom.map((room) => (
            <div key={room.value} className="rounded-lg bg-gray-700/50 px-3 py-2">
              <p className="text-sm font-medium text-white">{room.label}</p>
              <p className="mt-0.5 text-xs text-gray-400">{room.count} устройств</p>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3 rounded-xl border border-gray-700 bg-gray-800 p-4">
        <h2 className="text-sm font-semibold text-white">Фильтр по домену</h2>
        <div className="flex flex-wrap gap-2">
          {DOMAIN_FILTERS.map((filter) => (
            <button
              key={filter.value}
              type="button"
              onClick={() => setDomainFilter(filter.value)}
              className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors duration-150 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${
                domainFilter === filter.value
                  ? 'bg-gray-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </section>

      {loading && entities.length === 0 ? (
        <div className="flex items-center justify-center py-16">
          <span className="h-8 w-8 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" aria-label="Загрузка..." />
        </div>
      ) : null}

      <section className="space-y-4">
        <div>
          <h2 className="text-base font-semibold text-white">Список устройств</h2>
          <p className="text-sm text-gray-400">
            Найдено {filteredEntities.length} устройств
            {roomFilter !== 'all' ? ` в комнате «${getRoomLabel(roomFilter)}»` : ''}
            {domainFilter !== 'all'
              ? ` по фильтру «${DOMAIN_FILTERS.find((f) => f.value === domainFilter)?.label}»`
              : ''}
            .
          </p>
        </div>

        {filteredEntities.length === 0 && !loading ? (
          <div className="rounded-xl border border-gray-700 bg-gray-800 px-6 py-12 text-center">
            <p className="text-sm text-gray-500">
              {entities.length === 0
                ? 'Устройства не найдены. Добавьте первое устройство.'
                : 'Сущности по выбранным фильтрам не найдены.'}
            </p>
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
              />
            ))}
          </div>
        )}
      </section>

      <button
        type="button"
        onClick={() => setIsDialogOpen(true)}
        aria-label="Добавить устройство"
        className="fixed bottom-6 right-6 inline-flex items-center gap-3 rounded-full bg-sky-500 px-5 py-4 text-sm font-semibold text-white shadow-lg shadow-sky-900/30 transition hover:bg-sky-600 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900"
      >
        <Plus aria-hidden="true" size={18} />
        <span className="hidden sm:inline">Добавить устройство</span>
      </button>

      {isDialogOpen ? (
        <div className="fixed inset-0 z-40">
          <button
            type="button"
            aria-label="Закрыть диалог"
            className="absolute inset-0 bg-gray-950/70"
            onClick={closeDialog}
          />
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby="add-entity-title"
              className="relative z-10 w-full max-w-2xl rounded-xl border border-gray-700 bg-gray-800 p-6 shadow-2xl"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 id="add-entity-title" className="text-xl font-semibold text-white">
                    Добавить устройство
                  </h2>
                  <p className="mt-1 text-sm text-gray-400">
                    Создайте новую сущность и добавьте её в нужную комнату.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={closeDialog}
                  className="rounded-lg p-2 text-gray-400 transition hover:bg-gray-700 hover:text-white focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                >
                  <X aria-hidden="true" size={18} />
                </button>
              </div>

              <form className="mt-5 space-y-4" onSubmit={handleCreateEntity}>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="space-y-1.5 text-sm font-medium text-gray-300">
                    <span>Entity ID <span className="text-red-400">*</span></span>
                    <input
                      name="entity_id"
                      value={formState.entity_id}
                      onChange={handleFormChange}
                      placeholder="binary_sensor.motion_hallway"
                      className={inputClass}
                      required
                    />
                    {entityIdError && (
                      <p className="text-xs text-red-400">{entityIdError}</p>
                    )}
                  </label>
                  <label className="space-y-1.5 text-sm font-medium text-gray-300">
                    <span>Название <span className="text-red-400">*</span></span>
                    <input
                      name="name"
                      value={formState.name}
                      onChange={handleFormChange}
                      placeholder="Xiaomi Mi Motion Sensor 2"
                      className={inputClass}
                      required
                      minLength={2}
                    />
                  </label>
                  <label className="space-y-1.5 text-sm font-medium text-gray-300">
                    <span>Модель</span>
                    <input
                      name="model"
                      value={formState.model}
                      onChange={handleFormChange}
                      placeholder="RTCGQ02LM"
                      className={inputClass}
                    />
                  </label>
                  <label className="space-y-1.5 text-sm font-medium text-gray-300">
                    <span>Домен <span className="text-red-400">*</span></span>
                    <select
                      name="domain"
                      value={formState.domain}
                      onChange={handleFormChange}
                      className={selectClass}
                    >
                      {DOMAIN_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="space-y-1.5 text-sm font-medium text-gray-300">
                    <span>Комната <span className="text-red-400">*</span></span>
                    <select
                      name="room"
                      value={formState.room}
                      onChange={handleFormChange}
                      className={selectClass}
                    >
                      {ROOM_OPTIONS.map((room) => (
                        <option key={room.value} value={room.value}>
                          {room.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="space-y-1.5 text-sm font-medium text-gray-300">
                    <span>Мощность (кВт)</span>
                    <input
                      name="power_kw"
                      type="number"
                      min="0"
                      max="50"
                      step="0.01"
                      value={String((formState as unknown as Record<string, unknown>).power_kw ?? '0')}
                      onChange={handleFormChange}
                      placeholder="0.15"
                      className={inputClass}
                    />
                  </label>
                  <label className="space-y-1.5 text-sm font-medium text-gray-300 sm:col-span-2">
                    <span>Документация (URL)</span>
                    <input
                      name="doc_url"
                      type="url"
                      value={formState.doc_url}
                      onChange={handleFormChange}
                      placeholder="https://www.mi.com/global/product/..."
                      className={inputClass}
                    />
                  </label>
                </div>

                {formError ? (
                  <p role="alert" className="rounded-xl border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-400">
                    {formError}
                  </p>
                ) : null}

                <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                  <button
                    type="button"
                    onClick={closeDialog}
                    className="rounded-xl border border-gray-600 px-4 py-2.5 text-sm font-semibold text-gray-300 transition hover:bg-gray-700 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || !!entityIdError}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-600 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-60"
                  >
                    {isSubmitting ? (
                      <span aria-label="Загрузка..." className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    ) : (
                      <Plus aria-hidden="true" size={16} />
                    )}
                    Добавить устройство
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
