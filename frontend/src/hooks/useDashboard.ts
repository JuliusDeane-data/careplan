/**
 * Dashboard React Query hooks
 */

import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '@/services/dashboard.service'
import { DASHBOARD_CONFIG } from '@/config/dashboard.config'

/**
 * Hook to fetch dashboard statistics
 */
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardService.getStats(),
    staleTime: DASHBOARD_CONFIG.STATS_STALE_TIME,
    refetchInterval: DASHBOARD_CONFIG.POLLING_INTERVAL, // Auto-refresh every 30s
  })
}

/**
 * Hook to fetch activity feed
 */
export function useActivities(limit: number = DASHBOARD_CONFIG.ACTIVITY_PAGE_SIZE) {
  return useQuery({
    queryKey: ['activities', limit],
    queryFn: () => dashboardService.getActivities({ limit }),
    staleTime: DASHBOARD_CONFIG.ACTIVITIES_STALE_TIME,
    refetchInterval: DASHBOARD_CONFIG.POLLING_INTERVAL, // Auto-refresh
  })
}

/**
 * Hook to fetch upcoming events
 */
export function useUpcomingEvents(days: number = DASHBOARD_CONFIG.UPCOMING_EVENTS_DAYS) {
  return useQuery({
    queryKey: ['upcoming-events', days],
    queryFn: () => dashboardService.getUpcomingEvents({ days }),
    staleTime: DASHBOARD_CONFIG.STATS_STALE_TIME,
  })
}
