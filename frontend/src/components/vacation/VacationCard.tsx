import { format } from 'date-fns'
import { Calendar, Clock } from 'lucide-react'
import type { VacationRequest } from '@/types/vacation'
import { VacationStatusLabels } from '@/types/vacation'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useCancelVacationRequest } from '@/hooks/useVacation'

interface VacationCardProps {
  request: VacationRequest
}

export default function VacationCard({ request }: VacationCardProps) {
  const cancelMutation = useCancelVacationRequest()

  const handleCancel = async () => {
    if (window.confirm('Are you sure you want to cancel this vacation request?')) {
      try {
        await cancelMutation.mutateAsync(request.id)
      } catch (error) {
        console.error('Failed to cancel request:', error)
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'APPROVED':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'DENIED':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MMM d, yyyy')
    } catch {
      return dateStr
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          {/* Left side - Date and details */}
          <div className="flex-1 space-y-3">
            {/* Date Range */}
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <span className="font-medium">
                {formatDate(request.start_date)} - {formatDate(request.end_date)}
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
            {/* Status Badge */}
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                request.status
              )}`}
            >
              {VacationStatusLabels[request.status]}
            </span>

            {/* Cancel Button - only show for pending requests */}
            {request.status === 'PENDING' && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
                disabled={cancelMutation.isPending}
              >
                {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
