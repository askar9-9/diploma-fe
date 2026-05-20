import { useEffect, useState } from 'react'
import { Battery, Lightbulb, TrendingUp, Zap } from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { energyApi } from '../api/energyApi'
import { LoadingState } from '../components/ui/LoadingState'
import { useHomeData } from '../context/HomeDataContext'
import { formatCompactNumber, formatEntityState } from '../lib/home'
import type { EnergyHistory, HemsForecast, HemsStatus } from '../types/home'

interface HistoryChartPoint {
  dayLabel: string
  totalKwh: number
}

interface ForecastChartPoint {
  hourLabel: string
  loadForecast: number
  solarForecast: number
}

function getTariffZoneLabel(zone: string): string {
  return zone === 'night' ? 'Ночной тариф' : 'Дневной тариф'
}

function getOptimizerActionLabel(action: string): string {
  if (action === 'charge') {
    return 'Зарядка батареи'
  }

  if (action === 'discharge') {
    return 'Разряд батареи'
  }

  return 'Режим ожидания'
}

function getBatteryStatusText(status: HemsStatus | null): string {
  if (!status) {
    return 'Нет данных'
  }

  if (typeof status.battery_soc === 'number') {
    return `${Math.round(status.battery_soc)}% заряда`
  }

  return getOptimizerActionLabel(status.optimizer_action)
}

function toHistoryChartData(history: EnergyHistory | null): HistoryChartPoint[] {
  if (!history) {
    return []
  }

  return history.days.map((day) => ({
    dayLabel: new Date(day.date).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' }),
    totalKwh: day.total_kwh,
  }))
}

function toForecastChartData(forecast: HemsForecast | null): ForecastChartPoint[] {
  if (!forecast) {
    return []
  }

  return forecast.hours.map((hour, index) => ({
    hourLabel: `${hour.toString().padStart(2, '0')}:00`,
    loadForecast: forecast.load_forecast[index] ?? 0,
    solarForecast: forecast.solar_forecast[index] ?? 0,
  }))
}

