import { useCallback, useEffect, useRef, useState } from 'react'

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
const RECONNECT_INTERVAL = 5000

export interface WSMessage {
  type: 'device_state' | 'scene_activated' | 'ml_decision' | 'pattern_suggested'
  payload: Record<string, unknown>
}

export function useWebSocket() {
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const shouldReconnectRef = useRef(true)
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)

  const connect = useCallback(() => {
    const token = localStorage.getItem('token')

    if (!token || !shouldReconnectRef.current) {
      return
    }

    socketRef.current = new WebSocket(`${WS_BASE}/ws?token=${token}`)

    socketRef.current.onopen = () => {
      setConnected(true)
    }

    socketRef.current.onclose = () => {
      setConnected(false)

      if (!shouldReconnectRef.current) {
        return
      }

      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect()
      }, RECONNECT_INTERVAL)
    }

    socketRef.current.onmessage = (event) => {
      try {
        setLastMessage(JSON.parse(event.data) as WSMessage)
      } catch {
        // Ignore malformed payloads from the socket.
      }
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      shouldReconnectRef.current = false

      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current)
      }

      socketRef.current?.close()
    }
  }, [connect])

  return { connected, lastMessage }
}
