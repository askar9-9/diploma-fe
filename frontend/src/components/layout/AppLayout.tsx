import { Outlet } from 'react-router-dom'
import { useWebSocket } from '../../hooks/useWebSocket'
import Sidebar from './Sidebar'

export default function AppLayout() {
  const { connected } = useWebSocket()

  return (
    <div className="flex min-h-screen">
      <Sidebar connected={connected} />
      <main className="flex-1 p-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
