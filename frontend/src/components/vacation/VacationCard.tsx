import { useState } from 'react'
import { Calendar, Clock } from 'lucide-react'
import { toast } from 'sonner'
import type { VacationRequest } from '@/types/vacation'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { useCancelVacationRequest } from '@/hooks/useVacation'
import { VACATION_STATUS_STYLES } from '@/config/theme'
import { formatVacationDate, formatDateRange } from '@/utils/dateUtils'
import { getErrorMessage } from '@/utils/errorHandler'

interface VacationCardProps {
  request: VacationRequest
}

export default function VacationCard({ request }: VacationCardProps) {
  const cancelMutation = useCancelVacationRequest()
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)

  const handleCancelClick = () => {
    setShowConfirmDialog(true)
  }

  const handleConfirmCancel = async () => {
    const toastId = toast.loading('Cancelling vacation request...')

    try {
      await cancelMutation.mutateAsync(request.id)
      toast.success('Vacation request cancelled successfully', { id: toastId })
    } catch (error) {
      const errorMessage = getErrorMessage(error)
      toast.error(errorMessage, { id: toastId })
    } finally {
      setShowConfirmDialog(false)
    }
  }

  return (
    <>
      <ConfirmDialog
        open={showConfirmDialog}
        onOpenChange={setShowConfirmDialog}
        title="Cancel Vacation Request"
        description={`Are you sure you want to cancel your vacation from ${formatVacationDate(request.start_date)} to ${formatVacationDate(request.end_date)}?`}
        confirmLabel="Cancel Request"
        cancelLabel="Keep Request"
        onConfirm={handleConfirmCancel}
        variant="destructive"
      />
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          {/* Left side - Date and details */}
          <div className="flex-1 space-y-3">
            {/* Date Range */}
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <span className="font-medium">
                {formatDateRange(request.start_date, request.end_date)}
              </span>
            </div>

            {/* Days Badge */}
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <span className="text-sm text-muted-foreground">
                {request.total_days} {request.total_days === 1 ? 'day' : 'days'}
              </span>
            </div>

            {/* Reason */}
            {request.reason && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {request.reason}
              </p>
            )}

            {/* Approval/Denial info */}
            {request.approved_by && (
              <p className="text-xs text-muted-foreground">
                Approved by {request.approved_by.full_name}
              </p>
            )}
            {request.denied_by && (
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">
                  Denied by {request.denied_by.full_name}
                </p>
                {request.denial_reason && (
                  <p className="text-xs text-red-600 dark:text-red-400">
                    Reason: {request.denial_reason}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Right side - Status and actions */}
          <div className="flex flex-col items-end gap-3">
            {/* Status Badge with accessibility */}
            <span
              role="status"
              aria-label={`Status: ${VACATION_STATUS_STYLES[request.status].label} - ${VACATION_STATUS_STYLES[request.status].description}`}
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                VACATION_STATUS_STYLES[request.status].badge
              }`}
            >
              {VACATION_STATUS_STYLES[request.status].label}
            </span>

            {/* Cancel Button - only show for pending requests */}
            {request.status === 'PENDING' && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancelClick}
                disabled={cancelMutation.isPending}
                aria-label={`Cancel vacation request from ${formatVacationDate(request.start_date)} to ${formatVacationDate(request.end_date)}`}
              >
                {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
    </>
  )
}
