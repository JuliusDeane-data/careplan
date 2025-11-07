/**
 * Dashboard module type definitions
 */

// Dashboard Statistics
export interface DashboardStats {
  // Personal stats (all users)
  personal: {
    vacation_balance: {
      total: number
      remaining: number
      used: number
      pending: number
    }
    upcoming_vacations: number
    pending_requests: number
    last_login: string
  }

  // Team stats (managers only)
  team?: {
    total_members: number
    on_vacation_today: number
    pending_approvals: number
    vacation_utilization: number // percentage
    coverage_gaps: number
  }

  // System stats (admins only)
  system?: {
    total_employees: number
    active_employees: number
    total_locations: number
    vacation_requests_this_month: number
    system_health: 'healthy' | 'warning' | 'critical'
  }
}

// Activity Item
export interface Activity {
  id: number
  type: ActivityType
  title: string
  description: string
  actor: {
    id: number
    name: string
    avatar?: string
  }
  target?: {
    type: 'employee' | 'vacation' | 'location' | 'system'
    id: number
    name: string
  }
  timestamp: string
  is_read: boolean
  metadata?: Record<string, any>
}

export type ActivityType =
  | 'vacation_requested'
  | 'vacation_approved'
  | 'vacation_denied'
  | 'vacation_cancelled'
  | 'employee_created'
  | 'employee_updated'
  | 'employee_deleted'
  | 'location_created'
  | 'location_updated'
  | 'system_notification'
  | 'user_login'

// Upcoming Event
export interface UpcomingEvent {
  id: number
  type: 'vacation' | 'holiday' | 'meeting'
  title: string
  start_date: string
  end_date: string
  all_day: boolean
  employee?: {
    id: number
    name: string
    avatar?: string
  }
  location?: string
  status: 'pending' | 'approved' | 'confirmed'
}

// Activity type labels
export const ActivityTypeLabels: Record<ActivityType, string> = {
  vacation_requested: 'Vacation Requested',
  vacation_approved: 'Vacation Approved',
  vacation_denied: 'Vacation Denied',
  vacation_cancelled: 'Vacation Cancelled',
  employee_created: 'Employee Added',
  employee_updated: 'Employee Updated',
  employee_deleted: 'Employee Removed',
  location_created: 'Location Added',
  location_updated: 'Location Updated',
  system_notification: 'System Notification',
  user_login: 'User Login',
}
