import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'
import { useDashboardStats } from '@/hooks/useDashboard'
import StatsCard from '@/components/dashboard/StatsCard'
import ActivityFeed from '@/components/dashboard/ActivityFeed'
import QuickActions from '@/components/dashboard/QuickActions'
import UpcomingVacations from '@/components/dashboard/UpcomingVacations'
import {
  Calendar,
  CalendarCheck,
  CalendarClock,
  Users,
  UserCheck,
  Clock,
  Loader2,
} from 'lucide-react'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { data: stats, isLoading: statsLoading } = useDashboardStats()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const isManager = user?.role === 'MANAGER' || user?.role === 'ADMIN'
  const isAdmin = user?.role === 'ADMIN'

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            CarePlan Dashboard
          </h1>
          <div className="flex items-center gap-4">
            {isManager && (
              <Button
                onClick={() => navigate('/employees')}
                variant="outline"
              >
                <Users className="w-4 h-4 mr-2" />
                Employee Directory
              </Button>
            )}
            <Button onClick={handleLogout} variant="outline">
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Banner */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.first_name}!
          </h2>
          <p className="text-muted-foreground mt-1">
            Here's what's happening with your team today
          </p>
        </div>

        {/* Stats Cards */}
        {statsLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
            {/* Personal Stats */}
            <StatsCard
              title="Vacation Balance"
              value={stats?.personal.vacation_balance.remaining || 0}
              description={`of ${stats?.personal.vacation_balance.total || 0} days`}
              icon={Calendar}
              iconColor="text-blue-600"
              onClick={() => navigate('/vacation/new')}
            />
            <StatsCard
              title="Pending Requests"
              value={stats?.personal.pending_requests || 0}
              description="Awaiting approval"
              icon={Clock}
              iconColor="text-yellow-600"
              onClick={() => navigate('/vacation?status=PENDING')}
            />
            <StatsCard
              title="Upcoming Vacations"
              value={stats?.personal.upcoming_vacations || 0}
              description="Next 30 days"
              icon={CalendarCheck}
              iconColor="text-green-600"
              onClick={() => navigate('/vacation?status=APPROVED')}
            />
            <StatsCard
              title="Used Days"
              value={stats?.personal.vacation_balance.used || 0}
              description="This year"
              icon={CalendarClock}
              iconColor="text-purple-600"
            />
          </div>
        )}

        {/* Manager Stats */}
        {isManager && stats?.team && (
          <div className="grid gap-6 md:grid-cols-3 mb-8">
            <StatsCard
              title="Team Members"
              value={stats.team.total_members}
              description="Active employees"
              icon={Users}
              iconColor="text-blue-600"
              onClick={() => navigate('/employees')}
            />
            <StatsCard
              title="On Vacation Today"
              value={stats.team.on_vacation_today}
              description="Team members"
              icon={CalendarCheck}
              iconColor="text-orange-600"
            />
            <StatsCard
              title="Pending Approvals"
              value={stats.team.pending_approvals}
              description="Requires action"
              icon={Clock}
              iconColor="text-red-600"
              onClick={() => navigate('/vacation?view=team&status=PENDING')}
            />
          </div>
        )}

        {/* System Stats (Admin only) */}
        {isAdmin && stats?.system && (
          <div className="grid gap-6 md:grid-cols-2 mb-8">
            <StatsCard
              title="Total Employees"
              value={stats.system.total_employees}
              description="Organization-wide"
              icon={Users}
              iconColor="text-blue-600"
              onClick={() => navigate('/employees')}
            />
            <StatsCard
              title="Active Employees"
              value={stats.system.active_employees}
              description="Currently working"
              icon={UserCheck}
              iconColor="text-green-600"
              onClick={() => navigate('/employees?status=ACTIVE')}
            />
          </div>
        )}

        {/* Main Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Activity Feed */}
          <div className="lg:col-span-2 space-y-6">
            <ActivityFeed limit={10} showViewAll />
            <UpcomingVacations limit={5} days={30} />
          </div>

          {/* Right Column - Quick Actions */}
          <div>
            <QuickActions />
          </div>
        </div>

        {/* Profile Info Card */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Your Profile</CardTitle>
            <CardDescription>Employee information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Employee ID</p>
                <p className="text-lg font-semibold">{user?.employee_id}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Role</p>
                <p className="text-lg font-semibold">{user?.role}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="text-lg font-semibold">{user?.employment_status}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Location</p>
                <p className="text-lg font-semibold">{user?.primary_location?.name || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
