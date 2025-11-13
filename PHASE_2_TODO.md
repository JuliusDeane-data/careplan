# CarePlan Development TODO List - PHASE 2
## Shift Scheduling Foundation

**Created:** January 2025
**Based on:** ICU_MANAGER_REQUIREMENTS.md (TIER 1 Requirements)
**Previous Phase:** Phase 1 - Certification & Skills Foundation ✅ COMPLETED
**Approach:** Build robust shift scheduling with ICU-specific rules
**Focus:** 24/7/365 operations, minimum staffing ratios, compliance enforcement

---

## Phase 2 Overview

**Priority:** TIER 1 - CRITICAL
**Est. Time:** 6-8 hours with quality focus
**Business Value:** Core operational capability - cannot run ICU without scheduling

### Why These Features Now:
1. **Builds on Phase 1:** Leverages certification data for scheduling rules
2. **Core Operations:** Shift scheduling is the heart of workforce management
3. **Compliance Critical:** Minimum ratios are legal requirements
4. **Foundation for Phase 3:** Advanced features need basic scheduling first
5. **Immediate Value:** Managers can start using it on day one

---

## DEVELOPER TODO LIST - PHASE 2

### Task 1: Shift Models and Patterns
**Files:** `apps/shifts/models.py` (new app)
**Priority:** P0 (Blocking all shift work)
**Estimated Time:** 60 minutes

**Requirements:**

Create `Shift` model:
- `location` (ForeignKey to Location)
- `shift_type` (CharField - choices: DAY, NIGHT, ON_CALL)
- `start_time` (TimeField - e.g., 07:00)
- `end_time` (TimeField - e.g., 19:00)
- `date` (DateField)
- `required_staff_count` (IntegerField - minimum required)
- `required_rn_count` (IntegerField - minimum RNs required)
- `required_charge_nurse` (BooleanField)
- `notes` (TextField, optional)
- `is_published` (BooleanField - false = draft)

Create `ShiftAssignment` model:
- `shift` (ForeignKey to Shift)
- `employee` (ForeignKey to User)
- `role` (CharField - NURSE, CHARGE_NURSE, CNA, ON_CALL)
- `status` (CharField - SCHEDULED, CONFIRMED, CANCELLED, NO_SHOW)
- `assigned_by` (ForeignKey to User)
- `assigned_at` (DateTimeField)
- `notes` (TextField, optional)

Create `ShiftTemplate` model (for recurring patterns):
- `name` (CharField - e.g., "4-Week Rotation A")
- `location` (ForeignKey)
- `day_of_week` (IntegerField 0-6)
- `shift_type` (CharField)
- `start_time` (TimeField)
- `end_time` (TimeField)
- `required_staff_count` (IntegerField)
- `is_active` (BooleanField)

Add helper methods:
- `shift.get_duration_hours()` - calculate shift length
- `shift.get_assigned_count()` - count assigned staff
- `shift.is_fully_staffed()` - check if requirements met
- `shift.get_coverage_percentage()` - staffing level %
- `assignment.calculate_hours()` - for payroll
- `assignment.conflicts_with_other_shifts()` - check overlaps

Add validation methods:
- `validate_minimum_rest_period()` - 11 hours between shifts (EU directive)
- `validate_certification_requirements()` - all assigned staff have required certs
- `validate_max_consecutive_nights()` - no more than 4 nights in a row
- `validate_skill_mix()` - at least 60% RN, max 40% CNA

**Acceptance Criteria:**
- ✅ Models migrate successfully
- ✅ All constraints enforced at database level
- ✅ Indexes on date, employee, shift_type for performance
- ✅ Comprehensive docstrings
- ✅ Admin interface works for basic CRUD

---

### Task 2: Shift Scheduling API
**Files:** `apps/api/serializers/shifts.py`, `apps/api/views/shifts.py`
**Priority:** P0
**Estimated Time:** 75 minutes

**Requirements:**

