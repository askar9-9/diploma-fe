import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import LoginPage from '../pages/LoginPage'
import * as client from '../api/client'

describe('LoginPage', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('renders form fields', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )
    expect(screen.getByLabelText('Логин')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
  })

  it('shows error on failed login', async () => {
    vi.spyOn(client.authApi, 'login').mockRejectedValue(new Error('401'))

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'wrong' } })
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button'))
    await waitFor(() => expect(screen.getByText(/Неверный/)).toBeInTheDocument())
  })
})
