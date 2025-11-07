/**
 * QuickActions Component
 * Role-based quick action buttons for the dashboard
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import {
  Calendar,
  Users,
  CalendarClock,
  UserPlus,
  FileText,
  Settings,
} from 'lucide-react'

interface QuickAction {
  label: string
  icon: typeof Calendar
  path: string
  roles: string[]
  description: string
}

const QUICK_ACTIONS: QuickAction[] = [
  {
    label: 'Request Vacation',
    icon: Calendar,
    path: '/vacation/new',
    roles: ['EMPLOYEE', 'MANAGER', 'ADMIN'],
    description: 'Submit a new vacation request',
  },
  {
    label: 'My Vacations',
    icon: CalendarClock,
    path: '/vacation',
    roles: ['EMPLOYEE', 'MANAGER', 'ADMIN'],
    description: 'View your vacation requests',
  },
  {
    label: 'Team Vacations',
    icon: Users,
    path: '/vacation?view=team',
    roles: ['MANAGER', 'ADMIN'],
    description: 'View and approve team requests',
  },
  {
    label: 'Employee Directory',
    icon: Users,
    path: '/employees',
    roles: ['MANAGER', 'ADMIN'],
    description: 'Browse employee directory',
  },
  {
    label: 'Add Employee',
    icon: UserPlus,
    path: '/employees/new',
    roles: ['ADMIN'],
    description: 'Register a new employee',
  },
  {
    label: 'Reports',
    icon: FileText,
    path: '/reports',
    roles: ['MANAGER', 'ADMIN'],
    description: 'View reports and analytics',
  },
  {
    label: 'Settings',
    icon: Settings,
    path: '/settings',
    roles: ['ADMIN'],
    description: 'System settings',
  },
]

export default function QuickActions() {
  const navigate = useNavigate()
  const { user } = useAuth()

  // Filter actions based on user role
  const availableActions = QUICK_ACTIONS.filter((action) =>
    action.roles.includes(user?.role || 'EMPLOYEE')
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2">
          {availableActions.map((action) => {
            const Icon = action.icon
            return (
              <Button
                key={action.path}
                variant="outline"
                className="justify-start h-auto py-3"
                onClick={() => navigate(action.path)}
              >
                <Icon className="w-4 h-4 mr-3 flex-shrink-0" />
                <div className="text-left flex-1">
                  <div className="font-medium">{action.label}</div>
                  <div className="text-xs text-muted-foreground font-normal">
                    {action.description}
                  </div>
                </div>
              </Button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