Create serializers:
- `ShiftSerializer` - full shift data with assignments
- `ShiftListSerializer` - lightweight for calendar views
- `ShiftAssignmentSerializer` - assignment details
- `ShiftTemplateSerializer` - template management
- `BulkAssignmentSerializer` - assign multiple staff at once

Create ViewSets:
- `ShiftViewSet`:
  - `GET /api/shifts/` - list shifts (filterable by date range, location, type)
  - `POST /api/shifts/` - create shift (manager/admin only)
  - `PATCH /api/shifts/{id}/` - update shift
  - `DELETE /api/shifts/{id}/` - delete shift (unpublished only)
  - `GET /api/shifts/calendar/` - calendar view (start_date, end_date params)
  - `GET /api/shifts/understaffed/` - shifts below minimum requirements
  - `POST /api/shifts/publish/` - publish draft shifts
  - `POST /api/shifts/from-template/` - generate shifts from template

- `ShiftAssignmentViewSet`:
  - `POST /api/shifts/{id}/assignments/` - assign employee to shift
  - `DELETE /api/shifts/{id}/assignments/{assignment_id}/` - unassign
  - `PATCH /api/shifts/{id}/assignments/{assignment_id}/` - update status
  - `POST /api/shifts/{id}/assignments/bulk/` - bulk assign multiple employees

Custom actions:
- `@action POST /api/shifts/{id}/validate/` - validate shift meets all rules
- `@action GET /api/shifts/my-schedule/` - employee's own schedule
- `@action GET /api/shifts/conflicts/` - check for scheduling conflicts
- `@action POST /api/shifts/{id}/notify-staff/` - send notifications

**Permissions:**
- Employees can view own schedule
- Managers can view/edit shifts at their location
- Admins can view/edit all shifts
- Only managers/admins can publish shifts

**Acceptance Criteria:**
- ✅ RESTful API design
- ✅ Proper validation (certification checks, rest periods, etc.)
- ✅ Error messages are helpful
- ✅ Optimized queries (select_related, prefetch_related)
- ✅ Pagination for large result sets

---

### Task 3: Shift Scheduling Frontend Types
**Files:** `frontend/src/types/index.ts`
**Priority:** P0
**Estimated Time:** 30 minutes

**Requirements:**

Add TypeScript interfaces:
```typescript
export type ShiftType = 'DAY' | 'NIGHT' | 'ON_CALL'
export type ShiftStatus = 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'NO_SHOW'
export type ShiftRole = 'NURSE' | 'CHARGE_NURSE' | 'CNA' | 'ON_CALL'

export interface Shift {
  id: number
  location: Location
  shift_type: ShiftType
  start_time: string
  end_time: string
  date: string
  required_staff_count: number
  required_rn_count: number
  required_charge_nurse: boolean
  assigned_count: number
  coverage_percentage: number
  is_fully_staffed: boolean
  is_published: boolean
  notes?: string
  assignments: ShiftAssignment[]
  created_at: string
  updated_at: string
}

export interface ShiftAssignment {
  id: number
  shift: Shift | number
  employee: User
  role: ShiftRole
  status: ShiftStatus
  assigned_by: User
  assigned_at: string
  notes?: string
}

export interface ShiftTemplate {
  id: number
  name: string
  location: Location
  day_of_week: number
  shift_type: ShiftType
  start_time: string
  end_time: string
  required_staff_count: number
  is_active: boolean
}

export interface CreateShift {
  location_id: number
  shift_type: ShiftType
  start_time: string
  end_time: string
  date: string
  required_staff_count: number
  required_rn_count: number
  required_charge_nurse: boolean
  notes?: string
}

export interface AssignToShift {
  employee_id: number
  role: ShiftRole
  notes?: string
}

export interface ShiftValidationResult {
  is_valid: boolean
  errors: string[]
  warnings: string[]
}

export interface ShiftCalendarDay {
  date: string
  shifts: Shift[]
  total_assigned: number
  total_required: number
  is_understaffed: boolean
}
```

**Acceptance Criteria:**
- ✅ Types match backend models exactly
- ✅ Proper enums for choices
- ✅ Optional fields marked correctly

