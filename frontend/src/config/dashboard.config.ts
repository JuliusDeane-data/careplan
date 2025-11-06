/**
 * Dashboard module configuration
 */

export const DASHBOARD_CONFIG = {
  // Real-time updates
  POLLING_INTERVAL: 30 * 1000, // 30 seconds
  WEBSOCKET_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',

  // Activity feed
  MAX_ACTIVITIES: 50,
  ACTIVITY_PAGE_SIZE: 20,

  // Upcoming events
  UPCOMING_EVENTS_DAYS: 30,
  MAX_UPCOMING_EVENTS: 10,

  // Caching
  STATS_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  ACTIVITIES_STALE_TIME: 60 * 1000, // 1 minute

  // Performance
  SKELETON_COUNT: 4,
  ANIMATION_DURATION: 200, // ms
} as const
