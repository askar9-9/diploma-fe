import { User, Wifi, WifiOff } from 'lucide-react'

export default function TopBar({ connected }: { connected: boolean }) {
  return (
    <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center justify-between border-b border-gray-800 bg-gray-900/95 px-4 backdrop-blur sm:px-6">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-white">HomeIQ</span>
        <span aria-hidden="true" className="mx-1 text-gray-700">·</span>
        <span className="hidden text-sm text-gray-500 sm:inline">Умный дом</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-sm" role="status" aria-live="polite">
          {connected
            ? <Wifi aria-hidden="true" size={14} className="text-green-500" />
            : <WifiOff aria-hidden="true" size={14} className="text-red-500" />}
          <span className={connected ? 'text-green-400 text-xs' : 'text-red-400 text-xs'}>
            {connected ? 'Подключён' : 'Отключён'}
          </span>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-gray-800 border border-gray-700 px-3 py-1.5">
          <User aria-hidden="true" size={13} className="text-gray-400" />
          <span className="text-sm font-medium text-gray-300">admin</span>
        </div>
      </div>
    </header>
  )
}
