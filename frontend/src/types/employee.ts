/**
 * Employee module type definitions
 */

// Employee Role
export type EmployeeRole =
  | 'CARE_WORKER'
  | 'NURSE'
  | 'MANAGER'
  | 'ADMIN'
  | 'COORDINATOR'

// Employment Status
export type EmploymentStatus = 'ACTIVE' | 'ON_LEAVE' | 'TERMINATED' | 'PROBATION'

// Location Summary
export interface LocationSummary {
  id: number
  name: string
  address: string
  type: string
}

// Employee Summary (for list view)
export interface EmployeeSummary {
  id: number
  employee_id: string
  full_name: string
  email: string
  phone?: string
  role: EmployeeRole
  employment_status: EmploymentStatus
  primary_location: LocationSummary
  profile_photo?: string
  hire_date: string
}

// Address
export interface Address {
  street1: string
  street2?: string
  city: string
  state: string
  postal_code: string
  country: string
}

// Qualification
export interface Qualification {
  id: number
  name: string
  issuing_organization: string
  issue_date: string
  expiry_date?: string
  is_active: boolean
}

// Full Employee Profile
export interface Employee extends EmployeeSummary {
  first_name: string
  last_name: string
  middle_name?: string
  date_of_birth?: string
  gender?: 'M' | 'F' | 'O' | 'N'
  address?: Address

  // Employment
  department?: string
  job_title?: string
  manager?: EmployeeSummary
  hourly_rate?: number
  salary?: number

  // Locations
  secondary_locations: LocationSummary[]

  // Vacation
  annual_vacation_days: number
  remaining_vacation_days: number
  sick_days_remaining: number

  // Qualifications
  qualifications: Qualification[]
  skills: string[]

  // Metadata
  created_at: string
  updated_at: string
  last_login?: string
}

// Employee Filters
export interface EmployeeFilters {
  search?: string
  role?: EmployeeRole[]
  location?: number[]
  employment_status?: EmploymentStatus[]
  department?: string[]
  page?: number
  page_size?: number
  ordering?: string
}

// Employee Create/Update
export interface EmployeeCreate {
  first_name: string
  last_name: string
  middle_name?: string
  email: string
  phone?: string
  role: EmployeeRole
  employment_status: EmploymentStatus
  primary_location: number
  secondary_locations?: number[]
  hire_date: string
  date_of_birth?: string
  address?: Address
  department?: string
  job_title?: string
  manager_id?: number
  annual_vacation_days?: number
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {
  id: number
}

// Role display labels
export const EmployeeRoleLabels: Record<EmployeeRole, string> = {
  CARE_WORKER: 'Care Worker',
  NURSE: 'Nurse',
  MANAGER: 'Manager',
  ADMIN: 'Administrator',
  COORDINATOR: 'Coordinator',
}

// Status display labels
export const EmploymentStatusLabels: Record<EmploymentStatus, string> = {
  ACTIVE: 'Active',
  ON_LEAVE: 'On Leave',
  TERMINATED: 'Terminated',
  PROBATION: 'Probation',
}
