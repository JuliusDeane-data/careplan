// User & Authentication Types
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  employee_id: string
  role: 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
  employment_status: 'ACTIVE' | 'ON_LEAVE' | 'TERMINATED'
  employment_type?: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'TEMPORARY'
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  remaining_vacation_days: number
  annual_vacation_days: number
  phone?: string
  date_of_birth?: string
  address?: string
  city?: string
  state?: string
  postal_code?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  hire_date?: string
  termination_date?: string
  job_title?: string
  department?: string
  contract_hours_per_week?: number
  primary_location?: Location
  additional_locations?: Location[]
  qualifications?: Qualification[]
  supervisor?: User
  created_at?: string
  updated_at?: string
}

export interface LoginCredentials {
  email?: string
  username?: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface TokenRefreshResponse {
  access: string
}

// Location Types
export interface Location {
  id: number
  name: string
  code: string
  address?: string
  city?: string
  state?: string
  postal_code?: string
  phone?: string
  email?: string
  manager?: User
  manager_name?: string
  employee_count?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// Qualification Types
export interface Qualification {
  id: number
  name: string
  description?: string
  is_required: boolean
}

// Vacation Request Types
export type VacationRequestStatus = 'PENDING' | 'APPROVED' | 'DENIED' | 'CANCELLED'
export type VacationRequestType = 'VACATION' | 'SICK' | 'PERSONAL' | 'UNPAID'

export interface VacationRequest {
  id: number
  employee: User
  request_type: VacationRequestType
  start_date: string
  end_date: string
  vacation_days: number
  status: VacationRequestStatus
  reason?: string
  denial_reason?: string
  cancellation_reason?: string
  approved_by?: User
  denied_by?: User
  cancelled_by?: User
  approved_at?: string
  denied_at?: string
  cancelled_at?: string
  created_at: string
  updated_at: string
}

export interface CreateVacationRequest {
  request_type: VacationRequestType
  start_date: string
  end_date: string
  reason?: string
}

export interface VacationBalance {
  user_id: number
  employee_id: string
  name: string
  annual_vacation_days: number
  remaining_vacation_days: number
  used_vacation_days: number
  pending_days: number
  available_days: number
}

// Public Holiday Types
export interface PublicHoliday {
  id: number
  name: string
  date: string
  location?: Location
  is_nationwide: boolean
  is_recurring: boolean
  description?: string
}

// Notification Types
export type NotificationType =
  | 'VACATION_REQUEST_SUBMITTED'
  | 'VACATION_REQUEST_APPROVED'
  | 'VACATION_REQUEST_DENIED'
  | 'VACATION_REQUEST_CANCELLED'
  | 'EMPLOYEE_TERMINATED'
  | 'LOCATION_CHANGED'
  | 'SYSTEM_ANNOUNCEMENT'

export interface Notification {
  id: number
  recipient: User
  notification_type: NotificationType
  title: string
  message: string
  is_read: boolean
  related_user?: User
  related_vacation_request?: VacationRequest
  created_at: string
}

// Dashboard Stats Types
export interface DashboardStats {
  total_employees: number
  active_employees: number
  on_leave_employees: number
  pending_vacation_requests: number
  approved_vacation_requests: number
  total_locations: number
  role_distribution: {
    managers: number
    employees: number
  }
}

// API Response Types
export interface ApiError {
  error: string
  status_code?: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
