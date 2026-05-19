import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, vi } from 'vitest'
import { useWebSocket } from '../hooks/useWebSocket'

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
    const { result } = renderHook(() => useWebSocket())

    expect(MockWebSocket.instances).toHaveLength(1)
    expect(MockWebSocket.instances[0]?.url).toBe('ws://localhost:8000/ws?token=ws-token')

    MockWebSocket.instances[0]?.onopen?.()

    await waitFor(() => expect(result.current.connected).toBe(true))
  })
})
