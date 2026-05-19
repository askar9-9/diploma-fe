import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { authStore } from '../../store/authStore'

interface PrivateRouteProps {
  children: ReactNode
}

export default function PrivateRoute({ children }: PrivateRouteProps) {
  if (!authStore.isAuthenticated()) {
    return <Navigate replace to="/login" />
  }

  return <>{children}</>
}
