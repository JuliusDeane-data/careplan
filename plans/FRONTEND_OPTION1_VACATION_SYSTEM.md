# Frontend Option 1: Vacation Request System

**Date:** 2025-11-05
**Priority:** HIGH
**Estimated Time:** 2-3 hours
**Status:** Ready to implement

---

## 🎯 Overview

Build a complete vacation request and management system that allows employees to:
- Request vacation time
- View their vacation requests (pending, approved, denied)
- See their vacation calendar
- Track vacation balance

Managers will additionally be able to:
- View team vacation requests
- Approve/deny requests
- See team calendar

---

## 📋 Features Breakdown

### Core Features (Must Have)
1. **Vacation Request Form** - Create new vacation requests
2. **Vacation List View** - See all your requests with status
3. **Vacation Calendar** - Visual calendar showing approved vacations
4. **Balance Tracking** - Real-time vacation days remaining

### Enhanced Features (Should Have)
5. **Request Details Modal** - View full details of a request
6. **Filter & Search** - Filter by status, date range
7. **Status Badges** - Visual indicators for request status

### Manager Features (Nice to Have)
8. **Team Requests View** - See all team vacation requests
9. **Approve/Deny Actions** - Quick action buttons
10. **Team Calendar** - See who's out when

---

## 🏗️ Architecture

### Page Structure
```
/vacation
  ├── /new                    → VacationRequestPage
  ├── /                       → VacationListPage (my requests)
  ├── /calendar              → VacationCalendarPage (my calendar)
  └── /team                   → TeamVacationPage (manager only)
```

### Component Hierarchy
```
VacationRequestPage
  └── VacationRequestForm
      ├── DateRangePicker (shadcn calendar)
      ├── ReasonTextarea
      └── SubmitButton

VacationListPage
  ├── VacationFilters
  ├── VacationStats (balance, pending count)
  └── VacationCard[] (list of requests)
      ├── StatusBadge
      ├── DateDisplay
      └── ActionButtons

VacationCalendarPage
  └── VacationCalendar
      ├── MonthNavigation
      ├── CalendarGrid
      └── VacationEventCard[]
```

### API Integration
```typescript
// API endpoints to use:
GET    /api/vacation/requests/          // List my requests
POST   /api/vacation/requests/          // Create request
GET    /api/vacation/requests/{id}/     // Get details
DELETE /api/vacation/requests/{id}/     // Cancel request
GET    /api/vacation/requests/balance/  // Get balance

// Manager endpoints:
GET    /api/vacation/requests/?status=PENDING    // Team requests
POST   /api/vacation/requests/{id}/approve/      // Approve
POST   /api/vacation/requests/{id}/deny/         // Deny
```

---

## 📝 Implementation Steps

### Step 1: Setup & Types (15 min)

**Create type definitions:**
```typescript
// src/types/vacation.ts
export interface VacationRequest {
  id: number
  employee: {
    id: number
    name: string
    employee_id: string
  }
  start_date: string
  end_date: string
  total_days: number
  reason?: string
  status: 'PENDING' | 'APPROVED' | 'DENIED' | 'CANCELLED'
  created_at: string
  approved_by?: {
    id: number
    name: string
  }
  approved_at?: string
  denial_reason?: string
}

export interface VacationBalance {
  total_days: number
  remaining_days: number
  used_days: number
  pending_days: number
}

export interface VacationRequestCreate {
  start_date: string
  end_date: string
  reason?: string
}
```

**Create API service:**
```typescript
// src/services/vacation.service.ts
import api from './api'
import type { VacationRequest, VacationBalance, VacationRequestCreate } from '@/types/vacation'

export const vacationService = {
  async getMyRequests(): Promise<VacationRequest[]> {
    const response = await api.get('/vacation/requests/')
    return response.data.results || response.data
  },

  async createRequest(data: VacationRequestCreate): Promise<VacationRequest> {
    const response = await api.post('/vacation/requests/', data)
    return response.data
  },

  async getBalance(): Promise<VacationBalance> {
    const response = await api.get('/vacation/requests/balance/')
    return response.data
  },

  async cancelRequest(id: number): Promise<void> {
    await api.delete(`/vacation/requests/${id}/`)
  },

  async approveRequest(id: number): Promise<VacationRequest> {
    const response = await api.post(`/vacation/requests/${id}/approve/`)
    return response.data
  },

  async denyRequest(id: number, reason: string): Promise<VacationRequest> {
    const response = await api.post(`/vacation/requests/${id}/deny/`, { reason })
    return response.data
  }
}
```