---

### Task 4: Shift Service Layer
**Files:** `frontend/src/services/shift.service.ts`
**Priority:** P0
**Estimated Time:** 45 minutes

**Requirements:**

Create service methods:
```typescript
shiftService = {
  // Shift CRUD
  getShifts(filters: { start_date?, end_date?, location?, shift_type? })
  getShift(id: number)
  createShift(data: CreateShift)
  updateShift(id: number, data: Partial<CreateShift>)
  deleteShift(id: number)
  publishShift(id: number)

  // Calendar & Views
  getCalendar(startDate: string, endDate: string, locationId?: number)
  getMySchedule(startDate?: string, endDate?: string)
  getUnderstaffedShifts(startDate?: string, endDate?: string)

  // Assignments
  assignToShift(shiftId: number, data: AssignToShift)
  unassignFromShift(shiftId: number, assignmentId: number)
  bulkAssign(shiftId: number, employeeIds: number[], role: ShiftRole)
  updateAssignmentStatus(assignmentId: number, status: ShiftStatus)

  // Validation & Utilities
  validateShift(shiftId: number)
  checkConflicts(employeeId: number, shiftDate: string)
  notifyStaff(shiftId: number)

  // Templates
  getTemplates(locationId?: number)
  createTemplate(data: ShiftTemplate)
  generateFromTemplate(templateId: number, startDate: string, endDate: string)
}
```

**Acceptance Criteria:**
- ✅ Proper error handling
- ✅ TypeScript types enforced
- ✅ Consistent API patterns

---

### Task 5: React Query Hooks for Shifts
**Files:** `frontend/src/hooks/useShifts.ts`
**Priority:** P0
**Estimated Time:** 45 minutes

**Requirements:**

Create hooks:
- `useShifts(filters)` - query hook with filtering
- `useShift(id)` - single shift details
- `useMySchedule(startDate, endDate)` - employee's schedule
- `useShiftCalendar(startDate, endDate, locationId)` - calendar view
- `useUnderstaffedShifts(dateRange)` - staffing alerts
- `useCreateShift()` - mutation for creating shifts
- `useUpdateShift()` - mutation for updates
- `useDeleteShift()` - mutation for deletion
- `useAssignToShift()` - mutation for assignments
- `useBulkAssign()` - mutation for bulk assignments
- `usePublishShift()` - mutation to publish shifts
- `useShiftTemplates(locationId)` - query templates
- `useGenerateFromTemplate()` - mutation to generate shifts

Cache strategy:
- Invalidate shifts when assignments change
- Invalidate my-schedule when any shift changes
- Refetch calendar on successful mutations
- Optimistic updates for assignment changes

**Acceptance Criteria:**
- ✅ Proper query keys for caching
- ✅ Stale time configured appropriately
- ✅ Mutation side effects handled correctly

---

### Task 6: Shift Calendar Component
**Files:** `frontend/src/components/shifts/ShiftCalendar.tsx`
**Priority:** P1
**Estimated Time:** 90 minutes

**Requirements:**

Create calendar view component:
- Weekly or monthly view toggle
- Color-coded shifts (day = yellow, night = blue, on-call = purple)
- Visual indicators:
  - Fully staffed (green border)
  - Understaffed (orange/red border)
  - Unpublished (dashed border)
- Click on day to see shift details
- Staffing level bars showing assigned/required
- Filter by location
- Navigate prev/next week or month
- "Today" button to return to current date

Display for each shift:
- Shift type and time
- Assigned count / Required count
- Names of assigned staff (truncated with tooltip for full list)
- Warning icons for violations

**Acceptance Criteria:**
- ✅ Responsive design (works on tablet/mobile)
- ✅ Loading states while fetching
- ✅ Clear visual hierarchy
- ✅ Accessible (keyboard navigation, screen readers)

---

### Task 7: Shift Detail Modal
**Files:** `frontend/src/components/shifts/ShiftDetailModal.tsx`
**Priority:** P1
**Estimated Time:** 60 minutes

**Requirements:**

