# CarePlan Development TODO List - PHASE 3
## Advanced Scheduling & Skills-Based Matching

**Created:** January 2025
**Based on:** ICU_MANAGER_REQUIREMENTS.md (TIER 2 Requirements)
**Previous Phases:** Phase 1 ✅ | Phase 2 ✅
**Approach:** Build advanced scheduling features on solid foundation
**Focus:** Skills matching, fair distribution, shift swaps, analytics

---

## Phase 3 Overview

**Priority:** TIER 2 - HIGH IMPACT
**Est. Time:** 8-10 hours with quality focus
**Business Value:** Significant operational improvements and staff satisfaction

### Why These Features Now:
1. **Staff Satisfaction:** Shift swaps and fair distribution improve morale
2. **Optimal Patient Care:** Skills matching ensures right nurse for right patient
3. **Operational Efficiency:** Analytics identify issues before they become problems
4. **Retention:** Fair scheduling reduces burnout and turnover
5. **Builds on Phase 2:** Requires robust shift scheduling foundation

---

## DEVELOPER TODO LIST - PHASE 3

### Task 1: Shift Swap Request System
**Files:** `apps/shifts/models.py`, `apps/api/views/shifts.py`
**Priority:** P0
**Estimated Time:** 60 minutes

**Requirements:**

Create `ShiftSwapRequest` model:
- `requester` (ForeignKey to User - who wants to swap)
- `requester_shift` (ForeignKey to Shift - shift they want to give away)
- `target_employee` (ForeignKey to User, nullable - specific person or open)
- `target_shift` (ForeignKey to Shift, nullable - swap for specific shift or any)
- `reason` (TextField - why they need swap)
- `status` (CharField - PENDING, APPROVED, DENIED, CANCELLED)
- `approved_by` (ForeignKey to User, nullable - manager approval)
- `approved_at` (DateTimeField)
- `denial_reason` (TextField)
- `created_at`, `updated_at`

Add methods:
- `get_qualified_candidates()` - find staff who could take the shift
- `validate_swap()` - ensure swap meets all rules
- `execute_swap()` - perform the actual swap
- `notify_participants()` - send notifications

Workflow:
1. Employee requests to swap shift (can specify target employee or leave open)
2. System shows eligible candidates (have certs, no conflicts)
3. Target employee accepts or manager assigns
4. Manager approves swap
5. Assignments updated automatically

API endpoints:
- `POST /api/shifts/swap-requests/` - create swap request
- `GET /api/shifts/swap-requests/` - list swap requests (filtered by status, employee)
- `PATCH /api/shifts/swap-requests/{id}/accept/` - target accepts swap
- `PATCH /api/shifts/swap-requests/{id}/approve/` - manager approves
- `PATCH /api/shifts/swap-requests/{id}/deny/` - manager denies
- `DELETE /api/shifts/swap-requests/{id}/` - cancel request

**Acceptance Criteria:**
- ✅ Swaps validate all rules (rest periods, certs, etc.)
- ✅ Notifications send to all parties
- ✅ Audit trail maintained
- ✅ Cannot swap published shifts without manager approval

---

### Task 2: Skills-Based Assignment Recommendations
**Files:** `apps/shifts/matching.py` (new), `apps/api/views/shifts.py`
**Priority:** P1
**Estimated Time:** 75 minutes

**Requirements:**

Create skill matching algorithm:
- Analyze shift requirements (if specific skills needed)
- Score employees based on:
  - Has required certifications ✅ (blocking)
  - Has relevant skills (equipment, procedures)
  - Experience level matches shift complexity
  - Recently worked similar shifts (continuity)
  - Availability (not on vacation, no conflicts)
  - Workload balance (hours worked recently)
  - Preference (if employee indicated preference for shift type)

Create `ShiftRequirement` model (optional, for complex cases):
- `shift` (ForeignKey)
- `required_skill` (ForeignKey to Skill)
- `minimum_proficiency` (CharField - BASIC, INTERMEDIATE, ADVANCED, EXPERT)
- `required_count` (IntegerField - how many staff need this skill)

