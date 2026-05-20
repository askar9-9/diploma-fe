import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import App from '../App'

describe('App', () => {
  beforeEach(() => {
    localStorage.clear()
    window.history.pushState({}, '', '/')
  })

  it('redirects to login when user is not authenticated', () => {
    render(<App />)

    expect(screen.getByLabelText('Логин')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
  })

  it('renders dashboard layout when user is authenticated', () => {
    localStorage.setItem('token', 'token-123')

    render(<App />)

    expect(screen.getAllByText('HomeIQ').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThan(0)
    expect(screen.getByText('Комнаты')).toBeInTheDocument()
    expect(screen.getByText('Устройства')).toBeInTheDocument()
    expect(screen.getByText('Энергия')).toBeInTheDocument()
  })
})
