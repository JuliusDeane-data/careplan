/**
 * Employee status badge component
 */

import { EMPLOYEE_STATUS_STYLES } from '@/config/theme'
import type { EmploymentStatus } from '@/types/employee'

interface EmployeeStatusBadgeProps {
  status: EmploymentStatus
}

export default function EmployeeStatusBadge({ status }: EmployeeStatusBadgeProps) {
  const styles = EMPLOYEE_STATUS_STYLES[status]

  return (
    <span
      role="status"
      aria-label={`Employment status: ${styles.label}`}
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles.badge}`}
    >
      {styles.label}
    </span>
  )
}