Recommendation engine endpoint:
- `GET /api/shifts/{id}/recommended-staff/` - get ranked list of candidates

Response includes:
- Employee details
- Match score (0-100)
- Breakdown (why recommended):
  - ✅ Has required certs
  - ✅ Has required skills
  - ⚠️ Warning factors (worked many nights recently)
  - ❌ Blocking factors (on vacation, already assigned)
- Quick assign button

**Acceptance Criteria:**
- ✅ Recommendations are sensible
- ✅ Algorithm considers multiple factors
- ✅ Fast (< 1 second for 200 employees)
- ✅ Transparent (shows why recommended)

---

### Task 3: Fair Distribution Analytics
**Files:** `apps/shifts/analytics.py` (new), frontend dashboard
**Priority:** P1
**Estimated Time:** 60 minutes

**Requirements:**

Analytics for fair shift distribution:

Calculate metrics per employee (for time period):
- Total shifts worked
- Total hours worked
- Night shifts worked (%)
- Weekend shifts worked (%)
- Holiday shifts worked
- Consecutive days worked (max)
- Days off in a row (average)
- Shift type distribution (day/night/on-call %)
- Overtime hours
- Compare to team average (above/below average)

API endpoint:
- `GET /api/shifts/analytics/fair-distribution/`
  - Params: location_id, start_date, end_date
  - Returns: list of employees with metrics
  - Highlights outliers (worked significantly more/less than average)

Visual dashboard:
- Table showing all employees with metrics
- Color coding:
  - Green: within 10% of average
  - Yellow: 10-25% above/below average
  - Red: >25% deviation from average
- Sort by any column
- Filter by outliers only
- Chart showing distribution curves
- Export to CSV for deeper analysis

Use cases:
- Identify who's worked too many nights
- Ensure weekend coverage is distributed fairly
- Identify burnout risk (too many consecutive shifts)
- Justify scheduling decisions with data

**Acceptance Criteria:**
- ✅ Calculations are accurate
- ✅ Visual dashboard is clear
- ✅ Helps managers make fair decisions
- ✅ Export functionality works

---

### Task 4: Advanced Shift Templates & Patterns
**Files:** `apps/shifts/models.py`, template builder UI
**Priority:** P2
**Estimated Time:** 75 minutes

**Requirements:**

Enhance shift template system:

Create `ShiftPattern` model:
- `name` (CharField - e.g., "4-Week Rotation A")
- `location` (ForeignKey)
- `is_active` (BooleanField)
- `pattern_config` (JSONField - stores complex pattern)

Pattern config structure:
```json
{
  "cycle_length_weeks": 4,
  "shifts": [
    {
      "week": 1,
      "day_of_week": 1,
      "shift_type": "DAY",
      "start_time": "07:00",
      "end_time": "19:00",
      "required_staff": 8,
      "required_rn": 5
    },
    // ... more shifts
  ],
  "staff_rotation": {
    "rotation_type": "FIXED" | "ROTATING",
    "employees": [/* list of employee IDs */],
    "rotation_rules": {/* custom rules */}
  }
}
```

Template builder UI:
- Visual week grid
- Click to add shift
- Drag to copy shift pattern
- Assign employees to rotation
- Preview 4-8 weeks
- Save as template
- Apply template to date range

Smart features:
- Auto-distribute staff evenly
- Ensure fair night/weekend distribution
- Respect employee preferences (if tracked)
- Validate before applying

**Acceptance Criteria:**
- ✅ Can create complex 4-week patterns easily
- ✅ Preview shows exactly what will be created
- ✅ Applying template creates all shifts correctly
- ✅ Staff assignments respect all rules

---

### Task 5: Overtime Tracking and Warnings
**Files:** `apps/shifts/overtime.py`, dashboard widgets
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**

