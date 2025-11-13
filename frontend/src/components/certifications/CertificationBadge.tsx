/**
 * CertificationBadge - Visual indicator for certification status
 */

import { Badge } from '@/components/ui/badge'
import type { CertificationStatus, ExpiryWarningLevel } from '@/types'
import { getCertificationStatusColor } from '@/config/certification.config'

interface CertificationBadgeProps {
  status: CertificationStatus
  warningLevel?: ExpiryWarningLevel
  daysUntilExpiry?: number | null
  className?: string
}

export function CertificationBadge({
  status,
  warningLevel: _warningLevel,
  daysUntilExpiry,
  className,
}: CertificationBadgeProps) {
  const getStatusText = () => {
    if (status === 'EXPIRING_SOON' && daysUntilExpiry !== null && daysUntilExpiry !== undefined) {
      return `Expires in ${daysUntilExpiry} days`
    }

    switch (status) {
      case 'ACTIVE':
        return 'Active'
      case 'EXPIRING_SOON':
        return 'Expiring Soon'
      case 'EXPIRED':
        return 'Expired'
      case 'PENDING_VERIFICATION':
        return 'Pending Verification'
      default:
        return status
    }
  }

  const getVariant = () => {
    switch (status) {
      case 'ACTIVE':
        return 'default'
      case 'EXPIRING_SOON':
        return 'outline'
      case 'EXPIRED':
        return 'destructive'
      case 'PENDING_VERIFICATION':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const getColorClass = () => {
    const color = getCertificationStatusColor(status)
    switch (color) {
      case 'green':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'yellow':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'red':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      case 'gray':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
      default:
        return ''
    }
  }

  return (
    <Badge variant={getVariant()} className={`${getColorClass()} ${className || ''}`}>
      {getStatusText()}
    </Badge>
  )
}

interface ExpiryWarningBadgeProps {
  warningLevel: ExpiryWarningLevel
  daysUntilExpiry?: number | null
  className?: string
}

export function ExpiryWarningBadge({
  warningLevel,
  daysUntilExpiry,
  className,
}: ExpiryWarningBadgeProps) {
  if (!warningLevel) return null

  const getWarningText = () => {
    if (daysUntilExpiry !== null && daysUntilExpiry !== undefined) {
      return `${daysUntilExpiry} days`
    }
    return warningLevel
  }

  const getColorClass = () => {
    switch (warningLevel) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400 border-red-300'
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400 border-orange-300'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400 border-yellow-300'
      case 'LOW':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 border-blue-300'
      default:
        return ''
    }
  }

  return (
    <Badge variant="outline" className={`${getColorClass()} ${className || ''}`}>
      {getWarningText()}
    </Badge>
  )
}
