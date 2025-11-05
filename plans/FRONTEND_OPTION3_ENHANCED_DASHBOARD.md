# Frontend Option 3: Enhanced Dashboard with Real Data

**Date:** 2025-11-05
**Priority:** MEDIUM
**Estimated Time:** 1-2 hours
**Status:** Ready to implement

---

## 🎯 Overview

Transform the basic dashboard into a dynamic, data-driven command center that provides:
- Real-time statistics and metrics
- Recent activity feed
- Quick actions that actually work
- Team insights (for managers)
- Personalized notifications
- Visual data representations

---

## 📋 Features Breakdown

### Core Features (Must Have)
1. **Real Statistics** - Fetch and display actual data
2. **Recent Activity Feed** - Latest actions (vacations, approvals, updates)
3. **Vacation Overview** - Visual balance and upcoming vacations
4. **Quick Actions** - Working buttons with proper navigation

### Enhanced Features (Should Have)
5. **Statistics Cards** - Multiple metric cards with icons
6. **Pending Tasks** - Action items requiring attention
7. **Team Calendar Widget** - Who's out this week
8. **Notifications Panel** - Unread notifications

### Manager Features (Nice to Have)
9. **Team Statistics** - Team size, availability, pending requests
10. **Approval Queue** - Quick approve/deny widget
11. **Team Activity** - What's happening in the team
12. **Coverage Alerts** - Staffing warnings

---

## 🏗️ Architecture

### Dashboard Layout
```
+--------------------------------------------------+
| Welcome back, John! 👋                           |
| Today is Monday, November 5, 2025                |
+--------------------------------------------------+

+-------------+  +-------------+  +-------------+
| Vacation    |  | Pending     |  | Team        |
| Balance     |  | Requests    |  | Status      |
| 15 days     |  | 3 requests  |  | 42 active   |
+-------------+  +-------------+  +-------------+

+--------------------------------------------------+
| Quick Actions                                    |
| [Request Vacation] [View Schedule] [Time Off]    |
+--------------------------------------------------+

+------------------------+  +----------------------+
| Recent Activity        |  | Upcoming Vacations   |
| • Vacation approved    |  | 📅 John - Dec 20-27  |
| • New employee added   |  | 📅 Jane - Dec 24-26  |
| • Location updated     |  | 📅 Bob - Dec 30-31   |
+------------------------+  +----------------------+

+--------------------------------------------------+
| Notifications (3 unread)                         |
| 🔔 Your vacation request was approved            |
| 🔔 New employee joined your team                 |
| 🔔 Reminder: Submit timesheet                    |
+--------------------------------------------------+
```

---

## 📝 Implementation Steps

### Step 1: Dashboard API & Types (15 min)

**Create:** `src/types/dashboard.ts`
```typescript
export interface DashboardStats {
  // Personal Stats
  vacation_balance: number
  vacation_total: number
  pending_requests: number
  upcoming_vacations: number

  // Team Stats (manager only)
  team_size?: number
  team_on_leave?: number
  pending_approvals?: number
  coverage_alerts?: number
}

export interface ActivityItem {
  id: number
  type: 'VACATION_REQUEST' | 'VACATION_APPROVED' | 'VACATION_DENIED' |
        'EMPLOYEE_ADDED' | 'PROFILE_UPDATED' | 'LOCATION_CHANGED'
  description: string
  user: {
    name: string
    avatar?: string
  }
  timestamp: string
  metadata?: Record<string, any>
}

export interface UpcomingVacation {
  id: number
  employee: {
    id: number
    name: string
    avatar?: string
  }
  start_date: string
  end_date: string
  total_days: number
}

export interface NotificationItem {
  id: number
  type: 'SUCCESS' | 'INFO' | 'WARNING' | 'ERROR'
  title: string
  message: string
  read: boolean
  created_at: string
  link?: string
}
```

**Create:** `src/services/dashboard.service.ts`
```typescript
import api from './api'
import type { DashboardStats, ActivityItem, UpcomingVacation } from '@/types/dashboard'

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const response = await api.get('/dashboard/stats/')
    return response.data
  },

  async getRecentActivity(limit = 10): Promise<ActivityItem[]> {
    const response = await api.get('/dashboard/activity/', {
      params: { limit }
    })
    return response.data
  },

  async getUpcomingVacations(limit = 5): Promise<UpcomingVacation[]> {
    const response = await api.get('/dashboard/upcoming-vacations/', {
      params: { limit }
    })
    return response.data
  }
}
```

---

### Step 2: Statistics Cards Component (20 min)

**File:** `src/components/dashboard/StatsCard.tsx`

**Design:**
```
+------------------+
| 📅 Vacation Days |
|                  |
|       15         |
|    remaining     |
|                  |
| +12% vs last yr  |
+------------------+
```