Overtime tracking system:

Calculate for each employee:
- Regular hours (up to 40/week or 160/month)
- Overtime hours (beyond regular, up to weekly max)
- Excessive overtime (beyond safe limits)
- Projected hours (based on scheduled shifts)
- Compliance with max 48 hours/week rule (EU directive)

Overtime rules (configurable):
- Standard work week: 40 hours
- Maximum work week: 48 hours (averaged over 17 weeks)
- Overtime trigger: > 40 hours/week
- Warning levels:
  - Yellow: Approaching 40 hours
  - Orange: 40-48 hours (overtime but legal)
  - Red: > 48 hours (violation)

API endpoints:
- `GET /api/shifts/overtime/summary/` - overtime summary for all staff
- `GET /api/shifts/overtime/{employee_id}/` - detailed overtime for employee
- `GET /api/shifts/overtime/violations/` - list of current violations

Warnings:
- When assigning shift that would cause overtime
- Dashboard widget showing staff in overtime
- Weekly report to managers (automated)
- Alert if violating EU directive

**Acceptance Criteria:**
- ✅ Calculations match labor laws
- ✅ Warnings appear before violations occur
- ✅ Easy to see who's in overtime
- ✅ Historical tracking for audits

---

### Task 6: Shift History and Audit Trail
**Files:** `apps/shifts/models.py`, audit log viewer
**Priority:** P2
**Estimated Time:** 45 minutes

**Requirements:**

Create `ShiftHistory` model for audit trail:
- `shift` (ForeignKey)
- `action` (CharField - CREATED, MODIFIED, PUBLISHED, CANCELLED, ASSIGNED, UNASSIGNED)
- `changed_by` (ForeignKey to User)
- `changed_at` (DateTimeField)
- `old_value` (JSONField - before change)
- `new_value` (JSONField - after change)
- `reason` (TextField, optional)

Automatically log:
- Shift creation and deletion
- Assignment changes
- Publication events
- Template application
- Swap approvals

Audit log viewer (for managers/admins):
- Filter by date range, shift, employee, action type
- Show timeline of changes
- Export to CSV
- Link to relevant entities

Use cases:
- Dispute resolution ("Who removed me from that shift?")
- Compliance audits
- Understanding scheduling patterns
- Troubleshooting issues

**Acceptance Criteria:**
- ✅ All important changes are logged
- ✅ Logs are immutable (append-only)
- ✅ Easy to search and filter
- ✅ Performance is good even with thousands of log entries

---

### Task 7: Employee Schedule Preferences
**Files:** `apps/employees/models.py`, preference management UI
**Priority:** P2
**Estimated Time:** 45 minutes

**Requirements:**

Create `SchedulePreference` model:
- `employee` (ForeignKey)
- `preference_type` (CharField - PREFERRED_SHIFT_TYPE, PREFERRED_DAYS, UNAVAILABLE_DATES, MAX_CONSECUTIVE_NIGHTS, etc.)
- `preference_value` (JSONField - flexible structure)
- `priority` (CharField - MUST_HAVE, PREFERRED, NICE_TO_HAVE)
- `notes` (TextField)
- `is_active` (BooleanField)

Preference types:
- Preferred shift type (Day, Night, mix)
- Preferred days off (e.g., Mondays)
- Unavailable dates (hard constraints)
- Max consecutive nights
- Minimum days off per week
- Preferred work hours per week
- Cannot work with specific employees (rare, conflict resolution)

Preference management page:
- Employees can set preferences
- Manager can view and override
- System considers preferences when showing recommendations
- Preferences don't override requirements (nice-to-have, not mandatory)

Integration with scheduling:
- Recommendation engine factors in preferences
- Dashboard shows "preference satisfaction score"
- Alerts if consistently ignoring preferences (morale risk)

**Acceptance Criteria:**
- ✅ Easy for employees to set preferences
- ✅ System respects preferences when possible
- ✅ Managers can see and override
- ✅ Balance fairness with preferences

