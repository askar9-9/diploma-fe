import { useEffect, useState } from 'react'
import { PersonStanding, Sofa, Thermometer, Sun, Lightbulb, Lamp, Tv, SlidersHorizontal } from 'lucide-react'
import { devicesApi } from '../api/devicesApi'
import type { Device } from '../api/devicesApi'
import { useWebSocket } from '../hooks/useWebSocket'

const DEVICE_ICONS: Record<string, React.ElementType> = {
  motion_hall: PersonStanding,
  motion_living: Sofa,
  temperature: Thermometer,
  light_level: Sun,
  ceiling_light: Lightbulb,
  bedside_light: Lamp,
  thermostat: Thermometer,
  tv_on: Tv,
}

const DEVICE_NAMES: Record<string, string> = {
  motion_hall: 'Датчик коридора',
  motion_living: 'Датчик гостиной',
  temperature: 'Температура',
  light_level: 'Освещённость',
  ceiling_light: 'Основной свет',
  bedside_light: 'Ночник',
  thermostat: 'Термостат',
  tv_on: 'Телевизор',
}

const SENSOR_IDS = ['motion_hall', 'motion_living', 'temperature', 'light_level']
const ACTUATOR_IDS = ['ceiling_light', 'bedside_light', 'thermostat', 'tv_on']
const BINARY_ACTUATORS = new Set(['ceiling_light', 'bedside_light', 'tv_on'])

function formatSensorValue(id: string, value: number): string {
  if (id === 'temperature') return `${value.toFixed(1)}°C`
  if (id === 'light_level') return `${value.toFixed(1)}%`
  return value ? 'ВКЛ' : 'ВЫКЛ'
}

function formatTime(isoString: string): string {
  const d = new Date(isoString)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export default function DevicesPage() {
  const { lastMessage } = useWebSocket()
  const [devices, setDevices] = useState<Record<string, Device>>({})
  const [loading, setLoading] = useState<Record<string, boolean>>({})
  const [thermostatDraft, setThermostatDraft] = useState<number>(22)

  useEffect(() => {
    devicesApi.list().then((res) => {
      const map: Record<string, Device> = {}
      res.data.forEach((d) => { map[d.id] = d })
      setDevices(map)
      if (map['thermostat']) {
        setThermostatDraft(map['thermostat'].state)
      }
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!lastMessage) return
    const msg = lastMessage as unknown as Record<string, unknown>
    if (msg.type === 'device_update') {
      const deviceId = msg.device_id as string
      const value = msg.value as number
      setDevices((prev) => {
        if (!prev[deviceId]) return prev
        return {
          ...prev,
          [deviceId]: { ...prev[deviceId], state: value, updated_at: new Date().toISOString() },
        }
      })
      if (deviceId === 'thermostat') setThermostatDraft(value)
    }
  }, [lastMessage])

  const sendCommand = async (deviceId: string, value: number) => {
    setLoading((prev) => ({ ...prev, [deviceId]: true }))
    try {
      await devicesApi.command(deviceId, value)
      setDevices((prev) => ({
        ...prev,
        [deviceId]: { ...prev[deviceId], state: value, updated_at: new Date().toISOString() },
      }))
    } catch {
      // ignore
    } finally {
      setLoading((prev) => ({ ...prev, [deviceId]: false }))
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 space-y-8">
      <h1 className="text-2xl font-bold">Устройства</h1>

      {/* Sensors */}
      <section>
        <h2 className="text-lg font-semibold text-gray-300 mb-3">Датчики</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {SENSOR_IDS.map((id) => {
            const device = devices[id]
            const Icon = DEVICE_ICONS[id]
            return (
              <div key={id} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  {Icon && <Icon size={20} className="text-indigo-400" />}
                  <span className="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded-full">только чтение</span>
                </div>
                <div className="font-medium text-gray-300 text-sm mb-1">{DEVICE_NAMES[id]}</div>
                {device ? (
                  <>
                    <div className="text-xl font-bold text-indigo-400">
                      {formatSensorValue(id, device.state)}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{formatTime(device.updated_at)}</div>
                  </>
                ) : (
                  <div className="text-gray-500 text-sm">Загрузка...</div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* Actuators */}
      <section>
        <h2 className="text-lg font-semibold text-gray-300 mb-3">Исполнительные устройства</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {ACTUATOR_IDS.map((id) => {
            const device = devices[id]
            const isLoading = loading[id] || false
            const Icon = DEVICE_ICONS[id]
            const isOn = !!device?.state

            return (
              <div
                key={id}
                className={`rounded-xl p-4 border transition-colors ${
                  id !== 'thermostat' && isOn
                    ? 'bg-indigo-900/20 border-indigo-700'
                    : 'bg-gray-800 border-gray-700'
                }`}
              >
                <div className="flex items-center gap-2 mb-3">
                  {Icon && (
                    <Icon
                      size={20}
                      className={id !== 'thermostat' && isOn ? 'text-indigo-300' : 'text-gray-400'}
                    />
                  )}
                  <span className="font-medium text-gray-300 text-sm">{DEVICE_NAMES[id]}</span>
                </div>

                {id === 'thermostat' ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-1">
                      <SlidersHorizontal size={14} className="text-gray-400" />
                      <span className="text-xs text-gray-400">Температура</span>
                    </div>
                    <div className="text-xl font-bold text-indigo-400">
                      {thermostatDraft.toFixed(1)}°C
                    </div>
                    <input
                      type="range"
                      min={17}
                      max={25}
                      step={0.5}
                      value={thermostatDraft}
                      onChange={(e) => setThermostatDraft(parseFloat(e.target.value))}
                      onMouseUp={() => sendCommand('thermostat', thermostatDraft)}
                      onTouchEnd={() => sendCommand('thermostat', thermostatDraft)}
                      disabled={isLoading}
                      className="w-full accent-indigo-500 disabled:opacity-50"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>17°C</span><span>25°C</span>
                    </div>
                  </div>
                ) : BINARY_ACTUATORS.has(id) ? (
                  <div className="flex items-center justify-between">
                    <span className={`font-bold text-lg ${isOn ? 'text-green-400' : 'text-gray-500'}`}>
                      {isOn ? 'ВКЛ' : 'ВЫКЛ'}
                    </span>
                    <button
                      onClick={() => device && sendCommand(id, device.state ? 0 : 1)}
                      disabled={isLoading || !device}
                      className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50
                        ${isOn
                          ? 'bg-gray-600 hover:bg-gray-500 text-white'
                          : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}
                    >
                      {isLoading ? (
                        <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : isOn ? 'Выключить' : 'Включить'}
                    </button>
                  </div>
                ) : null}
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
