import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import PrivateRoute from '../components/routing/PrivateRoute'

describe('PrivateRoute', () => {
  beforeEach(() => localStorage.clear())

  it('redirects to login when token is missing', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route
            path="/"
            element={
              <PrivateRoute>
                <div>Private Content</div>
              </PrivateRoute>
            }
          />
          <Route path="/login" element={<div>Login Screen</div>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText('Login Screen')).toBeInTheDocument()
    expect(screen.queryByText('Private Content')).not.toBeInTheDocument()
  })
})
