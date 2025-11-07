/**
 * Employee card component for list view
 */

import { useNavigate } from 'react-router-dom'
import { Mail, Phone, MapPin, Calendar } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import EmployeeStatusBadge from './EmployeeStatusBadge'
import { EmployeeRoleLabels } from '@/types/employee'
import { formatVacationDate } from '@/utils/dateUtils'
import type { EmployeeSummary } from '@/types/employee'

interface EmployeeCardProps {
  employee: EmployeeSummary
}

export default function EmployeeCard({ employee }: EmployeeCardProps) {
  const navigate = useNavigate()

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="flex-shrink-0">
            {employee.profile_photo ? (
              <img
                src={employee.profile_photo}
                alt={employee.full_name}
                className="w-16 h-16 rounded-full object-cover"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-lg">
                {getInitials(employee.full_name)}
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="min-w-0">
                <h3 className="text-lg font-semibold truncate">{employee.full_name}</h3>
                <p className="text-sm text-muted-foreground">
                  {EmployeeRoleLabels[employee.role]}
                </p>
              </div>
              <EmployeeStatusBadge status={employee.employment_status} />
            </div>

            {/* Details */}
            <div className="space-y-1.5 mb-4">
              {employee.email && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4 flex-shrink-0" />
                  <span className="truncate">{employee.email}</span>
                </div>
              )}
              {employee.phone && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Phone className="h-4 w-4 flex-shrink-0" />
                  <span>{employee.phone}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">{employee.primary_location.name}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4 flex-shrink-0" />
                <span>Hired: {formatVacationDate(employee.hire_date)}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={() => navigate(`/employees/${employee.id}`)}
                className="flex-1"
              >
                View Profile
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
