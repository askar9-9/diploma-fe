import { NavLink } from 'react-router-dom'

const NAV = [
  { path: '/', label: 'Dashboard', icon: '🏠' },
  { path: '/devices', label: 'Devices', icon: '💡' },
  { path: '/scenarios', label: 'Scenarios', icon: '🎭' },
  { path: '/ml-insights', label: 'ML Insights', icon: '🧠' },
  { path: '/patterns', label: 'Pattern Review', icon: '🔍' },
  { path: '/simulation', label: 'Simulation', icon: '⚡' },
]

export default function Sidebar({ connected }: { connected: boolean }) {
  return (
    <aside className="w-56 bg-gray-800 min-h-screen flex flex-col p-4">
      <h2 className="text-xl font-bold text-indigo-400 mb-8">HomeIQ</h2>
      <nav className="flex-1 space-y-1">
        {NAV.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${isActive ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
            }
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="flex items-center gap-2 text-xs text-gray-400 mt-4">
        <span
          className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`}
        />
        {connected ? 'Connected' : 'Disconnected'}
      </div>
    </aside>
  )
}
