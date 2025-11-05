// Vacation Request Types

export interface VacationRequest {
  id: number
  employee: EmployeeSummary
  start_date: string
  end_date: string
  total_days: number
  reason?: string
  status: VacationStatus
  created_at: string
  updated_at: string
  approved_by?: EmployeeSummary
  approved_at?: string
  denied_by?: EmployeeSummary
  denied_at?: string
  denial_reason?: string
  cancelled_at?: string
}

export type VacationStatus = 'PENDING' | 'APPROVED' | 'DENIED' | 'CANCELLED'

export interface EmployeeSummary {
  id: number
  full_name: string
  employee_id: string
  email?: string
}

export interface VacationBalance {
  total_days: number
  remaining_days: number
  used_days: number
  pending_days: number
}

export interface VacationRequestCreate {
  start_date: string
  end_date: string
  reason?: string
}

export interface VacationRequestUpdate {
  start_date?: string
  end_date?: string
  reason?: string
}

export interface VacationDenyRequest {
  reason: string
}

export interface VacationFilters {
  status?: VacationStatus
  start_date?: string
  end_date?: string
  employee?: number
  ordering?: string
  page?: number
  page_size?: number
}

// Helper types for status display
export const VacationStatusColors = {
  PENDING: 'warning',
  APPROVED: 'success',
  DENIED: 'destructive',
  CANCELLED: 'secondary',
} as const

export const VacationStatusLabels = {
  PENDING: 'Pending',
  APPROVED: 'Approved',
  DENIED: 'Denied',
  CANCELLED: 'Cancelled',
} as const
