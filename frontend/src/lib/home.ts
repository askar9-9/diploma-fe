import {
  Activity,
  AlertTriangle,
  Bath,
  BedDouble,
  ChefHat,
  Cpu,
  DoorOpen,
  Droplets,
  Lightbulb,
  Power,
  Settings2,
  Sofa,
  Sun,
  Thermometer,
  TreePine,
  type LucideIcon,
  Zap,
} from 'lucide-react'
import type { Area, Entity } from '../types/home'

export const ROOM_OPTIONS = [
  { value: 'hallway', label: 'Прихожая', icon: DoorOpen },
  { value: 'living', label: 'Гостиная', icon: Sofa },
  { value: 'kitchen', label: 'Кухня', icon: ChefHat },
  { value: 'bedroom', label: 'Спальня', icon: BedDouble },
  { value: 'bathroom', label: 'Ванная', icon: Bath },
  { value: 'outdoor', label: 'Улица', icon: TreePine },
  { value: 'utility', label: 'Котельная', icon: Settings2 },
] as const

export const DOMAIN_OPTIONS = [
  { value: 'binary_sensor', label: 'Бинарный датчик' },
  { value: 'sensor', label: 'Датчик' },
  { value: 'switch', label: 'Устройство' },
  { value: 'light', label: 'Освещение' },
  { value: 'climate', label: 'Климат' },
] as const

const ROOM_LABELS = Object.fromEntries(ROOM_OPTIONS.map((room) => [room.value, room.label]))
const ROOM_INDEX = Object.fromEntries(ROOM_OPTIONS.map((room, index) => [room.value, index]))

export function getAreaName(area: Area): string {
  return area.name_ru || ROOM_LABELS[area.id] || area.id
}

export function getRoomLabel(room: string, fallback?: string): string {
  return fallback || ROOM_LABELS[room] || room
}

export function sortAreasByKnownOrder(areas: Area[]): Area[] {
  return [...areas].sort((left, right) => {
    const leftIndex = ROOM_INDEX[left.id] ?? Number.MAX_SAFE_INTEGER
    const rightIndex = ROOM_INDEX[right.id] ?? Number.MAX_SAFE_INTEGER
    return leftIndex - rightIndex || getAreaName(left).localeCompare(getAreaName(right), 'ru')
  })
}

export function getRoomIcon(room: string): LucideIcon {
  const roomOption = ROOM_OPTIONS.find((option) => option.value === room)
  return roomOption?.icon ?? Cpu
}

export function parseNumericState(state: string): number | null {
  if (!state || ['on', 'off', 'unknown', 'unavailable'].includes(state)) {
    return null
  }

  const numeric = Number(state)
  return Number.isFinite(numeric) ? numeric : null
}

export function isEntityActive(entity: Pick<Entity, 'state'>): boolean {
  if (entity.state === 'on') {
    return true
  }

  if (entity.state === 'off' || entity.state === 'unknown' || entity.state === 'unavailable') {
    return false
  }

  const numeric = parseNumericState(entity.state)
  return numeric != null && numeric > 0
}

export function isEntityOnline(entity: Pick<Entity, 'state' | 'attributes'>): boolean {
  const availability = entity.attributes.available

  if (typeof availability === 'boolean') {
    return availability
  }

  return entity.state !== 'unknown' && entity.state !== 'unavailable'
}

export function isEntityControllable(entity: Pick<Entity, 'domain'>): boolean {
  return entity.domain === 'switch' || entity.domain === 'light'
}

export function getEntityDeviceClass(entity: Pick<Entity, 'attributes'>): string | undefined {
  const value = entity.attributes.device_class
  return typeof value === 'string' ? value : undefined
}

export function getEntityUnit(entity: Pick<Entity, 'attributes'>): string {
  const value = entity.attributes.unit_of_measurement
  return typeof value === 'string' ? value : ''
}

export function formatCompactNumber(value: number): string {
  if (Number.isInteger(value)) {
    return value.toString()
  }

  if (Math.abs(value) >= 10) {
    return value.toFixed(0)
  }

  return value.toFixed(1)
}

export function formatEntityState(entity: Pick<Entity, 'state' | 'attributes'>): string {
  if (entity.state === 'on') {
    return 'Включено'
  }

  if (entity.state === 'off') {
    return 'Выключено'
  }

  if (entity.state === 'unavailable' || entity.state === 'unknown') {
    return 'Недоступно'
  }

  const numeric = parseNumericState(entity.state)
  if (numeric == null) {
    return entity.state
  }

  const unit = getEntityUnit(entity)
  return `${formatCompactNumber(numeric)}${unit ? ` ${unit}` : ''}`
}

export function formatUpdatedAt(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Время неизвестно'
  }

  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getEntityStateDotClass(entity: Pick<Entity, 'state'>): string {
  return isEntityActive(entity) ? 'bg-green-500' : 'bg-gray-400'
}

export function getEntityIcon(entity: Pick<Entity, 'domain' | 'attributes'>): LucideIcon {
  const deviceClass = getEntityDeviceClass(entity)

  if (entity.domain === 'binary_sensor') {
    if (deviceClass === 'motion') {
      return Activity
    }

    if (deviceClass === 'door') {
      return DoorOpen
    }

    if (deviceClass === 'smoke') {
      return AlertTriangle
    }
  }

  if (entity.domain === 'sensor') {
    if (deviceClass === 'temperature') {
      return Thermometer
    }

    if (deviceClass === 'humidity') {
      return Droplets
    }

    if (deviceClass === 'illuminance') {
      return Sun
    }

    if (deviceClass === 'power' || deviceClass === 'battery') {
      return Zap
    }
  }

  if (entity.domain === 'switch') {
    return Power
  }

  if (entity.domain === 'light') {
    return Lightbulb
  }

  if (entity.domain === 'climate') {
    return Thermometer
  }

  return Cpu
}
