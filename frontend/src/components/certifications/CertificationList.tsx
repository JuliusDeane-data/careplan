/**
 * CertificationList - Display list of certifications
 */

import { CertificationCard } from './CertificationCard'
import type { EmployeeCertification } from '@/types'

interface CertificationListProps {
  certifications: EmployeeCertification[]
  showEmployee?: boolean
  onVerify?: (id: number) => void
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  canVerify?: boolean
  canEdit?: boolean
  canDelete?: boolean
  emptyMessage?: string
  isLoading?: boolean
}

export function CertificationList({
  certifications,
  showEmployee = false,
  onVerify,
  onEdit,
  onDelete,
  canVerify = false,
  canEdit = false,
  canDelete = false,
  emptyMessage = 'No certifications found',
  isLoading = false,
}: CertificationListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-48 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse"
          />
        ))}
      </div>
    )
  }

  if (certifications.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {certifications.map((certification) => (
        <CertificationCard
          key={certification.id}
          certification={certification}
          showEmployee={showEmployee}
          onVerify={onVerify}
          onEdit={onEdit}
          onDelete={onDelete}
          canVerify={canVerify}
          canEdit={canEdit}
          canDelete={canDelete}
        />
      ))}
    </div>
  )
}