**Props:**
```typescript
interface StatsCardProps {
  icon: React.ComponentType
  label: string
  value: number | string
  sublabel?: string
  trend?: {
    value: number
    direction: 'up' | 'down'
    isPositive: boolean
  }
  color?: 'primary' | 'success' | 'warning' | 'destructive'
  onClick?: () => void
}
```

**Variants:**
- Primary (blue) - Default metrics
- Success (green) - Positive metrics
- Warning (yellow) - Attention needed
- Destructive (red) - Critical alerts

---

### Step 3: Recent Activity Feed (25 min)

**File:** `src/components/dashboard/ActivityFeed.tsx`

**Layout:**
```
+----------------------------------+
| Recent Activity                  |
+----------------------------------+
| 👤 John Doe                      |
| ✅ Vacation approved             |
| Dec 20-27 (5 days)               |
| 2 hours ago                      |
+----------------------------------+
| 👤 Jane Smith                    |
| 📝 Requested vacation            |
| Jan 15-20 (4 days)               |
| 5 hours ago                      |
+----------------------------------+
| 👤 Admin                         |
| ➕ New employee added            |
| Bob Wilson (EMP045)              |
| 1 day ago                        |
+----------------------------------+
| [View All Activity →]            |
+----------------------------------+
```

**Activity Types & Icons:**
- `VACATION_REQUEST` → 📝 Calendar icon
- `VACATION_APPROVED` → ✅ Check icon
- `VACATION_DENIED` → ❌ X icon
- `EMPLOYEE_ADDED` → ➕ Plus icon
- `PROFILE_UPDATED` → 📝 Edit icon
- `LOCATION_CHANGED` → 📍 Pin icon

**Features:**
- Avatar display
- Relative timestamps ("2 hours ago")
- Click to view details
- Color coding by type
- Load more / pagination

---

### Step 4: Quick Actions Widget (15 min)

**File:** `src/components/dashboard/QuickActions.tsx`

**Layout:**
```
+----------------------------------+
| Quick Actions                    |
+----------------------------------+
| [📅] Request Vacation            |
| [📊] View My Requests            |
| [👥] View Team                   |
| [📍] My Locations                |
+----------------------------------+
```

**Props:**
```typescript
interface QuickAction {
  icon: React.ComponentType
  label: string
  href: string
  description?: string
  badge?: number // For counts
  requiredRole?: EmployeeRole[]
}
```

**Actions by Role:**
- **All:** Request vacation, view requests, view profile
- **Manager:** Approve requests, view team, manage schedules
- **Admin:** Add employee, manage locations, system settings

---

### Step 5: Upcoming Vacations Widget (20 min)

**File:** `src/components/dashboard/UpcomingVacations.tsx`

**Layout:**
```
+----------------------------------+
| Who's Out This Week              |
+----------------------------------+
| 📅 Mon-Tue                       |
| 👤 John Doe                      |
| Main Office                      |
+----------------------------------+
| 📅 Wed-Fri                       |
| 👤 Jane Smith                    |
| Branch A                         |
+----------------------------------+
| 📅 Thu-Fri                       |
| 👤 Bob Wilson                    |
| Branch B                         |
+----------------------------------+
| [View Full Calendar →]           |
+----------------------------------+
```

**Features:**
- Show current week's vacations
- Group by date
- Show location for context
- Avatar display
- Navigate to calendar

---

### Step 6: Notifications Panel (20 min)

**File:** `src/components/dashboard/NotificationsPanel.tsx`

**Layout:**
```
+----------------------------------+
| Notifications (3 unread)         |
| [Mark all as read]               |
+----------------------------------+
| 🔔 Vacation Approved             |
| Your vacation request for        |
| Dec 20-27 has been approved      |
| 2 hours ago          [View]      |
+----------------------------------+
| 🔔 New Team Member               |
| Bob Wilson joined your team      |
| 1 day ago            [View]      |
+----------------------------------+
| 📬 No new notifications          |
+----------------------------------+
```

**Features:**
- Unread count badge
- Mark as read
- Type-specific icons
- Click to view details
- Toast notifications for new items

---

### Step 7: Manager Dashboard Enhancements (25 min)

**Additional Widgets for Managers:**

#### Approval Queue
```
+----------------------------------+
| Pending Approvals (5)            |
+----------------------------------+
| 👤 John Doe - 5 days             |
| Dec 20-27                        |
| [Approve] [Deny]                 |
+----------------------------------+
| 👤 Jane Smith - 3 days           |
| Jan 15-17                        |
| [Approve] [Deny]                 |
+----------------------------------+
| [View All Requests →]            |
+----------------------------------+
```

#### Team Statistics
```
+-------------+  +-------------+
| Team Size   |  | On Leave    |
| 42          |  | 3 (7%)      |
+-------------+  +-------------+

+-------------+  +-------------+
| Pending     |  | Coverage    |
| Requests    |  | Alert       |
| 5           |  | ⚠️ Low      |
+-------------+  +-------------+
```