---

### Task 8: Shift Coverage Heat Map
**Files:** `frontend/src/components/shifts/CoverageHeatMap.tsx`
**Priority:** P1
**Estimated Time:** 60 minutes

**Requirements:**

Visual heat map showing coverage levels:
- Grid showing days and shifts
- Color intensity based on coverage:
  - Deep red: < 50% staffed (critical)
  - Orange: 50-79% staffed (warning)
  - Yellow: 80-99% staffed (almost there)
  - Green: 100%+ staffed (good)
  - Dark green: > 120% staffed (overstaffed)
- Hover to see exact numbers
- Click to see shift details
- Filter by location, date range
- Toggle between:
  - Overall coverage
  - RN coverage specifically
  - Charge nurse coverage

Predictive mode:
- Show projected coverage for future weeks
- Highlight potential gaps
- Consider vacation requests
- Consider certification expirations

**Acceptance Criteria:**
- ✅ Visual and intuitive
- ✅ Instantly shows problem areas
- ✅ Helps with proactive planning
- ✅ Responsive design

---

### Task 9: Shift Swap Marketplace (UI)
**Files:** `frontend/src/pages/shifts/ShiftSwapPage.tsx`
**Priority:** P1
**Estimated Time:** 60 minutes

**Requirements:**

Shift swap marketplace page:

**Employee View:**
- "My Shifts" section - shifts they're assigned to
- "Request Swap" button on each shift
- Swap request form:
  - Reason for swap
  - Prefer specific person (optional)
  - Or open to anyone qualified
- "Available Swaps" section:
  - Other employees' swap requests
  - Filter by date, shift type
  - "I'll take it" button if qualified
  - Shows if swap conflicts with your schedule
- "My Swap Requests" section:
  - Active requests
  - Status (pending, awaiting manager, approved, denied)
  - Cancel button

**Manager View:**
- "Pending Swaps" requiring approval
- See both shifts involved
- Validate swap meets all rules
- Approve/deny with reason
- See swap history

Notifications:
- When someone accepts your swap request
- When swap is approved/denied
- When new swap available that matches your criteria

**Acceptance Criteria:**
- ✅ Intuitive for employees to use
- ✅ Quick for managers to approve
- ✅ All validation rules enforced
- ✅ Mobile-friendly (primary use case)

---

### Task 10: Advanced Scheduling Dashboard
**Files:** `frontend/src/pages/shifts/AdvancedSchedulingDashboard.tsx`
**Priority:** P1
**Estimated Time:** 75 minutes

**Requirements:**

Comprehensive scheduling dashboard for managers:

**Overview Section:**
- Coverage summary (next 7 days, next 30 days)
- Understaffed shifts count
- Pending swap requests
- Overtime alerts
- Certification expiry alerts

**Fair Distribution Panel:**
- Quick view of distribution metrics
- Highlight outliers
- Link to full analytics

**Overtime Panel:**
- Employees currently in overtime
- Projected overtime for next week
- Violations (if any)

**Skills Matching Panel:**
- Shifts requiring specific skills
- Skills gap warnings
- Training needs identified

**Alerts & Warnings:**
- Rule violations
- Scheduling conflicts
- Cert expirations affecting scheduled shifts
- Understaffed critical shifts
- Employees approaching burnout thresholds

**Quick Actions:**
- Create shift
- Approve pending swaps
- Generate schedule from template
- Send notifications
- Export reports

**Filters:**
- Location
- Date range
- Alert severity

**Acceptance Criteria:**
- ✅ Manager can see all critical info at a glance
- ✅ Actionable (can resolve issues from dashboard)
- ✅ Real-time updates
- ✅ Performance is excellent

---

### Task 11: Employee Workload Balance Indicator
**Files:** `frontend/src/components/shifts/WorkloadIndicator.tsx`
**Priority:** P2
**Estimated Time:** 30 minutes

