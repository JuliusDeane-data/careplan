import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider } from '@/contexts/AuthContext'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import VacationListPage from '@/pages/vacation/VacationListPage'
import VacationRequestPage from '@/pages/vacation/VacationRequestPage'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/vacation"
              element={
                <ProtectedRoute>
                  <VacationListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/vacation/new"
              element={
                <ProtectedRoute>
                  <VacationRequestPage />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          <Toaster position="top-right" richColors closeButton />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
