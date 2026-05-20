import { Brain, Cpu, Home, LayoutDashboard, MapPin, Settings, User, Zap } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const NAV = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/devices', label: 'Устройства', icon: Cpu },
  { path: '/areas', label: 'Комнаты', icon: MapPin },
  { path: '/energy', label: 'Энергия', icon: Zap },
  { path: '/automation', label: 'Автоматизация', icon: Brain },
]

export default function Sidebar({ connected }: { connected: boolean }) {
  return (
    <aside className="w-full shrink-0 border-b border-white/5 bg-slate-950 text-white lg:flex lg:w-56 lg:flex-col lg:border-b-0 lg:border-r">
      <div className="flex h-16 items-center gap-3 px-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-sky-500 shadow-lg shadow-sky-900/40">
          <Home aria-hidden="true" size={16} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">HomeIQ</p>
          <p className="text-[11px] text-slate-400">Умный дом</p>
        </div>
      </div>

      <nav
        aria-label="Основная навигация"
        className="flex gap-1 overflow-x-auto px-2 pb-2 lg:flex-1 lg:flex-col lg:overflow-visible lg:px-3 lg:pb-3"
      >
        {NAV.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `inline-flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-150 focus:ring-2 focus:ring-sky-500 focus:ring-offset-1 focus:ring-offset-slate-950 ${
                  isActive
                    ? 'bg-sky-500 text-white'
                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    aria-hidden="true"
                    size={16}
                    className={isActive ? 'text-white' : 'text-slate-400'}
                  />
                  {item.label}
                </>
              )}
            </NavLink>
          )
        })}
      </nav>

      <div className="border-t border-white/5 px-3 py-3 space-y-1">
        <NavLink
          to="/settings"
          className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-slate-400 transition-colors hover:bg-white/5 hover:text-white focus:ring-2 focus:ring-sky-500 focus:ring-offset-1 focus:ring-offset-slate-950"
        >
          <Settings aria-hidden="true" size={15} />
          <span>Настройки</span>
        </NavLink>

        <div className="flex items-center gap-3 px-3 py-2">
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sky-900/60 text-sky-400">
            <User aria-hidden="true" size={14} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">admin</p>
            <div
              className="flex items-center gap-1.5 mt-0.5"
              role="status"
              aria-live="polite"
            >
              <span
                aria-hidden="true"
                className={`h-1.5 w-1.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}
              />
              <span className="text-[11px] text-slate-500">
                {connected ? 'Подключён' : 'Переподключение...'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
