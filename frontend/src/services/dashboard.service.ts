/**
 * Dashboard service - API integration for dashboard data
 */

import api from './api'
import type { DashboardStats, Activity, UpcomingEvent } from '@/types/dashboard'

export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/dashboard/stats/')
    return response.data
  },

  /**
   * Get activity feed
   */
  async getActivities(params?: {
    limit?: number
    offset?: number
    type?: string
    since?: string
  }): Promise<{
    count: number
    next: string | null
    results: Activity[]
  }> {
    const response = await api.get('/dashboard/activities/', { params })
    return response.data
  },

  /**
   * Mark activity as read
   */
  async markActivityRead(id: number): Promise<void> {
    await api.post(`/dashboard/activities/${id}/mark-read/`)
  },

  /**
   * Get upcoming events
   */
  async getUpcomingEvents(params?: {
    days?: number
    types?: string[]
  }): Promise<UpcomingEvent[]> {
    const response = await api.get<UpcomingEvent[]>('/dashboard/upcoming-events/', {
      params,
    })
    return response.data
  },
}