**Requirements:**

Visual indicator of employee workload:
- Show on employee cards in staff selector
- Show on employee profile
- Metrics:
  - Hours worked last 7 days
  - Hours worked last 30 days
  - Consecutive shifts worked
  - Time since last day off
- Color coding:
  - Green: Well-rested (< 40 hrs/week, adequate rest)
  - Yellow: Moderate load (40-48 hrs/week)
  - Orange: High load (> 48 hrs/week or many consecutive shifts)
  - Red: Burnout risk (excessive hours, no days off)
- Tooltip shows detailed breakdown
- Warning icons if concerning patterns

Integration:
- Staff selector shows workload when assigning
- Recommendation engine penalizes overworked staff
- Dashboard shows burnout risk employees

**Acceptance Criteria:**
- ✅ Accurate calculation
- ✅ Clear visual design
- ✅ Helps prevent burnout
- ✅ Promotes fair distribution

---

### Task 12: Shift Reporting Suite
**Files:** `frontend/src/pages/shifts/ReportsPage.tsx`, backend report generators
**Priority:** P2
**Estimated Time:** 60 minutes

**Requirements:**

Comprehensive reporting system:

**Reports Available:**

1. **Staffing Compliance Report:**
   - Date range
   - All shifts with staffing levels
   - Violations highlighted
   - Export to PDF/CSV
   - Suitable for regulatory inspections

2. **Overtime Report:**
   - Employee overtime hours
   - Cost calculation
   - Trends over time
   - Comparison to budget

3. **Fair Distribution Report:**
   - All distribution metrics
   - Statistical analysis
   - Outlier identification
   - Recommendations for rebalancing

4. **Coverage Analysis:**
   - Coverage trends
   - Chronic understaffing patterns
   - Peak demand times
   - Staffing gaps

5. **Shift Pattern Report:**
   - Most common patterns
   - Template effectiveness
   - Schedule stability metrics

6. **Swap Request Report:**
   - Swap frequency
   - Approval rates
   - Common swap reasons
   - Identify systemic issues

Report builder:
- Select report type
- Choose date range
- Filter by location, department, employee
- Preview report
- Export (PDF, CSV, Excel)
- Schedule recurring reports (email weekly)

**Acceptance Criteria:**
- ✅ Reports are accurate and comprehensive
- ✅ Professional formatting
- ✅ Fast generation (< 10 seconds)
- ✅ Export formats work correctly

---

### Task 13: Mobile Optimization for Shift Management
**Files:** Mobile-specific components and views
**Priority:** P1
**Estimated Time:** 60 minutes

**Requirements:**

Optimize shift features for mobile:
- Responsive calendar view (swipe between weeks)
- Touch-friendly shift cards
- Quick swap request (3 taps maximum)
- Push notifications for shift changes
- Offline mode:
  - Cache employee's schedule
  - Show cached data when offline
  - Sync when back online
- Quick actions:
  - Accept swap
  - View shift details
  - Request time off
- Home screen widget (if PWA):
  - Next shift countdown
  - Quick view of week schedule

**Acceptance Criteria:**
- ✅ Excellent mobile UX
- ✅ Fast on mobile networks
- ✅ Offline capability works
- ✅ Push notifications reliable

---

### Task 14: Skills-Based Shift Planning
**Files:** `frontend/src/components/shifts/SkillsBasedPlanner.tsx`
**Priority:** P2
**Estimated Time:** 45 minutes

**Requirements:**

Advanced planning tool for complex shifts:
- Define shift requirements:
  - How many staff total
  - How many must have skill X
  - How many must have proficiency level Y
- System recommends optimal team composition
- Drag-and-drop to adjust
- Validation shows if requirements met
- Save as template for similar shifts

Example: ECMO patient shift
- Need 3 nurses
- At least 1 with ECMO certification (ADVANCED)
- At least 2 with ventilator management (INTERMEDIATE)
- At least 1 charge nurse

