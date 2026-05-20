import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import type { WsStateChangedMessage } from '../types/home'

const WS_BASE = (import.meta.env.VITE_WS_URL as string | undefined) ?? 'ws://localhost:8000'

interface WSContextValue {
  connected: boolean
  lastMessage: WsStateChangedMessage | null
}

const WebSocketContext = createContext<WSContextValue>({ connected: false, lastMessage: null })

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WsStateChangedMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const shouldReconnectRef = useRef(true)

  useEffect(() => {
    shouldReconnectRef.current = true

    function connect() {
      const token = localStorage.getItem('token')

      if (!token || !shouldReconnectRef.current) {
        return
      }

      const ws = new WebSocket(`${WS_BASE}/ws?token=${token}`)
      wsRef.current = ws

      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        wsRef.current = null

        if (!shouldReconnectRef.current) {
          return
        }

        reconnectRef.current = setTimeout(connect, 5000)
      }
      ws.onerror = () => ws.close()
      ws.onmessage = (event) => {
        try {
          const parsedMessage = JSON.parse(event.data as string) as WsStateChangedMessage
          if (parsedMessage.type === 'state_changed' && typeof parsedMessage.entity_id === 'string') {
            setLastMessage(parsedMessage)
          }
        } catch {
          // Ignore malformed websocket payloads.
        }
      }
    }

    connect()

    return () => {
      shouldReconnectRef.current = false

      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current)
      }

      wsRef.current?.close()
    }
  }, [])

  return (
    <WebSocketContext.Provider value={{ connected, lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocketContext(): WSContextValue {
  return useContext(WebSocketContext)
}
