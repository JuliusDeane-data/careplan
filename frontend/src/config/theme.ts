/**
 * Theme configuration for consistent styling across the application
 */

import type { VacationStatus } from '@/types/vacation'

export const VACATION_STATUS_STYLES: Record<
  VacationStatus,
  {
    badge: string
    label: string
    description: string
  }
> = {
  PENDING: {
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    label: 'Pending',
    description: 'Awaiting manager approval',
  },
  APPROVED: {
    badge: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    label: 'Approved',
    description: 'Approved by manager',
  },
  DENIED: {
    badge: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    label: 'Denied',
    description: 'Request was denied',
  },
  CANCELLED: {
    badge: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
    label: 'Cancelled',
    description: 'Request was cancelled',
  },
} as const

export const BALANCE_COLORS = {
  total: 'text-blue-600 dark:text-blue-400',
  available: 'text-green-600 dark:text-green-400',
  used: 'text-gray-600 dark:text-gray-400',
  pending: 'text-yellow-600 dark:text-yellow-400',
} as const

export const EMPLOYEE_STATUS_STYLES = {
  ACTIVE: {
    badge: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    icon: 'text-green-600',
    label: 'Active',
  },
  ON_LEAVE: {
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    icon: 'text-yellow-600',
    label: 'On Leave',
  },
  TERMINATED: {
    badge: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    icon: 'text-red-600',
    label: 'Terminated',
  },
  PROBATION: {
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    icon: 'text-blue-600',
    label: 'Probation',
  },
} as const
