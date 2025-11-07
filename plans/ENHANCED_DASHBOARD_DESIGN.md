# Enhanced Dashboard - Architectural Design Document

**Version:** 1.0
**Date:** November 6, 2025
**Author:** Senior Software Designer
**Status:** Design Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Requirements](#business-requirements)
3. [System Architecture](#system-architecture)
4. [Component Design](#component-design)
5. [Data Models](#data-models)
6. [API Integration](#api-integration)
7. [Real-Time Features](#real-time-features)
8. [User Flows](#user-flows)
9. [UI/UX Specifications](#ui-ux-specifications)
10. [Performance Optimization](#performance-optimization)
11. [Implementation Plan](#implementation-plan)
12. [Testing Strategy](#testing-strategy)

---

## Executive Summary

The Enhanced Dashboard transforms the basic dashboard into a comprehensive, role-based command center providing real-time insights, quick actions, and personalized information for care workers, managers, and administrators.

### Key Features
- **Real-Time Statistics:** Live metrics updated every 30 seconds
- **Activity Feed:** Recent actions and updates across the system
- **Quick Actions:** One-click access to common tasks
- **Personalized Widgets:** Role-based dashboard customization
- **Notification Center:** Unread notifications with priority indicators
- **Upcoming Events:** Calendar integration for vacations and shifts
- **Manager Insights:** Team metrics and pending approvals (managers/admins)
- **Performance Metrics:** KPIs and trends visualization

### Success Criteria
- Dashboard load time <1 second
- Real-time updates without page refresh
- Mobile-responsive on all devices
- Personalized based on user role
- Accessible (WCAG 2.1 AA)

---

## Business Requirements

### Functional Requirements

#### FR-1: Statistics Dashboard

**All Users:**
- Personal vacation balance with visual indicator
- Upcoming vacation requests (pending/approved)
- Recent activity feed (last 10 actions)
- Quick action buttons

**Managers/Admins (Additional):**
- Team statistics:
  - Total team members
  - On vacation today
  - Pending vacation requests
  - Average vacation utilization
- System statistics:
  - Total employees
  - Active locations
  - Total vacation requests this month

#### FR-2: Activity Feed

- Display recent activities (last 50)
- Types of activities:
  - Vacation request submitted
  - Vacation approved/denied
  - Employee created/updated
  - Location added
  - System notifications
- Time-based grouping (Today, Yesterday, This Week, Older)
- Real-time updates (WebSocket or polling)
- Filter by activity type
- "Mark all as read" functionality
- Load more pagination

#### FR-3: Quick Actions

**All Users:**
- Request Vacation
- View My Profile
- View My Vacations
- Contact Support

**Managers (Additional):**
- Approve Pending Requests
- View Team Calendar
- Generate Reports
- Manage Team

**Admins (Additional):**
- Add Employee
- Manage Locations
- System Settings
- View Analytics

#### FR-4: Notification Center

- Unread count badge
- Priority levels (high, medium, low)
- Notification types:
  - Vacation approved/denied
  - Request requires approval (managers)
  - System alerts
  - Reminders
- Click to navigate to related item
- Mark as read/unread
- Delete notification
- Notification preferences

#### FR-5: Widgets

**Vacation Balance Widget:**
- Visual progress bar
- Days remaining / total
- Expiration warning
- Quick link to request

**Upcoming Events Widget:**
- Next 5 upcoming vacations
- Calendar view toggle
- Add to personal calendar

**Pending Approvals Widget (Manager):**
- Count of pending requests
- Quick approve/deny
- Link to full list

**Team Overview Widget (Manager):**
- Team availability today
- Out of office list
- Coverage gaps

**Analytics Widget (Admin):**
- Vacation utilization rate
- Employee growth trend
- Top locations by headcount
- Monthly request trends

### Non-Functional Requirements

#### NFR-1: Performance
- Initial dashboard load: <1s
- Widget updates: <300ms
- Activity feed append: <100ms
- Support 100+ widgets without lag
- Efficient real-time updates

#### NFR-2: Usability
- Intuitive widget layout
- Drag-and-drop customization (future)
- Clear visual hierarchy
- Responsive design
- Dark mode support

#### NFR-3: Reliability
- Graceful degradation if API fails
- Fallback for real-time connection
- Cache dashboard data
- Retry failed requests

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  DashboardPage                                          │  │
│  │  ├── StatsGrid          (Statistics widgets)           │  │
│  │  ├── ActivityFeed       (Recent activities)            │  │
│  │  ├── QuickActions       (Action buttons)               │  │
│  │  ├── NotificationCenter (Notifications)                │  │
│  │  ├── UpcomingEvents     (Calendar events)              │  │
│  │  └── RoleSpecificWidgets (Manager/Admin widgets)       │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│       Business Logic Layer                                    │
│  ┌──────────────────┬──▼─────────────┬──────────────────┐   │
│  │ useDashboard     │ useActivities  │ useNotifications │   │
│  │ (stats)          │ (feed)         │ (alerts)         │   │
│  └──────────────────┴────────────────┴──────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│          Data Layer                                           │
│  ┌──────────────────┬──▼─────────────┬──────────────────┐   │
│  │ dashboardService │ activityService│ notificationService│  │
│  │ getStats()       │ getActivities()│ getNotifications() │  │
│  │ getUserMetrics() │ subscribeToFeed│ markAsRead()       │  │
│  └──────────────────┴────────────────┴──────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   Backend API Layer                           │
│  /api/dashboard/stats/        - Dashboard statistics          │
│  /api/dashboard/activities/   - Activity feed                 │
│  /api/notifications/          - Notifications                 │
│  /api/dashboard/widgets/      - Widget configuration          │
│  WebSocket: /ws/activities/   - Real-time activity updates    │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User → Dashboard Page → React Query Hook → API Service → Backend
                  ↑                                         │
                  └─────────── Real-time Update ←──────────┘
                            (WebSocket or Polling)
```

---

## Component Design

### Component Hierarchy

```
pages/
└── DashboardPage.tsx
    ├── DashboardHeader
    │   ├── Welcome Message
    │   ├── NotificationBell
    │   └── QuickSearch
    │
    ├── DashboardGrid (responsive grid)
    │   ├── StatsCard (vacation balance)
    │   ├── StatsCard (pending requests)
    │   ├── StatsCard (upcoming events)
    │   ├── ActivityFeed
    │   ├── QuickActions
    │   ├── UpcomingVacations
    │   ├── [Manager] PendingApprovals
    │   ├── [Manager] TeamOverview
    │   ├── [Admin] SystemMetrics
    │   └── [Admin] AnalyticsChart
    │
    └── NotificationCenter (slide-over)
        ├── NotificationList
        ├── NotificationItem
        └── NotificationFilters

components/dashboard/
├── StatsCard.tsx           (Metric display card)
├── ActivityFeed.tsx        (Activity list)
├── ActivityItem.tsx        (Single activity)
├── QuickActions.tsx        (Action buttons grid)
├── NotificationCenter.tsx  (Notification panel)
├── NotificationItem.tsx    (Single notification)
├── UpcomingVacations.tsx   (Event list)
├── PendingApprovals.tsx    (Manager widget)
├── TeamOverview.tsx        (Manager widget)
└── AnalyticsChart.tsx      (Admin widget)
```

### Component Specifications

#### DashboardPage

**Purpose:** Main dashboard container

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  CarePlan Dashboard        🔍 Search  🔔 (3)  [John] [⚙]   │
├─────────────────────────────────────────────────────────────┤
│  Welcome back, John!                         [Logout]        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Vacation    │  │ Pending     │  │ Upcoming    │         │
│  │ Balance     │  │ Requests    │  │ Events      │         │
│  │             │  │             │  │             │         │
│  │   15/30     │  │      2      │  │      3      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  ┌─────────────────────────────┐  ┌──────────────────────┐  │
│  │ Recent Activity             │  │ Quick Actions        │  │
│  │                             │  │                      │  │
│  │ • Vacation approved         │  │ [Request Vacation]   │  │
│  │ • New employee added        │  │ [View My Profile]    │  │
│  │ • Location updated          │  │ [Team Calendar]      │  │
│  │ • ...                       │  │ [Generate Report]    │  │
│  └─────────────────────────────┘  └──────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Upcoming Vacations                                    │   │
│  │                                                        │   │
│  │ Dec 20-27  John Smith       [View Details]           │   │
│  │ Jan 5-12   Jane Doe         [View Details]           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  [Manager Only]                                              │
│  ┌─────────────────────┐  ┌───────────────────────────┐     │
│  │ Pending Approvals   │  │ Team Overview             │     │
│  │                     │  │                           │     │
│  │ 5 requests awaiting │  │ Available: 12 / 15        │     │
│  │ [Review Now]        │  │ On Vacation: 2            │     │
│  └─────────────────────┘  │ On Leave: 1               │     │
│                            └───────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

#### StatsCard

**Purpose:** Display a single metric with icon and trend

**Props:**
```typescript
interface StatsCardProps {
  title: string
  value: number | string
  icon: ReactNode
  trend?: {
    value: number
    direction: 'up' | 'down' | 'neutral'
  }
  subtitle?: string
  action?: {
    label: string
    onClick: () => void
  }
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'gray'
}
```

**Example:**
```tsx
<StatsCard
  title="Vacation Balance"
  value="15 days"
  subtitle="of 30 total"
  icon={<Calendar />}
  color="green"
  action={{
    label: "Request Vacation",
    onClick: () => navigate('/vacation/new')
  }}
/>
```

---

#### ActivityFeed

**Purpose:** Display recent system activities

**Props:**
```typescript
interface ActivityFeedProps {
  maxItems?: number
  showFilters?: boolean
  realTime?: boolean
  onActivityClick?: (activity: Activity) => void
}
```

**Features:**
- Time grouping (Today, Yesterday, etc.)
- Activity type icons
- Relative timestamps ("2 hours ago")
- "Load more" button
- Auto-scroll to new items

---

#### QuickActions

**Purpose:** Role-based quick action buttons

**Layout:**
```
┌────────────────────────────────────┐
│  Quick Actions                     │
│                                    │
│  [📅 Request Vacation]             │
│  [👤 View My Profile]              │
│  [📊 View My Vacations]            │
│  [📞 Contact Support]              │
│                                    │
│  [Manager Only]                    │
│  [✓ Approve Requests]              │
│  [👥 View Team]                    │
└────────────────────────────────────┘
```

---

#### NotificationCenter

**Purpose:** Notification panel (slide-over)

**Features:**
- Unread count badge
- Priority filtering
- Mark as read/unread
- Delete notifications
- Navigate to related item
- Real-time updates

**Layout:**
```
┌────────────────────────────────────┐
│  Notifications (3 unread)    [✕]  │
├────────────────────────────────────┤
│  [All] [Unread] [High Priority]   │
├────────────────────────────────────┤
│  🔴 Vacation Request Denied        │
│     Your request was denied...     │
│     2 hours ago          [View]    │
├────────────────────────────────────┤
│  ⚫ Vacation Approved               │
│     Your vacation was approved...  │
│     1 day ago            [View]    │
├────────────────────────────────────┤
│  ⚪ New Employee Added              │
│     John Smith joined the team...  │
│     3 days ago           [View]    │
├────────────────────────────────────┤
│  [Load More]  [Mark All as Read]   │
└────────────────────────────────────┘
```

---

## Data Models

### TypeScript Interfaces

```typescript
// Dashboard Statistics
export interface DashboardStats {
  // Personal stats (all users)
  personal: {
    vacation_balance: {
      total: number
      remaining: number
      used: number
      pending: number
    }
    upcoming_vacations: number
    pending_requests: number
    last_login: string
  }

  // Team stats (managers only)
  team?: {
    total_members: number
    on_vacation_today: number
    pending_approvals: number
    vacation_utilization: number // percentage
    coverage_gaps: number
  }

  // System stats (admins only)
  system?: {
    total_employees: number
    active_employees: number
    total_locations: number
    vacation_requests_this_month: number
    system_health: 'healthy' | 'warning' | 'critical'
  }
}

// Activity Item
export interface Activity {
  id: number
  type: ActivityType
  title: string
  description: string
  actor: {
    id: number
    name: string
    avatar?: string
  }
  target?: {
    type: 'employee' | 'vacation' | 'location' | 'system'
    id: number
    name: string
  }
  timestamp: string
  is_read: boolean
  metadata?: Record<string, any>
}

export type ActivityType =
  | 'vacation_requested'
  | 'vacation_approved'
  | 'vacation_denied'
  | 'vacation_cancelled'
  | 'employee_created'
  | 'employee_updated'
  | 'employee_deleted'
  | 'location_created'
  | 'location_updated'
  | 'system_notification'
  | 'user_login'

// Notification
export interface Notification {
  id: number
  type: NotificationType
  priority: 'high' | 'medium' | 'low'
  title: string
  message: string
  link?: string
  is_read: boolean
  created_at: string
  expires_at?: string
  metadata?: Record<string, any>
}

export type NotificationType =
  | 'vacation_status'
  | 'approval_required'
  | 'system_alert'
  | 'reminder'
  | 'announcement'

// Upcoming Event
export interface UpcomingEvent {
  id: number
  type: 'vacation' | 'holiday' | 'meeting'
  title: string
  start_date: string
  end_date: string
  all_day: boolean
  employee?: {
    id: number
    name: string
    avatar?: string
  }
  location?: string
  status: 'pending' | 'approved' | 'confirmed'
}

// Widget Configuration
export interface WidgetConfig {
  id: string
  type: WidgetType
  title: string
  position: {
    row: number
    col: number
    width: number
    height: number
  }
  settings: Record<string, any>
  is_visible: boolean
}

export type WidgetType =
  | 'vacation_balance'
  | 'pending_requests'
  | 'upcoming_events'
  | 'activity_feed'
  | 'quick_actions'
  | 'pending_approvals'
  | 'team_overview'
  | 'system_metrics'
  | 'analytics_chart'
```

---

## API Integration

### Service Layer

```typescript
// src/services/dashboard.service.ts

import api from './api'
import type {
  DashboardStats,
  Activity,
  Notification,
  UpcomingEvent,
  WidgetConfig,
} from '@/types/dashboard'

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
   * Get notifications
   */
  async getNotifications(params?: {
    unread_only?: boolean
    priority?: string
  }): Promise<Notification[]> {
    const response = await api.get<Notification[]>('/notifications/', { params })
    return response.data
  },

  /**
   * Mark notification as read
   */
  async markNotificationRead(id: number): Promise<void> {
    await api.patch(`/notifications/${id}/`, { is_read: true })
  },

  /**
   * Mark all notifications as read
   */
  async markAllNotificationsRead(): Promise<void> {
    await api.post('/notifications/mark-all-read/')
  },

  /**
   * Delete notification
   */
  async deleteNotification(id: number): Promise<void> {
    await api.delete(`/notifications/${id}/`)
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

  /**
   * Get user's widget configuration
   */
  async getWidgetConfig(): Promise<WidgetConfig[]> {
    const response = await api.get<WidgetConfig[]>('/dashboard/widgets/')
    return response.data
  },

  /**
   * Update widget configuration
   */
  async updateWidgetConfig(config: WidgetConfig[]): Promise<void> {
    await api.post('/dashboard/widgets/', { widgets: config })
  },
}
```

---

## Real-Time Features

### WebSocket Integration (Future Enhancement)

```typescript
// src/hooks/useActivityFeed.ts (with WebSocket)

import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { dashboardService } from '@/services/dashboard.service'
import type { Activity } from '@/types/dashboard'

export function useActivityFeed(realTime: boolean = false) {
  const queryClient = useQueryClient()
  const [socket, setSocket] = useState<WebSocket | null>(null)

  const query = useQuery({
    queryKey: ['activities'],
    queryFn: () => dashboardService.getActivities({ limit: 50 }),
  })

  useEffect(() => {
    if (!realTime) return

    // Connect to WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/activities/')

    ws.onmessage = (event) => {
      const activity: Activity = JSON.parse(event.data)

      // Prepend new activity to cache
      queryClient.setQueryData<Activity[]>(['activities'], (old) => {
        if (!old) return [activity]
        return [activity, ...old]
      })

      // Show toast notification
      toast.info(`New activity: ${activity.title}`)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      // Fallback to polling
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [realTime, queryClient])

  return query
}
```

### Polling Fallback

```typescript
// Alternative: Polling for real-time updates

export function useActivityFeedPolling() {
  return useQuery({
    queryKey: ['activities'],
    queryFn: () => dashboardService.getActivities({ limit: 50 }),
    refetchInterval: 30 * 1000, // Poll every 30 seconds
    refetchIntervalInBackground: true, // Continue polling when tab not focused
  })
}
```

---

## User Flows

### Flow 1: Dashboard Load (All Users)

```
1. User logs in → Navigate to /dashboard
2. DashboardPage renders
3. Parallel data fetching:
   - Dashboard stats (vacation balance, etc.)
   - Activity feed (last 50 activities)
   - Notifications (unread only)
   - Upcoming events (next 30 days)
4. Show loading skeletons while fetching
5. Render widgets as data arrives
6. Start real-time updates (if enabled)
7. User sees personalized dashboard
```

### Flow 2: Notification Interaction

```
1. User sees notification badge (3 unread)
2. Clicks on bell icon
3. NotificationCenter slides in from right
4. Display notifications grouped by priority
5. User clicks on notification
6. Mark as read automatically
7. Navigate to related item (e.g., vacation request)
8. Badge count decrements
```

### Flow 3: Quick Action (Request Vacation)

```
1. User clicks "Request Vacation" quick action
2. Navigate to /vacation/new
3. Form pre-filled with today's date
4. User submits request
5. Success toast shown
6. Navigate back to dashboard
7. Activity feed updates with new activity
8. Stats widget updates (pending +1)
9. Notification sent to manager (if applicable)
```

### Flow 4: Manager Approval Workflow

```
1. Manager sees "5 pending approvals" on dashboard
2. Clicks on "Pending Approvals" widget
3. Navigate to approval queue
4. Manager reviews request
5. Approves or denies request
6. Activity feed updates
7. Employee receives notification
8. Dashboard stats update (pending -1)
```

---

## UI/UX Specifications

### Design Principles

1. **Glanceability:** Key metrics visible at a glance
2. **Actionability:** Quick actions prominently placed
3. **Personalization:** Role-based content
4. **Consistency:** Matches CarePlan design system
5. **Performance:** Optimistic updates, smooth animations

### Layout Grid

```
Desktop (>1024px):
┌──┬──┬──┬──┐
│1 │2 │3 │4 │  Stats cards (4 columns)
├──┴──┼──┴──┤
│  A  │  Q  │  Activity feed (2/3) + Quick Actions (1/3)
├─────┼─────┤
│  U  │  M  │  Upcoming (2/3) + Manager widget (1/3)
└─────┴─────┘

Tablet (768-1023px):
┌──┬──┐
│1 │2 │  Stats cards (2 columns)
├──┼──┤
│3 │4 │
├──┴──┤
│  A  │  Activity feed (full width)
├─────┤
│  Q  │  Quick Actions (full width)
├─────┤
│  U  │  Upcoming (full width)
└─────┘

Mobile (<768px):
┌────┐
│ 1  │  Stats cards (1 column, stacked)
├────┤
│ 2  │
├────┤
│ 3  │
├────┤
│ Q  │  Quick Actions
├────┤
│ A  │  Activity feed
├────┤
│ U  │  Upcoming
└────┘
```

### Color Palette

```typescript
export const DASHBOARD_COLORS = {
  stats: {
    vacation: 'text-blue-600 dark:text-blue-400',
    pending: 'text-yellow-600 dark:text-yellow-400',
    approved: 'text-green-600 dark:text-green-400',
    team: 'text-purple-600 dark:text-purple-400',
  },
  trend: {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600',
  },
  notification: {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-gray-500',
  },
} as const
```

---

## Performance Optimization

### Optimization Strategies

1. **Lazy Loading:**
   - Load widgets on demand
   - Defer non-critical widgets
   - Lazy load charts/analytics

2. **Data Fetching:**
   - Parallel requests for all widgets
   - Cache dashboard data (5 min)
   - Prefetch on hover/focus

3. **Real-Time Updates:**
   - WebSocket for instant updates
   - Polling fallback (30s interval)
   - Throttle update frequency

4. **Rendering:**
   - Virtual scrolling for activity feed
   - Memoize widget components
   - Optimize re-renders

5. **Caching:**
   - React Query caching
   - LocalStorage for widget config
   - Service Worker for offline

### Performance Metrics

- **LCP:** <2.5s (dashboard fully loaded)
- **FID:** <100ms (quick action click)
- **CLS:** <0.1 (stable layout)
- **Widget Load:** <500ms each
- **Real-time Latency:** <200ms (WebSocket)

---

## Implementation Plan

### Phase 1: Core Components (8 hours)

**Tasks:**
1. Create dashboard types and interfaces - 1h
2. Create dashboard service - 1.5h
3. Create React Query hooks - 2h
4. Build StatsCard component - 1h
5. Build DashboardGrid layout - 1h
6. Build QuickActions component - 0.5h
7. Create configuration file - 1h

**Deliverables:**
- Complete type system
- Working API integration
- Reusable dashboard components
- Basic dashboard layout

### Phase 2: Activity & Notifications (6 hours)

**Tasks:**
1. Build ActivityFeed component - 2h
2. Build ActivityItem component - 1h
3. Build NotificationCenter component - 2h
4. Build NotificationItem component - 0.5h
5. Real-time polling integration - 0.5h

**Deliverables:**
- Functional activity feed
- Working notification center
- Real-time updates (polling)

### Phase 3: Widgets (8 hours)

**Tasks:**
1. UpcomingVacations widget - 1.5h
2. PendingApprovals widget (manager) - 2h
3. TeamOverview widget (manager) - 2h
4. SystemMetrics widget (admin) - 1.5h
5. AnalyticsChart widget (admin) - 1h

**Deliverables:**
- All dashboard widgets
- Role-based visibility
- Interactive elements

### Phase 4: Polish & Integration (6 hours)

**Tasks:**
1. Dashboard header with search - 1h
2. Mobile responsive layout - 2h
3. Loading states and skeletons - 1h
4. Error handling - 0.5h
5. Accessibility improvements - 1h
6. Performance optimization - 0.5h

**Deliverables:**
- Fully responsive dashboard
- Polished UI/UX
- Production-ready

### Phase 5: Testing (4 hours)

**Tasks:**
1. Unit tests for components - 1.5h
2. Integration tests - 1h
3. E2E tests for workflows - 1h
4. Performance testing - 0.5h

**Deliverables:**
- >80% test coverage
- All critical paths tested
- Performance benchmarks met

**Total Estimated Time: 32 hours**

---

## Testing Strategy

### Unit Tests

```typescript
// StatsCard.test.tsx
describe('StatsCard', () => {
  it('displays metric correctly', () => {
    render(
      <StatsCard
        title="Vacation Balance"
        value="15 days"
        icon={<Calendar />}
      />
    )

    expect(screen.getByText('Vacation Balance')).toBeInTheDocument()
    expect(screen.getByText('15 days')).toBeInTheDocument()
  })

  it('shows trend indicator when provided', () => {
    render(
      <StatsCard
        title="Requests"
        value={10}
        trend={{ value: 20, direction: 'up' }}
      />
    )

    expect(screen.getByText('+20%')).toBeInTheDocument()
    expect(screen.getByTestId('trend-up-icon')).toBeInTheDocument()
  })

  it('calls action handler on button click', () => {
    const handleClick = jest.fn()
    render(
      <StatsCard
        title="Test"
        value={1}
        action={{ label: 'Click', onClick: handleClick }}
      />
    )

    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### Integration Tests

```typescript
// DashboardPage.integration.test.tsx
describe('DashboardPage Integration', () => {
  it('loads all dashboard data', async () => {
    render(<DashboardPage />)

    // Loading state
    expect(screen.getAllByTestId('skeleton')).toHaveLength(4)

    // Data loads
    await waitFor(() => {
      expect(screen.getByText('15 days')).toBeInTheDocument() // Vacation balance
      expect(screen.getByText('Recent Activity')).toBeInTheDocument()
      expect(screen.getByText('Quick Actions')).toBeInTheDocument()
    })
  })

  it('shows manager-specific widgets for managers', async () => {
    mockAuthContext({ role: 'MANAGER' })
    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Pending Approvals')).toBeInTheDocument()
      expect(screen.getByText('Team Overview')).toBeInTheDocument()
    })
  })

  it('updates activity feed in real-time', async () => {
    render(<DashboardPage />)

    // Initial activities load
    await waitFor(() => {
      expect(screen.getByText('Vacation approved')).toBeInTheDocument()
    })

    // Simulate new activity via WebSocket
    act(() => {
      mockWebSocket.emit('new_activity', newActivity)
    })

    // New activity appears
    expect(screen.getByText(newActivity.title)).toBeInTheDocument()
  })
})
```

### E2E Tests

```typescript
// dashboard.e2e.ts
test('dashboard workflow', async ({ page }) => {
  // Login
  await loginAsUser(page)

  // Dashboard loads
  await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible()

  // Stats visible
  await expect(page.getByText('Vacation Balance')).toBeVisible()
  await expect(page.getByText('15 days')).toBeVisible()

  // Quick action works
  await page.getByRole('button', { name: 'Request Vacation' }).click()
  await expect(page).toHaveURL('/vacation/new')

  // Back to dashboard
  await page.goto('/dashboard')

  // Open notifications
  await page.getByRole('button', { name: 'Notifications' }).click()
  await expect(page.getByText('Notifications')).toBeVisible()

  // Mark notification as read
  await page.getByRole('button', { name: 'Mark as Read' }).first().click()
  await expect(page.getByTestId('notification-badge')).toHaveText('2')
})
```

---

## Appendix

### Configuration File

```typescript
// src/config/dashboard.config.ts

export const DASHBOARD_CONFIG = {
  // Real-time updates
  POLLING_INTERVAL: 30 * 1000, // 30 seconds
  WEBSOCKET_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',

  // Activity feed
  MAX_ACTIVITIES: 50,
  ACTIVITY_PAGE_SIZE: 20,

  // Notifications
  MAX_NOTIFICATIONS: 100,
  NOTIFICATION_RETENTION_DAYS: 30,

  // Upcoming events
  UPCOMING_EVENTS_DAYS: 30,
  MAX_UPCOMING_EVENTS: 10,

  // Caching
  STATS_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  ACTIVITIES_STALE_TIME: 60 * 1000, // 1 minute
  NOTIFICATIONS_STALE_TIME: 30 * 1000, // 30 seconds

  // Performance
  SKELETON_COUNT: 4,
  ANIMATION_DURATION: 200, // ms

  // Widgets
  DEFAULT_WIDGETS: [
    { id: 'vacation-balance', type: 'vacation_balance', position: { row: 0, col: 0 } },
    { id: 'pending-requests', type: 'pending_requests', position: { row: 0, col: 1 } },
    { id: 'upcoming-events', type: 'upcoming_events', position: { row: 0, col: 2 } },
    { id: 'activity-feed', type: 'activity_feed', position: { row: 1, col: 0 } },
    { id: 'quick-actions', type: 'quick_actions', position: { row: 1, col: 1 } },
  ],
} as const
```

---

**End of Document**

*Next Steps: Review and approve design, then proceed to implementation.*
