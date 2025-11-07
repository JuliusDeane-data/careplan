import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, CalendarDays, Loader2 } from 'lucide-react'
import type { VacationStatus } from '@/types/vacation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useMyVacationRequests, useVacationBalance } from '@/hooks/useVacation'
import VacationCard from '@/components/vacation/VacationCard'

type FilterTab = 'ALL' | VacationStatus

export default function VacationListPage() {
  const navigate = useNavigate()
  const [activeFilter, setActiveFilter] = useState<FilterTab>('ALL')

  const { data: balance, isLoading: balanceLoading } = useVacationBalance()
  const { data: requests, isLoading: requestsLoading, error } = useMyVacationRequests()

  const filteredRequests = requests?.filter((request) => {
    if (activeFilter === 'ALL') return true
    return request.status === activeFilter
  })

  const getFilterCount = (status: FilterTab) => {
    if (!requests) return 0
    if (status === 'ALL') return requests.length
    return requests.filter((r) => r.status === status).length
  }

  const filters: { label: string; value: FilterTab }[] = [
    { label: 'All', value: 'ALL' },
    { label: 'Pending', value: 'PENDING' },
    { label: 'Approved', value: 'APPROVED' },
    { label: 'Denied', value: 'DENIED' },
    { label: 'Cancelled', value: 'CANCELLED' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <CalendarDays className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              My Vacation Requests
            </h1>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
            <Button onClick={() => navigate('/vacation/new')}>
              <Plus className="h-4 w-4 mr-2" />
              Request Vacation
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Balance Card */}
          {balanceLoading ? (
            <Card>
              <CardContent className="flex justify-center items-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </CardContent>
            </Card>
          ) : balance ? (
            <Card>
              <CardHeader>
                <CardTitle>Vacation Balance</CardTitle>
                <CardDescription>Your current vacation day allocation</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                  <div>
                    <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                      {balance.total_days}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">Total Days</p>
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                      {balance.remaining_days}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">Available</p>
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-gray-600 dark:text-gray-400">
                      {balance.used_days}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">Used</p>
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                      {balance.pending_days}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">Pending</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : null}

          {/* Filter Tabs */}
          <div className="flex gap-2 flex-wrap">
            {filters.map((filter) => {
              const count = getFilterCount(filter.value)
              const isActive = activeFilter === filter.value
              return (
                <Button
                  key={filter.value}
                  variant={isActive ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter(filter.value)}
                  className="relative"
                >
                  {filter.label}
                  <span
                    className={`ml-2 px-1.5 py-0.5 text-xs rounded-full ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {count}
                  </span>
                </Button>
              )
            })}
          </div>

          {/* Requests List */}
          {requestsLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <Card>
              <CardContent className="py-8">
                <div className="text-center text-red-600 dark:text-red-400">
                  <p className="font-medium">Failed to load vacation requests</p>
                  <p className="text-sm mt-1">
                    {error instanceof Error ? error.message : 'An error occurred'}
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : filteredRequests && filteredRequests.length > 0 ? (
            <div className="space-y-4">
              {filteredRequests.map((request) => (
                <VacationCard key={request.id} request={request} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <CalendarDays className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium text-muted-foreground mb-2">
                    {activeFilter === 'ALL'
                      ? 'No vacation requests yet'
                      : `No ${activeFilter.toLowerCase()} requests`}
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    Get started by requesting your first vacation
                  </p>
                  <Button onClick={() => navigate('/vacation/new')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Request Vacation
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