Modal showing full shift details:
- Shift information (type, time, date, location)
- Requirements (staff count, RN count, charge nurse needed)
- Assigned staff list with roles
- For each assignment:
  - Employee name and photo/initials
  - Role badge
  - Status badge
  - Certifications status (valid/expiring/expired)
  - Actions (remove assignment, change role)
- Unassigned slots visualization
- "Add Staff" button (opens staff selector)
- Validation warnings (if any rules violated)
- Publish button (if manager and unpublished)
- Edit/Delete buttons (if has permission)

**Acceptance Criteria:**
- ✅ Clear visual layout
- ✅ Actions disabled if no permission
- ✅ Confirmation dialogs for destructive actions
- ✅ Real-time updates when assignments change

---

### Task 8: Staff Assignment Selector
**Files:** `frontend/src/components/shifts/StaffSelector.tsx`
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**

Component to assign staff to shifts:
- Search/filter available employees
- Show employee availability (not already assigned that day)
- Display employee certifications
- Show conflicts (if assigning would violate rules):
  - Minimum rest period violation
  - Already assigned to another shift
  - Missing required certifications
  - Would exceed max consecutive nights
- Select role (Nurse, Charge Nurse, CNA)
- Bulk select (assign multiple at once)
- Visual indicators:
  - Available (green)
  - Has conflict (yellow - show warning)
  - Not qualified (red - cannot assign)

**Acceptance Criteria:**
- ✅ Fast search/filter
- ✅ Clear conflict warnings
- ✅ Prevents invalid assignments
- ✅ Bulk operations work smoothly

---

### Task 9: My Schedule Page (Employee View)
**Files:** `frontend/src/pages/shifts/MySchedulePage.tsx`
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**

Employee's personal schedule view:
- Calendar view of assigned shifts
- List view option (sortable by date)
- Filter by date range
- Visual differentiation of shift types
- Show for each shift:
  - Date and day of week
  - Shift type and time
  - Location
  - Duration (hours)
  - Role (if charge nurse, highlight)
  - Co-workers assigned (optional)
- Statistics card:
  - Hours scheduled this week
  - Hours scheduled this month
  - Night shifts this month
  - Weekends this month
- Download/print schedule option
- iCal export option

**Acceptance Criteria:**
- ✅ Fast and responsive
- ✅ Clear at a glance
- ✅ Works well on mobile (primary use case)
- ✅ Offline capability (show cached schedule)

---

### Task 10: Shift Management Page (Manager View)
**Files:** `frontend/src/pages/shifts/ShiftManagementPage.tsx`
**Priority:** P1
**Estimated Time:** 75 minutes

**Requirements:**

Manager's shift management dashboard:
- **Main Calendar:** ShiftCalendar component showing all shifts
- **Quick Stats Panel:**
  - Understaffed shifts (next 7 days)
  - Unpublished shifts
  - Total hours scheduled (this week/month)
  - Coverage percentage
- **Alerts Section:**
  - Shifts below minimum staffing
  - Scheduling rule violations
  - Staff with certification expiring (affects scheduling)
- **Quick Actions:**
  - Create new shift
  - Generate from template
  - Publish all draft shifts
  - View understaffed shifts
  - View conflicts report
- **Filters:**
  - Location (if manager has multiple)
  - Shift type
  - Published vs. draft
  - Date range

**Acceptance Criteria:**
- ✅ Manager can complete most tasks from this page
- ✅ Real-time updates when shifts change
- ✅ Alerts are prominent and actionable
- ✅ Performance is good even with 100+ shifts

---

### Task 11: Create/Edit Shift Form
**Files:** `frontend/src/components/shifts/ShiftForm.tsx`
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**

Form for creating/editing shifts:
- Location selector (if admin with multiple locations)
- Date picker
- Shift type selector (Day, Night, On-Call)
- Time pickers (start time, end time)
  - Pre-fill based on shift type (Day = 07:00-19:00, Night = 19:00-07:00)
