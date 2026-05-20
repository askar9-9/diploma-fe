import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import PrivateRoute from './components/routing/PrivateRoute'
import { HomeDataProvider } from './context/HomeDataContext'
import LoginPage from './pages/LoginPage'

const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const AreasPage = lazy(() => import('./pages/AreasPage'))
const AreaDetailPage = lazy(() => import('./pages/AreaDetailPage'))
const DevicesPage = lazy(() => import('./pages/DevicesPage'))
const EnergyPage = lazy(() => import('./pages/EnergyPage'))
const AutomationPage = lazy(() => import('./pages/AutomationPage'))

function PageFallback() {
  return (
    <div className="flex items-center justify-center py-20">
      <span className="h-8 w-8 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" aria-label="Загрузка страницы..." />
    </div>
  )
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
              <HomeDataProvider>
                <AppLayout />
              </HomeDataProvider>
            </PrivateRoute>
          }
        >
          <Route
            index
            element={
              <Suspense fallback={<PageFallback />}>
                <DashboardPage />
              </Suspense>
            }
          />
          <Route
            path="areas"
            element={
              <Suspense fallback={<PageFallback />}>
                <AreasPage />
              </Suspense>
            }
          />
          <Route
            path="areas/:areaId"
            element={
              <Suspense fallback={<PageFallback />}>
                <AreaDetailPage />
              </Suspense>
            }
          />
          <Route
            path="devices"
            element={
              <Suspense fallback={<PageFallback />}>
                <DevicesPage />
              </Suspense>
            }
          />
          <Route
            path="energy"
            element={
              <Suspense fallback={<PageFallback />}>
                <EnergyPage />
              </Suspense>
            }
          />
          <Route
            path="automation"
            element={
              <Suspense fallback={<PageFallback />}>
                <AutomationPage />
              </Suspense>
            }
          />
          <Route path="*" element={<Navigate replace to="/" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
