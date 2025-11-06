/**
 * ActivityFeed Component
 * Displays a feed of recent activities
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useActivities } from '@/hooks/useDashboard'
import { Loader2, RefreshCw } from 'lucide-react'
import ActivityItem from './ActivityItem'

interface ActivityFeedProps {
  limit?: number
  showViewAll?: boolean
  onViewAll?: () => void
}

export default function ActivityFeed({
  limit = 10,
  showViewAll = false,
  onViewAll,
}: ActivityFeedProps) {
  const { data, isLoading, error, refetch, isRefetching } = useActivities(limit)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle>Recent Activity</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => refetch()}
          disabled={isRefetching}
        >
          <RefreshCw
            className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`}
          />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-sm text-destructive">Failed to load activities</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              className="mt-2"
            >
              Try Again
            </Button>
          </div>
        ) : !data?.results.length ? (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">No recent activities</p>
          </div>
        ) : (
          <>
            <div className="divide-y">
              {data.results.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </div>

            {showViewAll && data.count > limit && (
              <div className="mt-4 text-center">
                <Button variant="outline" size="sm" onClick={onViewAll}>
                  View All Activities ({data.count})
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