- Required staff count (number input)
- Required RN count (number input, must be <= total count)
- Charge nurse required (checkbox)
- Notes (textarea)
- Save as draft vs. Publish immediately
- For editing:
  - Warning if shift is already published
  - Show current assignments
  - Prevent changes that would invalidate assignments

Validation:
- End time must be after start time (or next day for overnight)
- RN count <= total count
- Required counts > 0
- Date cannot be in the past (for new shifts)

**Acceptance Criteria:**
- ✅ Intuitive UX
- ✅ Real-time validation
- ✅ Clear error messages
- ✅ Smart defaults

---

### Task 12: Shift Template Management
**Files:** `frontend/src/pages/shifts/ShiftTemplatesPage.tsx`
**Priority:** P2
**Estimated Time:** 60 minutes

**Requirements:**

Page to manage recurring shift patterns:
- List of existing templates
- Create new template form
- Edit/delete templates
- Preview template (what shifts it would create)
- Generate shifts from template:
  - Select template
  - Choose date range
  - Preview shifts that will be created
  - Confirm and create
- Templates show:
  - Name
  - Location
  - Day of week
  - Shift type and time
  - Required staff counts
  - Status (active/inactive)

Example templates:
- "ICU-1 4-Week Rotation"
- "Weekend Coverage Pattern"
- "Holiday Schedule"

**Acceptance Criteria:**
- ✅ Easy to create complex patterns
- ✅ Preview before creating actual shifts
- ✅ Can modify template without affecting existing shifts

---

### Task 13: Staffing Dashboard Widget
**Files:** `frontend/src/components/shifts/StaffingDashboardWidget.tsx`
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**

Dashboard widget showing staffing status:
- **For Next 24 Hours:**
  - Current shift staffing level
  - Next shift staffing level
  - Alerts if understaffed
- **For Next 7 Days:**
  - Bar chart showing coverage percentage by day
  - Red bars if any day < 80% staffed
- **Quick Stats:**
  - Open shifts (not fully staffed)
  - Published vs. draft shifts
  - Total staff hours scheduled
- Click through to Shift Management Page

Add to main DashboardPage for managers/admins

**Acceptance Criteria:**
- ✅ Glanceable (info visible in 2 seconds)
- ✅ Actionable (click to drill down)
- ✅ Updates in real-time

---

### Task 14: Update ProfilePage with Shift Info
**Files:** `frontend/src/pages/ProfilePage.tsx`
**Priority:** P2
**Estimated Time:** 20 minutes

**Requirements:**

Replace "My Shifts" placeholder section with real data:
- Show next 3 upcoming shifts
- Link to "View Full Schedule" (My Schedule Page)
- Quick stats:
  - Hours scheduled this week
  - Next shift (date, time, location)

**Acceptance Criteria:**
- ✅ Integrates seamlessly
- ✅ Loading states
- ✅ Click through works

---

### Task 15: Shift Notifications System
**Files:** `apps/shifts/notifications.py`, `apps/shifts/tasks.py`
**Priority:** P2
**Estimated Time:** 45 minutes

**Requirements:**

Notification system for shift events:
- **When shift is published:**
  - Notify all assigned staff
  - Include shift details, location, time
- **When assigned to shift:**
  - Notify employee immediately
  - Include shift details
- **When removed from shift:**
  - Notify employee with reason
- **When shift is cancelled:**
  - Notify all assigned staff
- **Shift reminders:**
  - 24 hours before shift starts
  - 2 hours before shift starts (optional)

Use existing notification infrastructure
Store in database (Notification model)
Could add email/SMS later

**Acceptance Criteria:**
- ✅ Notifications send correctly
- ✅ Users can view in notification center
- ✅ Opt-out preferences respected

---

### Task 16: Shift Conflict Detection and Warnings
**Files:** `apps/shifts/validators.py`, frontend validation
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**

Comprehensive conflict checking:

Backend validators:
- `validate_minimum_rest_period()` - 11 hours between shifts
- `validate_max_consecutive_nights()` - no more than 4 nights
- `validate_max_hours_per_week()` - 48 hours averaged over 17 weeks
- `validate_required_certifications()` - staff has active certs for shift
- `validate_overlapping_shifts()` - not assigned to two shifts at once
- `validate_charge_nurse_qualified()` - charge nurse has 5+ years experience

