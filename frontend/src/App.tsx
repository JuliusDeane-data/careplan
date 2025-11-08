import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider } from '@/contexts/AuthContext'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/LoginPage'
import ProfilePage from '@/pages/ProfilePage'
import DashboardPage from '@/pages/DashboardPage'
import VacationListPage from '@/pages/vacation/VacationListPage'
import VacationRequestPage from '@/pages/vacation/VacationRequestPage'
import EmployeeListPage from '@/pages/employees/EmployeeListPage'
import EmployeeDetailPage from '@/pages/employees/EmployeeDetailPage'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
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
            <Route
              path="/employees"
              element={
                <ProtectedRoute>
                  <EmployeeListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employees/:id"
              element={
                <ProtectedRoute>
                  <EmployeeDetailPage />
                </ProtectedRoute>
              }
            />
          </Routes>
          <Toaster position="top-right" richColors closeButton />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
