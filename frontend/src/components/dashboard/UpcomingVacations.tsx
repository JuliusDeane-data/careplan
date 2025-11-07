/**
 * UpcomingVacations Component
 * Displays upcoming vacation events
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useUpcomingEvents } from '@/hooks/useDashboard'
import { Loader2, Calendar } from 'lucide-react'
import { formatVacationDate, getDaysUntil, getEventDuration } from '@/utils/dateUtils'

interface UpcomingVacationsProps {
  limit?: number
  days?: number
}

export default function UpcomingVacations({
  limit = 5,
  days = 30,
}: UpcomingVacationsProps) {
  const { data: events, isLoading, error } = useUpcomingEvents(days)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Upcoming Events
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-sm text-destructive">
              Failed to load upcoming events
            </p>
          </div>
        ) : !events?.length ? (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">
              No upcoming events in the next {days} days
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {events.slice(0, limit).map((event) => (
              <div
                key={event.id}
                className="flex items-start justify-between gap-4 pb-4 border-b last:border-0 last:pb-0"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-sm">{event.title}</p>
                    <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                      {event.type}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {formatVacationDate(event.start_date)}
                    {event.start_date !== event.end_date && (
                      <> - {formatVacationDate(event.end_date)}</>
                    )}
                  </p>
                  {event.employee && (
                    <p className="text-xs text-muted-foreground mt-1">
                      👤 {event.employee.name}
                    </p>
                  )}
                  {event.location && (
                    <p className="text-xs text-muted-foreground mt-1">
                      📍 {event.location}
                    </p>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs font-medium text-muted-foreground">
                    {getDaysUntil(event.start_date)}
                  </p>
                  {event.start_date !== event.end_date && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {getEventDuration(event.start_date, event.end_date)} days
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
