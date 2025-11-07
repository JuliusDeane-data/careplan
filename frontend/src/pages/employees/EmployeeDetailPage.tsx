/**
 * Employee detail page - profile view
 */

import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Mail, Phone, MapPin, Calendar, Briefcase, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import EmployeeStatusBadge from '@/components/employees/EmployeeStatusBadge'
import { useEmployeeProfile } from '@/hooks/useEmployees'
import { useAuth } from '@/contexts/AuthContext'
import { EmployeeRoleLabels } from '@/types/employee'
import { formatVacationDate } from '@/utils/dateUtils'

export default function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()

  const { data: employee, isLoading, error } = useEmployeeProfile(id ? parseInt(id) : undefined)

  const isAdmin = user?.role === 'ADMIN'
  const isManager = user?.role === 'MANAGER'
  const canEdit = isAdmin || isManager

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !employee) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-3xl mx-auto">
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-red-600 dark:text-red-400">
                <p className="font-medium">Failed to load employee</p>
                <p className="text-sm mt-1">
                  {error instanceof Error ? error.message : 'Employee not found'}
                </p>
                <Button className="mt-4" onClick={() => navigate('/employees')}>
                  Back to Directory
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/employees')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">Employee Profile</h1>
            <p className="text-muted-foreground">View employee information</p>
          </div>
          {canEdit && (
            <Button onClick={() => navigate(`/employees/${employee.id}/edit`)}>
              Edit Profile
            </Button>
          )}
        </div>

        {/* Profile Header */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start gap-6">
              {/* Avatar */}
              <div className="flex-shrink-0">
                {employee.profile_photo ? (
                  <img
                    src={employee.profile_photo}
                    alt={employee.full_name}
                    className="w-24 h-24 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-2xl">
                    {getInitials(employee.full_name)}
                  </div>
                )}
              </div>

              {/* Header Info */}
              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">{employee.full_name}</h2>
                    <p className="text-lg text-muted-foreground">
                      {EmployeeRoleLabels[employee.role]}
                    </p>
                  </div>
                  <EmployeeStatusBadge status={employee.employment_status} />
                </div>
                <div className="mt-4 flex flex-wrap gap-4">
                  <div className="text-sm text-muted-foreground">
                    <strong>Employee ID:</strong> {employee.employee_id}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <strong>Hired:</strong> {formatVacationDate(employee.hire_date)}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Two Column Layout */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
              <CardDescription>How to reach this employee</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Email</p>
                  <p className="text-sm text-muted-foreground">{employee.email}</p>
                </div>
              </div>
              {employee.phone && (
                <div className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">{employee.phone}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3">
                <MapPin className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Primary Location</p>
                  <p className="text-sm text-muted-foreground">
                    {employee.primary_location.name}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Employment Information */}
          <Card>
            <CardHeader>
              <CardTitle>Employment Details</CardTitle>
              <CardDescription>Job information and history</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Briefcase className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Role</p>
                  <p className="text-sm text-muted-foreground">
                    {EmployeeRoleLabels[employee.role]}
                  </p>
                </div>
              </div>
              {employee.department && (
                <div className="flex items-center gap-3">
                  <Briefcase className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Department</p>
                    <p className="text-sm text-muted-foreground">{employee.department}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Hire Date</p>
                  <p className="text-sm text-muted-foreground">
                    {formatVacationDate(employee.hire_date)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Status</p>
                  <p className="text-sm text-muted-foreground">
                    {employee.employment_status}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Vacation Balance */}
          <Card>
            <CardHeader>
              <CardTitle>Vacation Balance</CardTitle>
              <CardDescription>Current vacation day allocation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {employee.remaining_vacation_days}
                  </p>
                  <p className="text-sm text-muted-foreground">Remaining</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-muted-foreground">
                    {employee.annual_vacation_days}
                  </p>
                  <p className="text-sm text-muted-foreground">Annual Total</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Locations */}
          {employee.secondary_locations && employee.secondary_locations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Locations</CardTitle>
                <CardDescription>Assigned work locations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div>
                  <p className="text-sm font-medium">Primary</p>
                  <p className="text-sm text-muted-foreground">
                    {employee.primary_location.name}
                  </p>
                </div>
                {employee.secondary_locations.length > 0 && (
                  <div>
                    <p className="text-sm font-medium">Secondary</p>
                    <ul className="text-sm text-muted-foreground">
                      {employee.secondary_locations.map((location) => (
                        <li key={location.id}>{location.name}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
