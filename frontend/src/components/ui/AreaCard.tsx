import type { ElementType } from 'react'
import { Link } from 'react-router-dom'

interface AreaCardProps {
  activeCount: number
  deviceCount: number
  href?: string
  icon: ElementType
  name: string
}

export function AreaCard({
  activeCount,
  deviceCount,
  href,
  icon: Icon,
  name,
}: AreaCardProps) {
  const content = (
    <>
      <div className="flex flex-col items-center justify-center flex-1 gap-3">
        <div className="rounded-xl bg-sky-900/40 p-4 text-sky-400 transition-colors duration-150 group-hover:bg-sky-900/60">
          <Icon aria-hidden="true" size={28} />
        </div>
        <h3 className="text-sm font-semibold text-white text-center leading-tight">{name}</h3>
      </div>
      <div className="mt-auto flex items-center justify-between px-1">
        <span className="text-xs text-gray-400">{deviceCount} устр.</span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            activeCount > 0
              ? 'bg-sky-900/50 text-sky-400'
              : 'bg-gray-700 text-gray-500'
          }`}
        >
          {activeCount} акт.
        </span>
      </div>
    </>
  )

  const baseClass =
    'group flex flex-col aspect-square rounded-xl border border-gray-700 bg-gray-800 p-4 shadow-sm transition-colors duration-150 hover:bg-gray-700 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900'

  if (href) {
    return (
      <Link to={href} className={baseClass}>
        {content}
      </Link>
    )
  }

  return (
    <div className={baseClass}>
      {content}
    </div>
  )
}
