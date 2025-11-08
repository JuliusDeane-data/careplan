/**
 * ProfilePage - User profile showing personal information and shifts
 * Displays user's own information without sensitive data
 */

import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Mail,
  Phone,
  MapPin,
  Calendar,
  Briefcase,
  Clock,
  Award,
  LogOut,
  Edit,
  ArrowLeft,
  CalendarDays,
  Building2,
} from 'lucide-react'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) {
    navigate('/login')
    return null
  }

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  // Format date helper
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  // Calculate years of service
  const getYearsOfService = () => {
    if (!user.hire_date) return 'N/A'
    const years = new Date().getFullYear() - new Date(user.hire_date).getFullYear()
    return years === 1 ? '1 year' : `${years} years`
  }

  // Get employment status badge style
  const getStatusBadge = () => {
    const styles = {
      ACTIVE: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      ON_LEAVE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      TERMINATED: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    }
    return styles[user.employment_status as keyof typeof styles] || styles.ACTIVE
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/dashboard')}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                My Profile
              </h1>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled>
                <Edit className="w-4 h-4 mr-2" />
                Edit Profile
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header Card */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-start gap-6">
              {/* Avatar */}
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
                {user.first_name?.[0]}
                {user.last_name?.[0]}
              </div>

              {/* Basic Info */}
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                      {user.first_name} {user.last_name}
                    </h2>
                    <p className="text-lg text-gray-600 dark:text-gray-400 mt-1">
                      {user.job_title || 'Employee'}
                    </p>
                  </div>
                  <Badge className={getStatusBadge()}>
                    {user.employment_status?.replace('_', ' ')}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Employee ID
                    </p>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {user.employee_id}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Department
                    </p>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {user.department || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Role</p>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {user.role}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Years of Service
                    </p>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {getYearsOfService()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5" />
                Contact Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                  <p className="font-medium">{user.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Phone</p>
                  <p className="font-medium">{user.phone || 'Not provided'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Primary Location
                  </p>
                  <p className="font-medium">
                    {user.primary_location?.name || 'Not assigned'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Employment Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Employment Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Hire Date
                  </p>
                  <p className="font-medium">{formatDate(user.hire_date)}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Employment Type
                  </p>
                  <p className="font-medium">
                    {user.employment_type?.replace('_', ' ') || 'N/A'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Building2 className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Contract Hours
                  </p>
                  <p className="font-medium">
                    {user.contract_hours_per_week
                      ? `${user.contract_hours_per_week} hours/week`
                      : 'N/A'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Vacation Balance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CalendarDays className="w-5 h-5" />
                Vacation Balance
              </CardTitle>
              <CardDescription>Your annual vacation allowance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                    {user.remaining_vacation_days}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Days Remaining
                  </p>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-3xl font-bold text-gray-600 dark:text-gray-400">
                    {user.annual_vacation_days}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Total Annual
                  </p>
                </div>
              </div>
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Used</span>
                  <span className="font-medium">
                    {(user.annual_vacation_days || 0) -
                      (user.remaining_vacation_days || 0)}{' '}
                    days
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${
                        ((user.annual_vacation_days || 0) -
                          (user.remaining_vacation_days || 0)) /
                        (user.annual_vacation_days || 1) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>
              <div className="mt-4">
                <Button
                  className="w-full"
                  onClick={() => navigate('/vacation')}
                >
                  View Vacation Requests
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Upcoming Shifts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                My Shifts
              </CardTitle>
              <CardDescription>Your upcoming work schedule</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                  Shift scheduling coming soon
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-500">
                  This feature is currently under development. You'll be able to
                  view and manage your shifts here once it's available.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Qualifications */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                Qualifications & Certifications
              </CardTitle>
              <CardDescription>
                Your professional certifications and training
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Award className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                  No qualifications recorded
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-500">
                  Contact your manager or HR to update your qualifications and
                  certifications.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Emergency Contact (if provided) */}
        {user.emergency_contact_name && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Phone className="w-5 h-5" />
                Emergency Contact
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Name</p>
                  <p className="font-medium">{user.emergency_contact_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Phone</p>
                  <p className="font-medium">
                    {user.emergency_contact_phone || 'Not provided'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}