---

### Step 2: Vacation Request Form (45 min)

**File:** `src/pages/vacation/VacationRequestPage.tsx`

**Features:**
- Date range picker (start/end date)
- Reason textarea
- Real-time validation
- Days calculation
- Balance check
- Success/error handling

**Validation Rules:**
- Start date must be at least 14 days in future
- End date must be after start date
- Must have sufficient vacation balance
- No overlapping requests

**Form Schema (Zod):**
```typescript
const vacationRequestSchema = z.object({
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  reason: z.string().optional(),
}).refine((data) => {
  const start = new Date(data.start_date)
  const end = new Date(data.end_date)
  return end > start
}, {
  message: "End date must be after start date",
  path: ["end_date"]
})
```

**UI Components Needed:**
- `<Calendar>` from shadcn/ui for date picker
- `<Textarea>` for reason
- `<Alert>` for validation errors
- `<Button>` for submit

---

### Step 3: Vacation List View (30 min)

**File:** `src/pages/vacation/VacationListPage.tsx`

**Layout:**
```
+----------------------------------+
| Vacation Balance Card            |
| 15 days remaining / 30 total     |
+----------------------------------+

| [All] [Pending] [Approved]       |
| [Denied] [Cancelled]             |
+----------------------------------+

+----------------------------------+
| Request Card                     |
| Dec 20 - Dec 27 (5 days)         |
| Status: [PENDING]                |
| Requested: 2 days ago            |
| [View Details] [Cancel]          |
+----------------------------------+
```

**Features:**
- Status filter tabs
- Sort by date
- Pagination
- Cancel pending requests
- View details modal

**Status Badge Colors:**
- PENDING → Yellow/Warning
- APPROVED → Green/Success
- DENIED → Red/Destructive
- CANCELLED → Gray/Muted

---

### Step 4: Vacation Card Component (20 min)

**File:** `src/components/vacation/VacationCard.tsx`

**Props:**
```typescript
interface VacationCardProps {
  request: VacationRequest
  onCancel?: (id: number) => void
  onApprove?: (id: number) => void
  onDeny?: (id: number) => void
  showActions?: boolean
}
```

**Display:**
- Date range with icon
- Total days badge
- Status badge
- Reason (truncated)
- Action buttons (contextual)
- Approved by (if applicable)

---

### Step 5: Vacation Calendar View (45 min)

**File:** `src/pages/vacation/VacationCalendarPage.tsx`

**Calendar Library:** Use `date-fns` + custom grid or install `react-big-calendar`

**Features:**
- Month view (default)
- Week view
- Day view
- Show approved vacations on calendar
- Color-coded events
- Click event to see details
- Navigate months

**Event Display:**
- Full day events for vacation days
- Hover tooltip with details
- Different colors for own vs team vacations

---

### Step 6: Vacation Balance Component (15 min)

**File:** `src/components/vacation/VacationBalance.tsx`

**Display:**
```
+---------------------------+
| Vacation Balance          |
+---------------------------+
| Available:  15 days       |
| Used:       10 days       |
| Pending:     5 days       |
+---------------------------+
| Total:      30 days/year  |
+---------------------------+
| [Request Vacation]        |
+---------------------------+
```

**Visual:**
- Progress bar showing used/remaining
- Numbers prominently displayed
- Quick action button

---

### Step 7: Manager Team View (30 min) [Optional]

**File:** `src/pages/vacation/TeamVacationPage.tsx`

**Features:**
- See all team requests
- Filter by employee
- Filter by status
- Approve/deny with one click
- Batch actions
- Team calendar view

**Layout:**
```
+----------------------------------+
| Team Vacation Requests           |
| [Pending: 5] [Approved: 12]      |
+----------------------------------+

+----------------------------------+
| John Doe - EMP001                |
| Dec 20 - Dec 27 (5 days)         |
| Reason: Family vacation          |
| [Approve] [Deny]                 |
+----------------------------------+
```