export default function EnergyPage() {
  const { entities } = useHomeData()
  const [history, setHistory] = useState<EnergyHistory | null>(null)
  const [forecast, setForecast] = useState<HemsForecast | null>(null)
  const [status, setStatus] = useState<HemsStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    async function loadEnergyData() {
      const [historyResult, forecastResult, statusResult] = await Promise.allSettled([
        energyApi.history(),
        energyApi.forecast(),
        energyApi.status(),
      ])

      if (!isMounted) {
        return
      }

      if (historyResult.status === 'fulfilled') {
        setHistory(historyResult.value.data)
      }

      if (forecastResult.status === 'fulfilled') {
        setForecast(forecastResult.value.data)
      }

      if (statusResult.status === 'fulfilled') {
        setStatus(statusResult.value.data)
      }

      setError(
        historyResult.status === 'rejected' ||
        forecastResult.status === 'rejected' ||
        statusResult.status === 'rejected'
          ? 'Часть энергетических данных недоступна. Показаны только успешно загруженные блоки.'
          : null,
      )
      setLoading(false)
    }

    void loadEnergyData()

    return () => {
      isMounted = false
    }
  }, [])

  const historyChartData = toHistoryChartData(history)
  const forecastChartData = toForecastChartData(forecast)
  const breakdownEntities = entities
    .filter((entity) => entity.domain === 'switch' && entity.power_kw > 0)
    .sort((left, right) => right.power_kw - left.power_kw)
  const totalBreakdownPower = breakdownEntities.reduce((sum, entity) => sum + entity.power_kw, 0)

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold text-white">Энергия</h1>
        <p className="text-sm text-gray-400">
          История потребления, прогноз нагрузки и рекомендации HEMS на ближайшие 24 часа.
        </p>
      </div>

      {error ? (
        <div role="alert" className="rounded-3xl border border-amber-700 bg-amber-900/30 px-4 py-3 text-sm text-amber-300">
          {error}
        </div>
      ) : null}

      {loading && !history && !forecast && !status ? <LoadingState /> : null}

      <div className="grid gap-4 lg:grid-cols-3">
        <article className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-amber-900/40 p-3 text-amber-400">
              <Zap aria-hidden="true" size={20} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-400">Тариф сейчас</p>
              <p className="text-2xl font-semibold text-white">
                {status ? `${formatCompactNumber(status.tariff_price)} тг/кВт·ч` : '—'}
              </p>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-400">
            {status ? getTariffZoneLabel(status.tariff_zone) : 'Статус тарифа недоступен'}
          </p>
        </article>

        <article className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-sky-900/40 p-3 text-sky-400">
              <Lightbulb aria-hidden="true" size={20} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-400">Рекомендация</p>
              <p className="text-xl font-semibold text-white">
                {status ? getOptimizerActionLabel(status.optimizer_action) : '—'}
              </p>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-400">
            {status?.recommendation ?? 'Рекомендация от оптимизатора пока недоступна.'}
          </p>
        </article>

        <article className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-green-900/40 p-3 text-green-400">
              <Battery aria-hidden="true" size={20} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-400">Статус батареи</p>
              <p className="text-xl font-semibold text-white">{getBatteryStatusText(status)}</p>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-400">
            {status
              ? `Текущий час: ${status.current_hour.toString().padStart(2, '0')}:00`
              : 'Нет данных о текущем часу.'}
          </p>
        </article>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-3">
            <TrendingUp aria-hidden="true" size={18} className="text-blue-600" />
            <div>
              <h2 className="text-lg font-semibold text-white">Потребление за 7 дней</h2>
              <p className="text-sm text-gray-400">Историческое потребление в кВт·ч по дням.</p>
            </div>
          </div>
          {historyChartData.length === 0 ? (
            <p className="rounded-xl bg-gray-700/50 px-4 py-10 text-center text-sm text-gray-400">
              История потребления пока недоступна.
            </p>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={historyChartData}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="dayLabel" />
                  <YAxis unit=" кВт·ч" />
                  <Tooltip />
                  <Bar dataKey="totalKwh" name="Потребление" fill="#2563eb" radius={[12, 12, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>

        <section className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-3">
            <Zap aria-hidden="true" size={18} className="text-amber-600" />
            <div>
              <h2 className="text-lg font-semibold text-white">Прогноз на 24 часа</h2>
              <p className="text-sm text-gray-400">Сравнение нагрузки и солнечной генерации по часам.</p>
            </div>
          </div>
          {forecastChartData.length === 0 ? (
            <p className="rounded-xl bg-gray-700/50 px-4 py-10 text-center text-sm text-gray-400">
              Прогноз нагрузки пока недоступен.
            </p>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecastChartData}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="hourLabel" minTickGap={24} />
                  <YAxis unit=" кВт" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="loadForecast"
                    name="Нагрузка"
                    stroke="#2563eb"
                    strokeWidth={3}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="solarForecast"
                    name="Солнечная генерация"
                    stroke="#eab308"
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
      </div>

      <section className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Потребление по устройствам</h2>
            <p className="text-sm text-gray-400">
              Таблица по сущностям `switch.*` и их номинальной нагрузке.
            </p>
          </div>
          <div className="rounded-xl bg-gray-700 px-4 py-2 text-sm font-medium text-gray-300">
            Итого: {totalBreakdownPower.toFixed(2)} кВт
          </div>
        </div>

        {breakdownEntities.length === 0 ? (
          <p className="rounded-xl bg-gray-700/50 px-4 py-10 text-center text-sm text-gray-400">
            В системе пока нет нагрузок `switch.*` с указанным `power_kw`.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700 text-sm">
              <thead>
                <tr className="text-left text-gray-400">
                  <th className="py-3 pr-4 font-medium">Сущность</th>
                  <th className="py-3 pr-4 font-medium">Название</th>
                  <th className="py-3 pr-4 font-medium">Состояние</th>
                  <th className="py-3 font-medium">Мощность</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/50">
                {breakdownEntities.map((entity) => (
                  <tr key={entity.entity_id}>
                    <td className="py-3 pr-4 font-mono text-xs text-gray-300">{entity.entity_id}</td>
                    <td className="py-3 pr-4 text-white">{entity.name}</td>
                    <td className="py-3 pr-4 text-gray-400">{formatEntityState(entity)}</td>
                    <td className="py-3 font-medium text-white">{entity.power_kw.toFixed(2)} кВт</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