#### Coverage Alerts
```
+----------------------------------+
| Coverage Alerts                  |
+----------------------------------+
| ⚠️ Branch A - Dec 24             |
| Only 2 staff scheduled           |
| Min required: 4                  |
+----------------------------------+
| ⚠️ Main Office - Dec 31          |
| Only 3 staff scheduled           |
| Min required: 5                  |
+----------------------------------+
```

---

## 🎨 Visual Enhancements

### Charts & Graphs
**Install chart library:**
```bash
npm install recharts
```

**Chart Options:**
1. **Vacation Usage Chart** - Bar chart showing monthly usage
2. **Team Availability** - Pie chart of available vs out
3. **Request Trends** - Line chart of requests over time

**Example:**
```typescript
<ResponsiveContainer width="100%" height={200}>
  <BarChart data={vacationData}>
    <Bar dataKey="days" fill="#3b82f6" />
    <XAxis dataKey="month" />
    <YAxis />
  </BarChart>
</ResponsiveContainer>
```

### Progress Bars
```typescript
<Progress
  value={(usedDays / totalDays) * 100}
  className="h-2"
/>
```

### Badges & Status Indicators
- Unread count badges
- Status indicators (online/offline)
- Priority flags
- New item indicators

---

## 🔌 Integration Points

### React Query Hooks
```typescript
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardService.getStats,
    refetchInterval: 5 * 60 * 1000 // Refresh every 5 min
  })
}

export function useRecentActivity() {
  return useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: () => dashboardService.getRecentActivity(10),
    refetchInterval: 2 * 60 * 1000 // Refresh every 2 min
  })
}

export function useUpcomingVacations() {
  return useQuery({
    queryKey: ['dashboard-upcoming-vacations'],
    queryFn: () => dashboardService.getUpcomingVacations(5)
  })
}
```

### Real-time Updates (Future)
```typescript
// WebSocket connection for real-time notifications
const useNotifications = () => {
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/notifications/')

    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data)
      setNotifications(prev => [notification, ...prev])
      toast.success(notification.message)
    }

    return () => ws.close()
  }, [])

  return notifications
}
```

---

## 🎯 Dashboard Variants

### Employee Dashboard
- **Focus:** Personal information
- **Widgets:** Vacation balance, my requests, team calendar
- **Actions:** Request vacation, view schedule

### Manager Dashboard
- **Focus:** Team oversight
- **Widgets:** Team stats, approval queue, coverage alerts
- **Actions:** Approve requests, view team, manage schedules

### Admin Dashboard
- **Focus:** System overview
- **Widgets:** All stats, system health, user activity
- **Actions:** Manage users, configure system, view reports

---

## 🧪 Testing Checklist

- [ ] Stats load correctly
- [ ] Activity feed updates
- [ ] Quick actions navigate properly
- [ ] Upcoming vacations display
- [ ] Notifications work
- [ ] Manager widgets show (role check)
- [ ] Refresh functionality works
- [ ] Loading states display
- [ ] Error states handle gracefully
- [ ] Mobile responsive
- [ ] Real-time updates (if implemented)

---

## 🎯 Success Criteria

1. ✅ Dashboard shows real data from API
2. ✅ Activity feed updates automatically
3. ✅ Quick actions work and navigate correctly
4. ✅ Statistics are accurate and current
5. ✅ Manager features visible to managers only
6. ✅ Responsive on all devices
7. ✅ Fast load times (<2s)
8. ✅ Proper loading/error states
9. ✅ Visual polish and consistency
10. ✅ Accessible and keyboard navigable

---

## 🚀 Implementation Order

**Total Time: 1-2 hours**

1. **Setup (15 min):** Types, API service, hooks
2. **Stats Cards (20 min):** Create reusable stats card component
3. **Activity Feed (25 min):** Build activity feed with real data
4. **Quick Actions (15 min):** Working action buttons
5. **Polish (20 min):** Upcoming vacations, notifications, responsive

**Manager features can be added incrementally.**

---

## 📦 Additional Dependencies

**Charts (Optional):**
```bash
npm install recharts
```

**Icons:**
Already have `lucide-react` ✅

**Date formatting:**
Already have `date-fns` ✅

---

## 🎨 Design System

**Colors:**
- Primary: Stats cards, actions
- Success: Approved, positive metrics
- Warning: Pending, attention needed
- Destructive: Denied, critical alerts
- Muted: Inactive, secondary info

**Spacing:**
- Cards: 4-6 gap
- Sections: 8 gap
- Widgets: 16px padding

**Typography:**
- Headers: 2xl bold
- Metrics: 3xl bold
- Labels: sm medium
- Body: base regular

---

**Ready for implementation after Options 1 & 2!** 🎉
