import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import DevicesPage from './pages/DevicesPage'
import LoginPage from './pages/LoginPage'
import MLInsightsPage from './pages/MLInsightsPage'
import PatternsPage from './pages/PatternsPage'
import ScenariosPage from './pages/ScenariosPage'
import SimulationPage from './pages/SimulationPage'
import { authStore } from './store/authStore'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  return authStore.isAuthenticated() ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AppLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="devices" element={<DevicesPage />} />
          <Route path="scenarios" element={<ScenariosPage />} />
          <Route path="ml-insights" element={<MLInsightsPage />} />
          <Route path="patterns" element={<PatternsPage />} />
          <Route path="simulation" element={<SimulationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
