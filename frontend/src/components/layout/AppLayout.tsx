import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { useWebSocketContext } from '../../context/WebSocketContext'

export default function AppLayout() {
  const { connected } = useWebSocketContext()

  return (
    <div className="flex min-h-screen flex-col bg-gray-900 lg:flex-row">
      <Sidebar connected={connected} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar connected={connected} />
        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
