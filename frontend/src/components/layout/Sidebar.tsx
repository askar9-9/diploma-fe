import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Cpu,
  PlayCircle,
  Brain,
  Search,
  Timer,
  Home,
  Wifi,
  WifiOff,
} from 'lucide-react'

const NAV = [
  { path: '/', label: 'Дашборд', icon: LayoutDashboard },
  { path: '/devices', label: 'Устройства', icon: Cpu },
  { path: '/scenarios', label: 'Сценарии', icon: PlayCircle },
  { path: '/ml-insights', label: 'ML Аналитика', icon: Brain },
  { path: '/patterns', label: 'Паттерны', icon: Search },
  { path: '/simulation', label: 'Симуляция', icon: Timer },
]

export default function Sidebar({ connected }: { connected: boolean }) {
  return (
    <aside className="w-60 bg-gray-800 min-h-screen flex flex-col p-4 border-r border-gray-700">
      <div className="flex items-center gap-2.5 mb-8">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shrink-0">
          <Home size={16} className="text-white" />
        </div>
        <h2 className="text-xl font-bold text-white">HomeIQ</h2>
      </div>
      <nav className="flex-1 space-y-1">
        {NAV.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={16} className={isActive ? 'text-white' : 'text-gray-400'} />
                  {item.label}
                </>
              )}
            </NavLink>
          )
        })}
      </nav>
      <div className="flex items-center gap-2 text-xs text-gray-500 mt-4 pt-4 border-t border-gray-700">
        {connected ? (
          <Wifi size={14} className="text-green-400" />
        ) : (
          <WifiOff size={14} className="text-red-400" />
        )}
        <span className={connected ? 'text-green-400' : 'text-red-400'}>
          {connected ? 'Подключено' : 'Отключено'}
        </span>
      </div>
    </aside>
  )
}
