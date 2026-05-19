import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../App'

vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({ connected: true, lastMessage: null }),
}))

describe('App', () => {
  beforeEach(() => {
    localStorage.clear()
    window.history.pushState({}, '', '/')
  })

  it('redirects to login when user is not authenticated', () => {
    render(<App />)

    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
  })

  it('renders dashboard layout when user is authenticated', () => {
    localStorage.setItem('token', 'token-123')

    render(<App />)

    expect(screen.getAllByText('Dashboard')).toHaveLength(2)
    expect(screen.getByText('Connected')).toBeInTheDocument()
    expect(screen.getByText('Devices')).toBeInTheDocument()
  })
})
