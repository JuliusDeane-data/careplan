/**
 * Employee list page - main directory view
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, Loader2, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import EmployeeCard from '@/components/employees/EmployeeCard'
import { useEmployees } from '@/hooks/useEmployees'
import { useAuth } from '@/contexts/AuthContext'
import type { EmployeeFilters } from '@/types/employee'

export default function EmployeeListPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState<EmployeeFilters>({
    page: 1,
    page_size: 20,
  })

  // Apply search to filters
  const activeFilters = {
    ...filters,
    search: search || undefined,
  }

  const { data, isLoading, error } = useEmployees(activeFilters)

  const isAdmin = user?.role === 'ADMIN'

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <Users className="h-6 w-6 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Employee Directory
                </h1>
                <p className="text-sm text-muted-foreground">
                  {data?.count ? `${data.count} employees` : 'Browse employees'}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </Button>
              {isAdmin && (
                <Button onClick={() => navigate('/employees/new')}>
                  Add Employee
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Search Bar */}
          <Card>
            <CardContent className="pt-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search employees by name, email, or ID..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </CardContent>
          </Card>

          {/* Employee Grid */}
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <Card>
              <CardContent className="py-8">
                <div className="text-center text-red-600 dark:text-red-400">
                  <p className="font-medium">Failed to load employees</p>
                  <p className="text-sm mt-1">
                    {error instanceof Error ? error.message : 'An error occurred'}
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : data?.results && data.results.length > 0 ? (
            <>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {data.results.map((employee) => (
                  <EmployeeCard key={employee.id} employee={employee} />
                ))}
              </div>

              {/* Pagination */}
              {data.count > 20 && (
                <div className="flex justify-center gap-2 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setFilters({ ...filters, page: (filters.page || 1) - 1 })}
                    disabled={!data.previous || filters.page === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setFilters({ ...filters, page: (filters.page || 1) + 1 })}
                    disabled={!data.next}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium text-muted-foreground mb-2">
                    No employees found
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    {search ? 'Try adjusting your search' : 'Get started by adding an employee'}
                  </p>
                  {isAdmin && !search && (
                    <Button onClick={() => navigate('/employees/new')}>
                      Add First Employee
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
