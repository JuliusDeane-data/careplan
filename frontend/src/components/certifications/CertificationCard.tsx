/**
 * CertificationCard - Display certification information in a card format
 */

import { format } from 'date-fns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CertificationBadge, ExpiryWarningBadge } from './CertificationBadge'
import { CheckCircle, FileText, Calendar, AlertCircle } from 'lucide-react'
import type { EmployeeCertification } from '@/types'

interface CertificationCardProps {
  certification: EmployeeCertification
  showEmployee?: boolean
  onVerify?: (id: number) => void
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  canVerify?: boolean
  canEdit?: boolean
  canDelete?: boolean
}

export function CertificationCard({
  certification,
  showEmployee = false,
  onVerify,
  onEdit,
  onDelete,
  canVerify = false,
  canEdit = false,
  canDelete = false,
}: CertificationCardProps) {
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy')
    } catch {
      return dateString
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold">
              {certification.qualification.name}
              <span className="ml-2 text-sm text-muted-foreground font-normal">
                ({certification.qualification.code})
              </span>
            </CardTitle>
            {showEmployee && (
              <p className="text-sm text-muted-foreground mt-1">
                {certification.employee.first_name} {certification.employee.last_name}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <CertificationBadge
              status={certification.status}
              warningLevel={certification.expiry_warning_level}
              daysUntilExpiry={certification.days_until_expiry}
            />
            {certification.expiry_warning_level && (
              <ExpiryWarningBadge
                warningLevel={certification.expiry_warning_level}
                daysUntilExpiry={certification.days_until_expiry}
              />
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Dates */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Issued</p>
              <p className="text-sm font-medium">{formatDate(certification.issue_date)}</p>
            </div>
          </div>
          {certification.expiry_date && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Expires</p>
                <p className="text-sm font-medium">{formatDate(certification.expiry_date)}</p>
              </div>
            </div>
          )}
        </div>

        {/* Verification Status */}
        <div className="flex items-center gap-2">
          {certification.is_verified ? (
            <>
              <CheckCircle className="w-4 h-4 text-green-600" />
              <div>
                <p className="text-xs text-muted-foreground">Verified by</p>
                <p className="text-sm font-medium">
                  {certification.verified_by?.first_name}{' '}
                  {certification.verified_by?.last_name}
                  {certification.verified_at && (
                    <span className="text-xs text-muted-foreground ml-1">
                      on {formatDate(certification.verified_at)}
                    </span>
                  )}
                </p>
              </div>
            </>
          ) : (
            <>
              <AlertCircle className="w-4 h-4 text-yellow-600" />
              <p className="text-sm text-muted-foreground">Not yet verified</p>
            </>
          )}
        </div>

        {/* Document */}
        {certification.certificate_document && (
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-muted-foreground" />
            <a
              href={certification.certificate_document}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline"
            >
              View Certificate Document
            </a>
          </div>
        )}

        {/* Notes */}
        {certification.notes && (
          <div className="pt-2 border-t">
            <p className="text-xs text-muted-foreground mb-1">Notes</p>
            <p className="text-sm whitespace-pre-wrap">{certification.notes}</p>
          </div>
        )}

        {/* Actions */}
        {(canVerify || canEdit || canDelete) && (
          <div className="flex gap-2 pt-2 border-t">
            {canVerify && !certification.is_verified && (
              <Button
                size="sm"
                onClick={() => onVerify?.(certification.id)}
                className="flex-1"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Verify
              </Button>
            )}
            {canEdit && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onEdit?.(certification.id)}
                className="flex-1"
              >
                Edit
              </Button>
            )}
            {canDelete && (
              <Button
                size="sm"
                variant="destructive"
                onClick={() => onDelete?.(certification.id)}
                className="flex-1"
              >
                Delete
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
