import type { ElementType } from 'react'

interface StatCardProps {
  icon: ElementType
  label: string
  value: string | number
  sub?: string
  iconColor?: string
  iconBg?: string
}

export function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  iconColor = 'text-sky-400',
  iconBg = 'bg-sky-900/50',
}: StatCardProps) {
  return (
    <div className="rounded-xl border border-gray-700 bg-gray-800 p-4 shadow-sm">
      <div className="mb-3 flex items-center gap-3">
        <div className={`${iconBg} rounded-xl p-2.5`}>
          <Icon aria-hidden="true" size={20} className={iconColor} />
        </div>
        <span className="text-sm font-medium text-gray-400">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {sub && <div className="mt-1 text-xs text-gray-400">{sub}</div>}
    </div>
  )
}