Frontend warnings:
- Show conflicts before assignment
- Color-code severity (error vs. warning)
- Errors block assignment
- Warnings allow override with manager approval
- Display specific rule violated

**Acceptance Criteria:**
- ✅ All EU Working Time Directive rules enforced
- ✅ ICU-specific rules enforced
- ✅ Clear error messages explain violations
- ✅ Managers can see all violations in conflict report

---

### Task 17: Integration with Existing Features
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**

Connect shifts with existing features:
- **Vacation Integration:**
  - Cannot assign to shift if on approved vacation
  - Show vacation requests in calendar view (grayed out)
  - Warn if assigning to shift on pending vacation request
- **Certification Integration:**
  - Check certifications before allowing assignment
  - Show certification status in staff selector
  - Dashboard shows staff with expiring certs who are scheduled
- **Employee Status:**
  - Cannot assign terminated employees
  - Cannot assign employees on leave
  - Respect employment status

**Acceptance Criteria:**
- ✅ All features work together seamlessly
- ✅ No data inconsistencies
- ✅ Constraints enforced

---

### Task 18: Testing and Quality Assurance
**Priority:** P0
**Estimated Time:** 60 minutes

**Requirements:**

Comprehensive testing:
- Test shift creation and editing
- Test bulk assignment operations
- Test conflict detection (try to violate each rule)
- Test permissions (employee can't edit shifts, manager can)
- Test calendar views (weekly, monthly)
- Test filtering and search
- Test notifications send correctly
- Test edge cases:
  - Midnight-crossing shifts (19:00-07:00)
  - Daylight saving time changes
  - Assigning to past dates (should block)
  - Deleting shift with assignments
  - Publishing with validation errors
- Test mobile responsiveness (employees use mobile primarily)
- Test performance with 500+ shifts

**Acceptance Criteria:**
- ✅ All features work correctly
- ✅ No console errors
- ✅ Build succeeds
- ✅ Mobile experience is excellent
- ✅ Performance is good

---

### Task 19: Documentation and Migration Guide
**Files:** `README.md`, migration notes
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**

Update documentation:
- Add shift scheduling to feature list
- Document manager workflow (create shifts, assign staff, publish)
- Document employee workflow (view schedule, get notifications)
- Add API documentation for shift endpoints
- Create migration notes for existing installations
- Add screenshots of key features
- Document configuration options (shift types, rules, etc.)

**Acceptance Criteria:**
- ✅ Clear, complete documentation
- ✅ Examples provided
- ✅ Migration path documented

---

## TOTAL ESTIMATED TIME: 13-15 hours

---

## Phase 2 Success Criteria

**Functional:**
- ✅ Managers can create and publish shifts
- ✅ Managers can assign staff to shifts
- ✅ System prevents invalid assignments (no rest, expired certs, etc.)
- ✅ Employees can view their schedule
- ✅ Calendar shows coverage levels at a glance
- ✅ Understaffed shifts are flagged
- ✅ Notifications work for shift changes

**Technical:**
- ✅ No errors in console or backend logs
- ✅ Database queries optimized
- ✅ Build succeeds
- ✅ Mobile experience is excellent
- ✅ All TypeScript types correct

**Business Value:**
- ✅ Managers save hours per week on scheduling
- ✅ Compliance with staffing ratios tracked automatically
- ✅ Staff know their schedules well in advance
- ✅ Reduces scheduling conflicts
- ✅ Foundation for advanced scheduling features

---

## Dependencies
- Phase 1 (Certifications) must be complete ✅
- Existing employee and location systems must work
- Notification system exists (from vacation module)

---

## Next Phase Preview

**Phase 3** will add:
- Shift swap workflow
- Advanced scheduling templates
- Fair distribution analytics
- Skills-based assignment recommendations
- Overtime tracking and warnings
- Historical scheduling data and trends