System suggests teams that meet criteria
Manager fine-tunes and approves

**Acceptance Criteria:**
- ✅ Handles complex requirements
- ✅ Suggestions are optimal
- ✅ Easy to use
- ✅ Prevents invalid assignments

---

### Task 15: Integration Testing and Refinement
**Priority:** P0
**Estimated Time:** 90 minutes

**Requirements:**

Comprehensive testing of all Phase 3 features:

**Functional Tests:**
- Shift swap workflow (create, accept, approve, execute)
- Skills-based recommendations (verify scoring)
- Fair distribution analytics (verify calculations)
- Overtime tracking (verify labor law compliance)
- Advanced templates (create complex patterns)
- Workload indicators (verify accuracy)
- Reports (verify all reports generate correctly)

**Integration Tests:**
- Swaps integrate with notifications
- Overtime integrates with scheduling rules
- Skills matching uses certification data
- Preferences respected in recommendations
- Mobile app syncs correctly

**Performance Tests:**
- Analytics with 500+ employees
- Heat map with 1000+ shifts
- Report generation speed
- Mobile app responsiveness

**Edge Cases:**
- Swap requests for past shifts (should block)
- Circular swap requests (A→B, B→C, C→A)
- Overtime during DST change
- Skills matching with incomplete data
- Template application across month boundaries

**Acceptance Criteria:**
- ✅ All features work correctly
- ✅ No regressions in Phase 1 or 2 features
- ✅ Performance is excellent
- ✅ Mobile experience is polished

---

### Task 16: Documentation and Training Materials
**Files:** `README.md`, user guides
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**

Create documentation:
- Update README with Phase 3 features
- Manager guide:
  - How to use fair distribution analytics
  - How to approve swap requests
  - How to use skills-based planning
  - How to interpret reports
- Employee guide:
  - How to request shift swap
  - How to set schedule preferences
  - How to view overtime status
- API documentation updates
- Configuration guide (overtime rules, distribution settings, etc.)
- Screenshots of key features
- Video walkthrough (optional)

**Acceptance Criteria:**
- ✅ Clear, comprehensive documentation
- ✅ Covers all major features
- ✅ Examples provided
- ✅ Professional presentation

---

## TOTAL ESTIMATED TIME: 14-16 hours

---

## Phase 3 Success Criteria

**Functional:**
- ✅ Employees can request and swap shifts easily
- ✅ System recommends optimal staff assignments based on skills
- ✅ Fair distribution analytics show balanced workload
- ✅ Overtime is tracked and warnings prevent violations
- ✅ Advanced templates enable complex scheduling patterns
- ✅ Reports provide actionable insights
- ✅ Mobile experience is excellent

**Technical:**
- ✅ No console errors or backend errors
- ✅ Performance is excellent even with large datasets
- ✅ Build succeeds
- ✅ Mobile app works offline
- ✅ All calculations are accurate

**Business Value:**
- ✅ Staff satisfaction improves (fair scheduling)
- ✅ Patient care improves (skills matching)
- ✅ Reduces manager workload (automation)
- ✅ Compliance is easier (automated tracking)
- ✅ Reduces burnout (workload balancing)
- ✅ Data-driven decision making (analytics)

---

## Dependencies
- Phase 1 (Certifications) ✅
- Phase 2 (Basic Scheduling) ✅
- Skills module from Phase 1 (Tasks 14-16)

---

## Next Phases Preview

**Phase 4:** Patient Acuity Matching & Predictive Analytics
- Patient acuity scoring
- Predictive staffing models
- AI-powered schedule optimization
- Demand forecasting

**Phase 5:** Mobile Native App & Notifications
- Native iOS/Android apps
- Real-time push notifications
- Offline-first architecture
- Location-based features (clock in/out)

**Phase 6:** Integration & Automation
- Payroll system integration
- HR system integration
- Automated schedule generation
- Self-healing schedules (auto-fill call-outs)
