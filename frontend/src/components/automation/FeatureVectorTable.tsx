import type { FeatureVector } from '../../types/home'

const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

interface Row {
  key: keyof FeatureVector
  label: string
  render: (v: number) => React.ReactNode
}

const ROWS: Row[] = [
  {
    key: 'hour_of_day',
    label: 'Час суток',
    render: (v) => (
      <div className="flex items-center gap-2">
        <span className="text-white">{v}:00</span>
        <div className="flex-1 h-1.5 rounded-full bg-gray-700 max-w-[80px] overflow-hidden">
          <div className="h-full rounded-full bg-sky-500" style={{ width: `${(v / 23) * 100}%` }} />
        </div>
      </div>
    ),
  },
  {
    key: 'weekday',
    label: 'День недели',
    render: (v) => <span className="text-white">{WEEKDAYS[v] ?? v}</span>,
  },
  {
    key: 'motion_hall',
    label: 'Движение (прихожая)',
    render: (v) => (
      <span className={v ? 'text-green-400' : 'text-gray-500'}>
        {v ? '🟢 Движение есть' : '🔴 Нет движения'}
      </span>
    ),
  },
  {
    key: 'motion_living',
    label: 'Движение (гостиная)',
    render: (v) => (
      <span className={v ? 'text-green-400' : 'text-gray-500'}>
        {v ? '🟢 Движение есть' : '🔴 Нет движения'}
      </span>
    ),
  },
  {
    key: 'temperature',
    label: 'Температура',
    render: (v) => (
      <div className="flex items-center gap-2">
        <span className="text-white">{v.toFixed(1)}°C</span>
        <div className="flex-1 h-1.5 rounded-full bg-gray-700 max-w-[80px] overflow-hidden">
          <div className="h-full rounded-full bg-amber-500" style={{ width: `${((v - 15) / 15) * 100}%` }} />
        </div>
      </div>
    ),
  },
  {
    key: 'light_level',
    label: 'Освещённость',
    render: (v) => (
      <div className="flex items-center gap-2">
        <span className="text-white">{v.toFixed(0)}%</span>
        <div className="flex-1 h-1.5 rounded-full bg-gray-700 max-w-[80px] overflow-hidden">
          <div className="h-full rounded-full bg-yellow-400" style={{ width: `${v}%` }} />
        </div>
      </div>
    ),
  },
  {
    key: 'tv_on',
    label: 'Телевизор',
    render: (v) => (
      <span className={v ? 'text-sky-400' : 'text-gray-500'}>
        {v ? '🟢 Включён' : '🔴 Выключен'}
      </span>
    ),
  },
  {
    key: 'minutes_idle',
    label: 'Минут без движения',
    render: (v) => (
      <div className="flex items-center gap-2">
        <span className="text-white">{v}</span>
        {v === 0 && <span className="text-xs text-green-400">(движение активно)</span>}
        {v > 60 && <span className="text-xs text-amber-400">(возможно, никого нет)</span>}
      </div>
    ),
  },
]

interface FeatureVectorTableProps {
  vector: FeatureVector
}

export function FeatureVectorTable({ vector }: FeatureVectorTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-700">
      <table className="min-w-full divide-y divide-gray-700 text-sm">
        <thead className="bg-gray-900/50">
          <tr>
            <th className="py-3 pl-4 pr-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Признак
            </th>
            <th className="py-3 px-4 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
              Значение
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700/50 bg-gray-800">
          {ROWS.map((row) => (
            <tr key={row.key} className="hover:bg-gray-700/30 transition-colors">
              <td className="py-3 pl-4 pr-3 font-mono text-xs text-gray-400">{row.label}</td>
              <td className="py-3 px-4">{row.render(vector[row.key])}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
