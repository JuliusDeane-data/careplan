import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateVacationRequest, useVacationBalance } from '@/hooks/useVacation'
import { VACATION_CONFIG, VALIDATION_MESSAGES } from '@/config/vacation.config'
import { calculateVacationDays, calculateDaysUntil } from '@/utils/dateUtils'
import { getErrorMessage, getFieldErrors } from '@/utils/errorHandler'

// Validation schema using config
const vacationSchema = z
  .object({
    start_date: z.string().min(1, VALIDATION_MESSAGES.START_DATE_REQUIRED),
    end_date: z.string().min(1, VALIDATION_MESSAGES.END_DATE_REQUIRED),
    reason: z
      .string()
      .max(VACATION_CONFIG.MAX_REASON_LENGTH, VALIDATION_MESSAGES.REASON_TOO_LONG)
      .transform((str) => str.trim())
      .optional(),
  })
  .refine(
    (data) => {
      if (!data.start_date || !data.end_date) return true
      return new Date(data.end_date) >= new Date(data.start_date)
    },
    {
      message: VALIDATION_MESSAGES.END_BEFORE_START,
      path: ['end_date'],
    }
  )
  .refine(
    (data) => {
      if (!data.start_date) return true
      const daysFromNow = calculateDaysUntil(data.start_date)
      return daysFromNow >= VACATION_CONFIG.MIN_ADVANCE_DAYS
    },
    {
      message: VALIDATION_MESSAGES.MIN_ADVANCE_NOTICE,
      path: ['start_date'],
    }
  )

type VacationFormData = z.infer<typeof vacationSchema>

export default function VacationRequestPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string>('')

  const { data: balance } = useVacationBalance()
  const createMutation = useCreateVacationRequest()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setError: setFieldError,
  } = useForm<VacationFormData>({
    resolver: zodResolver(vacationSchema),
  })

  const startDate = watch('start_date')
  const endDate = watch('end_date')

  const requestedDays = calculateVacationDays(startDate, endDate)

  const onSubmit = async (data: VacationFormData) => {
    try {
      setError('')

      // Client-side balance check
      if (balance && requestedDays > balance.remaining_days) {
        setError(
          `Insufficient vacation days. Requested: ${requestedDays}, Available: ${balance.remaining_days}`
        )
        return
      }

      const toastId = toast.loading('Submitting vacation request...')

      await createMutation.mutateAsync(data)

      toast.success('Vacation request submitted successfully!', { id: toastId })
      navigate('/vacation')
    } catch (error: unknown) {
      // Handle field-specific errors from API
      const fieldErrors = getFieldErrors(error)
      if (fieldErrors) {
        Object.entries(fieldErrors).forEach(([field, message]) => {
          setFieldError(field as keyof VacationFormData, {
            type: 'server',
            message,
          })
        })
      }

      // Set general error message
      const errorMessage = getErrorMessage(error)
      setError(errorMessage)
      toast.error(errorMessage)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/vacation')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Request Vacation</h1>
            <p className="text-muted-foreground">Submit a new vacation request</p>
          </div>
        </div>

        {/* Balance Card */}
        {balance && (
          <Card>
            <CardHeader>
              <CardTitle>Your Vacation Balance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-primary">{balance.remaining_days}</p>
                  <p className="text-sm text-muted-foreground">Available</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-muted-foreground">{balance.used_days}</p>
                  <p className="text-sm text-muted-foreground">Used</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-warning">{balance.pending_days}</p>
                  <p className="text-sm text-muted-foreground">Pending</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Request Form */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card>
            <CardHeader>
              <CardTitle>Vacation Details</CardTitle>
              <CardDescription>
                Fill in the details of your vacation request (minimum {VACATION_CONFIG.MIN_ADVANCE_DAYS} days advance notice)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Date Range */}
              <div className="grid gap-6 md:grid-cols-2">
                {/* Start Date */}
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date *</Label>
                  <Input id="start_date" type="date" {...register('start_date')} />
                  {errors.start_date && (
                    <p className="text-sm text-red-500">{errors.start_date.message}</p>
                  )}
                </div>

                {/* End Date */}
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date *</Label>
                  <Input id="end_date" type="date" {...register('end_date')} />
                  {errors.end_date && (
                    <p className="text-sm text-red-500">{errors.end_date.message}</p>
                  )}
                </div>
              </div>

              {/* Days Calculation */}
              {startDate && endDate && requestedDays > 0 && (
                <div
                  className={`rounded-lg p-4 border ${
                    balance && requestedDays > balance.remaining_days
                      ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                      : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                  }`}
                >
                  <p className="text-sm">
                    <strong>Requested Days: {requestedDays}</strong>
                    {balance && requestedDays > balance.remaining_days && (
                      <span className="text-red-600 dark:text-red-400 ml-2">
                        (Insufficient balance: {balance.remaining_days} days available)
                      </span>
                    )}
                  </p>
                </div>
              )}

              {/* Reason */}
              <div className="space-y-2">
                <Label htmlFor="reason">
                  Reason (Optional)
                  <span className="text-xs text-muted-foreground ml-2">
                    Max {VACATION_CONFIG.MAX_REASON_LENGTH} characters
                  </span>
                </Label>
                <textarea
                  id="reason"
                  placeholder="e.g., Family vacation, personal time..."
                  {...register('reason')}
                  rows={4}
                  maxLength={VACATION_CONFIG.MAX_REASON_LENGTH}
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  aria-describedby="reason-description"
                />
                <p id="reason-description" className="text-xs text-muted-foreground">
                  Optional explanation for your vacation request
                </p>
                {errors.reason && <p className="text-sm text-red-500">{errors.reason.message}</p>}
              </div>

              {/* Error Message */}
              {error && (
                <div
                  role="alert"
                  className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
                >
                  <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-4 justify-end">
                <Button type="button" variant="outline" onClick={() => navigate('/vacation')}>
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || createMutation.isPending}
                  aria-busy={isSubmitting || createMutation.isPending}
                >
                  {isSubmitting || createMutation.isPending ? 'Submitting...' : 'Submit Request'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </div>
    </div>
  )
}
