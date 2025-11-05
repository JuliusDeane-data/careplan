import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useCreateVacationRequest, useVacationBalance } from '@/hooks/useVacation'

// Validation schema
const vacationSchema = z.object({
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  reason: z.string().optional(),
}).refine((data) => {
  const start = new Date(data.start_date)
  const end = new Date(data.end_date)
  return end >= start
}, {
  message: "End date must be on or after start date",
  path: ["end_date"]
}).refine((data) => {
  const start = new Date(data.start_date)
  const now = new Date()
  const daysFromNow = Math.ceil((start.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return daysFromNow >= 14
}, {
  message: "Vacation must be requested at least 14 days in advance",
  path: ["start_date"]
})

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
  } = useForm<VacationFormData>({
    resolver: zodResolver(vacationSchema),
  })

  const startDate = watch('start_date')
  const endDate = watch('end_date')

  const calculateDays = () => {
    if (!startDate || !endDate) return 0
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = Math.abs(end.getTime() - start.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    return diffDays
  }

  const requestedDays = calculateDays()

  const onSubmit = async (data: VacationFormData) => {
    try {
      setError('')
      await createMutation.mutateAsync(data)
      navigate('/vacation')
    } catch (error: any) {
      setError(error.response?.data?.message || 'Failed to create vacation request')
      console.error('Failed to create vacation request:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/vacation')}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Request Vacation</h1>
            <p className="text-muted-foreground">
              Submit a new vacation request
            </p>
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
                  <p className="text-2xl font-bold text-primary">
                    {balance.remaining_days}
                  </p>
                  <p className="text-sm text-muted-foreground">Available</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-muted-foreground">
                    {balance.used_days}
                  </p>
                  <p className="text-sm text-muted-foreground">Used</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-warning">
                    {balance.pending_days}
                  </p>
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
                Fill in the details of your vacation request
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Date Range */}
              <div className="grid gap-6 md:grid-cols-2">
                {/* Start Date */}
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date *</Label>
                  <Input
                    id="start_date"
                    type="date"
                    {...register('start_date')}
                  />
                  {errors.start_date && (
                    <p className="text-sm text-red-500">{errors.start_date.message}</p>
                  )}
                </div>

                {/* End Date */}
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date *</Label>
                  <Input
                    id="end_date"
                    type="date"
                    {...register('end_date')}
                  />
                  {errors.end_date && (
                    <p className="text-sm text-red-500">{errors.end_date.message}</p>
                  )}
                </div>
              </div>

              {/* Days Calculation */}
              {startDate && endDate && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
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
                <Label htmlFor="reason">Reason (Optional)</Label>
                <textarea
                  id="reason"
                  placeholder="e.g., Family vacation, personal time..."
                  {...register('reason')}
                  rows={4}
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
                {errors.reason && (
                  <p className="text-sm text-red-500">{errors.reason.message}</p>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-4 justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/vacation')}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || createMutation.isPending}
                >
                  {isSubmitting || createMutation.isPending
                    ? 'Submitting...'
                    : 'Submit Request'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </div>
    </div>
  )
}
