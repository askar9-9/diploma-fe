import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { afterEach, beforeEach, vi } from 'vitest'
import { useWebSocket } from '../hooks/useWebSocket'
import { WebSocketProvider } from '../context/WebSocketContext'

class MockWebSocket {
  static instances: MockWebSocket[] = []

  onclose: (() => void) | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onopen: (() => void) | null = null
  url: string

  constructor(url: string) {
    this.url = url
    MockWebSocket.instances.push(this)
  }

  close() {
    this.onclose?.()
  }
}

describe('useWebSocket', () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem('token', 'ws-token')
    MockWebSocket.instances = []
    vi.stubGlobal('WebSocket', MockWebSocket)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('connects with token in the websocket URL', async () => {
    const wrapper = ({ children }: { children: ReactNode }) => (
      <WebSocketProvider>{children}</WebSocketProvider>
    )
    const { result } = renderHook(() => useWebSocket(), { wrapper })

    expect(MockWebSocket.instances).toHaveLength(1)
    expect(MockWebSocket.instances[0]?.url).toBe('ws://localhost:8000/ws?token=ws-token')

    MockWebSocket.instances[0]?.onopen?.()

    await waitFor(() => expect(result.current.connected).toBe(true))
  })
})