---

## 🎨 UI/UX Considerations

### Design Principles
1. **Clear Status Indicators** - Use colors and badges
2. **Quick Actions** - One-click approve/deny
3. **Mobile Responsive** - Works on all devices
4. **Loading States** - Skeleton loaders while fetching
5. **Error Handling** - Clear error messages

### Accessibility
- Keyboard navigation
- ARIA labels
- Focus management
- Screen reader support

### Performance
- Paginate long lists
- Lazy load calendar events
- Cache balance data
- Optimistic updates

---

## 🔌 Integration Points

### React Query Hooks
```typescript
// src/hooks/useVacationRequests.ts
export function useVacationRequests() {
  return useQuery({
    queryKey: ['vacation-requests'],
    queryFn: vacationService.getMyRequests
  })
}

export function useVacationBalance() {
  return useQuery({
    queryKey: ['vacation-balance'],
    queryFn: vacationService.getBalance
  })
}

export function useCreateVacationRequest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: vacationService.createRequest,
    onSuccess: () => {
      queryClient.invalidateQueries(['vacation-requests'])
      queryClient.invalidateQueries(['vacation-balance'])
    }
  })
}
```

### Routing
```typescript
// Update App.tsx routes
<Route path="/vacation">
  <Route index element={<VacationListPage />} />
  <Route path="new" element={<VacationRequestPage />} />
  <Route path="calendar" element={<VacationCalendarPage />} />
  <Route path="team" element={<TeamVacationPage />} />
</Route>
```

---

## 🧪 Testing Checklist

### Manual Testing
- [ ] Request vacation with valid dates
- [ ] Request with insufficient balance (should fail)
- [ ] Request with overlapping dates (should fail)
- [ ] Cancel pending request
- [ ] View request details
- [ ] Filter requests by status
- [ ] View calendar
- [ ] Manager approve request
- [ ] Manager deny request

### Edge Cases
- [ ] Request on weekends/holidays
- [ ] Request spanning year boundary
- [ ] Request same day start/end
- [ ] Very long vacation (30+ days)
- [ ] Concurrent requests

---

## 📦 Dependencies

**Already installed:**
- ✅ react-hook-form
- ✅ zod
- ✅ @hookform/resolvers
- ✅ date-fns
- ✅ @tanstack/react-query
- ✅ axios
- ✅ shadcn/ui components

**May need to install:**
```bash
# For calendar view (optional)
npm install react-big-calendar
npm install @types/react-big-calendar

# Or build custom with date-fns (recommended)
# No additional installs needed
```

---

## 🎯 Success Criteria

**Feature is complete when:**
1. ✅ Can create vacation request from form
2. ✅ Can view list of all requests
3. ✅ Can see vacation balance
4. ✅ Can cancel pending requests
5. ✅ Can view calendar of approved vacations
6. ✅ Managers can approve/deny requests
7. ✅ All validations work correctly
8. ✅ Responsive on mobile
9. ✅ Loading states implemented
10. ✅ Error handling works

**Quality Checks:**
- [ ] No TypeScript errors
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Accessible (keyboard navigation)
- [ ] Fast load times (<2s)
- [ ] Clean, readable code
- [ ] Proper error boundaries

---

## 📈 Future Enhancements

**Phase 2:**
- Recurring vacation (annual holidays)
- Email notifications on status change
- Vacation request templates
- Conflict detection with team calendar
- Export to ICS/Google Calendar
- Vacation request notes/comments
- Approval workflow (multi-level)
- Vacation history analytics

**Phase 3:**
- Mobile app integration
- Push notifications
- Vacation trading between employees
- Automated approval rules
- Integration with payroll
- Vacation carryover rules
- Time-off types (sick, personal, etc.)

---

## 🚀 Implementation Order

1. **Day 1 (1.5 hours):**
   - Setup types and API service
   - Create request form
   - Create list view
   - Test basic flow

2. **Day 2 (1 hour):**
   - Add balance component
   - Add status filters
   - Add cancel functionality
   - Polish UI

3. **Day 3 (Optional, 30min):**
   - Add calendar view
   - Add manager features
   - Final testing and polish

---

**Ready to start implementation!** 🎉
