# CarePlan Development TODO List
## Project Manager's Implementation Plan

**Created:** January 2025
**Based on:** ICU_MANAGER_REQUIREMENTS.md
**Approach:** Phased implementation, quality over speed
**Focus:** High-impact features that build on existing infrastructure

---

## Analysis Summary

After reviewing the ICU Manager requirements, I've identified **43 distinct feature requests** spanning certification tracking, shift scheduling, skills management, compliance, and analytics.

**Key Insights:**
- The manager ranked features in 4 tiers based on criticality
- TIER 1 (Critical) features directly impact patient safety and regulatory compliance
- Many features have dependencies on infrastructure not yet built
- Quality and precision are non-negotiable in healthcare software

**Strategic Approach:**
We'll implement features in phases, ensuring each phase is production-ready before moving forward. This session will focus on **Phase 1: Certification & Skills Foundation**.

---

## Phase 1: Certification & Skills Foundation (THIS SESSION)
**Priority:** TIER 1 - CRITICAL
**Est. Time:** 4-6 hours with quality focus
**Business Value:** Solves immediate compliance and safety needs

### Why These Features First:
1. **Highest ROI:** Prevents regulatory fines and scheduling non-compliant staff
2. **Foundation for future:** Shift scheduling depends on certification data
3. **Immediate usability:** Managers can start tracking certifications today
4. **Low dependency:** Builds on existing employee system
5. **Clear success criteria:** Either certified or not - binary and testable

---

## DEVELOPER TODO LIST - PHASE 1

### Task 1: Extend Data Models for Certifications
**File:** `apps/employees/models.py`
**Priority:** P0 (Blocking all other work)
**Estimated Time:** 45 minutes

**Requirements:**
- Update `Qualification` model to include:
  - `expiry_date` (DateField, nullable for non-expiring)
  - `renewal_period_months` (IntegerField, e.g., 24 for BLS)
  - `is_required` (BooleanField - cannot work without)
  - `category` (CharField - choices: MUST_HAVE, SPECIALIZED, OPTIONAL)
  - `issuing_organization` (CharField)

- Create new `EmployeeQualification` junction model:
  - `employee` (ForeignKey to User)
  - `qualification` (ForeignKey to Qualification)
  - `issue_date` (DateField)
  - `expiry_date` (DateField, nullable)
  - `document` (FileField for uploaded certificate)
  - `verified_by` (ForeignKey to User, nullable - who verified)
  - `verified_at` (DateTimeField, nullable)
  - `status` (CharField - choices: ACTIVE, EXPIRED, EXPIRING_SOON, PENDING_VERIFICATION)
  - `notes` (TextField, optional)

- Add helper methods:
  - `is_expired()` - check if past expiry date
  - `is_expiring_soon(days=30)` - check if expiring within X days
  - `days_until_expiry()` - calculate remaining days

**Acceptance Criteria:**
- ✅ Models pass Django migrations
- ✅ All fields have appropriate help_text
- ✅ Proper indexes on date fields
- ✅ Clean code with docstrings

---

### Task 2: Create Certification Management API
**File:** `apps/employees/views.py`, `apps/employees/serializers.py`
**Priority:** P0
**Estimated Time:** 60 minutes

**Requirements:**
- Create `EmployeeQualificationSerializer`:
  - Include all fields
  - Nested employee and qualification data
  - Read-only computed fields (is_expired, days_until_expiry)

- Create API endpoints:
  - `GET /api/employees/{id}/certifications/` - List employee's certifications
  - `POST /api/employees/{id}/certifications/` - Add certification
  - `PATCH /api/employees/{id}/certifications/{cert_id}/` - Update certification
  - `DELETE /api/employees/{id}/certifications/{cert_id}/` - Remove certification
  - `GET /api/certifications/expiring/` - Get all expiring certifications (filtered by days)
  - `GET /api/certifications/expired/` - Get all expired certifications

- Filters and search:
  - Filter by status (active, expired, expiring)
  - Filter by qualification type
  - Filter by employee
  - Search by employee name or qualification name

**Acceptance Criteria:**
- ✅ RESTful API design
- ✅ Proper permissions (staff can view own, managers can view team, admin can view all)
- ✅ Pagination for list endpoints
- ✅ Input validation
- ✅ Comprehensive error handling

---

### Task 3: Frontend Types and Configuration
**File:** `frontend/src/types/certification.ts`, `frontend/src/config/certification.config.ts`
**Priority:** P0
**Estimated Time:** 30 minutes

**Requirements:**
- Create TypeScript interfaces:
  ```typescript
  interface Certification {
    id: number
    employee: EmployeeSummary
    qualification: Qualification
    issue_date: string
    expiry_date: string | null
    document_url: string | null
    verified_by: EmployeeSummary | null
    verified_at: string | null
    status: CertificationStatus
    notes: string
    is_expired: boolean
    is_expiring_soon: boolean
    days_until_expiry: number | null
  }

  type CertificationStatus = 'ACTIVE' | 'EXPIRED' | 'EXPIRING_SOON' | 'PENDING_VERIFICATION'

  interface QualificationExtended extends Qualification {
    expiry_date: string | null
    renewal_period_months: number | null
    is_required: boolean
    category: 'MUST_HAVE' | 'SPECIALIZED' | 'OPTIONAL'
    issuing_organization: string
  }
  ```

- Create configuration:
  ```typescript
  CERTIFICATION_CONFIG = {
    EXPIRY_WARNING_DAYS: [90, 60, 30, 14, 7],
    CRITICAL_WARNING_DAYS: 30,
    STATUS_COLORS: {...},
    CATEGORY_LABELS: {...}
  }
  ```

**Acceptance Criteria:**
- ✅ All types match backend models
- ✅ Exported from types/index.ts
- ✅ Configuration is centralized

---

### Task 4: Certification Service Layer
**File:** `frontend/src/services/certification.service.ts`
**Priority:** P0
**Estimated Time:** 30 minutes

**Requirements:**
- Create service with methods:
  - `getCertifications(employeeId?, filters?)` - Get certifications
  - `getEmployeeCertifications(employeeId)` - Get specific employee's certs
  - `addCertification(data)` - Add new certification
  - `updateCertification(id, data)` - Update certification
  - `deleteCertification(id)` - Remove certification
  - `getExpiringCertifications(days=30)` - Get expiring soon
  - `getExpiredCertifications()` - Get all expired
  - `uploadCertificateDocument(certId, file)` - Upload document

**Acceptance Criteria:**
- ✅ Uses axios with proper error handling
- ✅ Returns typed data
- ✅ Handles file uploads for documents

---

### Task 5: React Query Hooks for Certifications
**File:** `frontend/src/hooks/useCertifications.ts`
**Priority:** P0
**Estimated Time:** 30 minutes

**Requirements:**
- Create hooks:
  - `useCertifications(employeeId?, filters?)` - Query hook with caching
  - `useEmployeeCertifications(employeeId)` - Get employee's certifications
  - `useExpiringCertifications(days)` - Get expiring certifications
  - `useExpiredCertifications()` - Get expired certifications
  - `useAddCertification()` - Mutation hook
  - `useUpdateCertification()` - Mutation hook
  - `useDeleteCertification()` - Mutation hook

- Cache invalidation strategy
- Optimistic updates for mutations
- Loading and error states

**Acceptance Criteria:**
- ✅ Proper React Query configuration
- ✅ Cache invalidation works correctly
- ✅ TypeScript types are correct

---

### Task 6: Certification Status Badge Component
**File:** `frontend/src/components/certifications/CertificationStatusBadge.tsx`
**Priority:** P1
**Estimated Time:** 20 minutes

**Requirements:**
- Display certification status with appropriate colors:
  - ACTIVE: Green
  - EXPIRING_SOON: Yellow/Orange
  - EXPIRED: Red
  - PENDING_VERIFICATION: Gray
- Show days until expiry for expiring certifications
- Tooltip with full status information
- Accessibility (ARIA labels)

**Acceptance Criteria:**
- ✅ Visual hierarchy clear
- ✅ Color-blind friendly
- ✅ Responsive design

---

### Task 7: Certification Card Component
**File:** `frontend/src/components/certifications/CertificationCard.tsx`
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**
- Display single certification with:
  - Qualification name and code
  - Issue date and expiry date
  - Status badge
  - Days until expiry (if applicable)
  - Issuing organization
  - Document download link (if uploaded)
  - Verified status (if verified)
  - Actions (edit, delete, upload document)

- Visual warnings for expiring/expired
- Icons for different certification types

**Acceptance Criteria:**
- ✅ Clear visual design
- ✅ Action buttons work correctly
- ✅ Loading states for actions

---

### Task 8: Certification List Component
**File:** `frontend/src/components/certifications/CertificationList.tsx`
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**
- Display list of certifications
- Group by status (expired, expiring, active)
- Filters:
  - By status
  - By category (must-have, specialized, optional)
  - By qualification type
- Search by qualification name
- Sort by expiry date
- Empty states for no certifications

**Acceptance Criteria:**
- ✅ Performant with many certifications
- ✅ Filters work correctly
- ✅ Clear visual grouping

---

### Task 9: Enhanced Profile Page with Certifications
**File:** `frontend/src/pages/ProfilePage.tsx`
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**
- Replace "Qualifications" placeholder section with real data
- Display employee's certifications using CertificationList
- Show summary statistics:
  - Total active certifications
  - Expiring soon count
  - Expired count
- Quick actions:
  - Add new certification (if has permission)
  - View all certifications link

**Acceptance Criteria:**
- ✅ Integrates seamlessly with existing profile
- ✅ Loading and error states
- ✅ Responsive design

---

### Task 10: Certification Dashboard for Managers
**File:** `frontend/src/pages/certifications/CertificationDashboardPage.tsx`
**Priority:** P1
**Estimated Time:** 45 minutes

**Requirements:**
- Overview dashboard showing:
  - **Critical Alerts:** Expired certifications (red alert)
  - **Warnings:** Expiring within 30 days (orange warning)
  - **Statistics:**
    - Total employees
    - Employees with all required certifications
    - Compliance percentage
  - **Lists:**
    - Expiring certifications (grouped by urgency)
    - Expired certifications
    - Recently added certifications

- Filters:
  - By location
  - By department
  - By qualification type
  - By time range

- Actions:
  - Click to view employee profile
  - Download compliance report
  - Send renewal reminders

**Acceptance Criteria:**
- ✅ Real-time data
- ✅ Clear visual alerts
- ✅ Manager can take action immediately
- ✅ Accessible to managers and admins only

---

### Task 11: Add Certification Management to Employee Detail Page
**File:** `frontend/src/pages/employees/EmployeeDetailPage.tsx`
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**
- Add "Certifications" tab/section to employee detail
- Display employee's certifications
- Allow managers/admins to:
  - Add new certification
  - Edit existing certification
  - Upload certificate document
  - Verify certification
  - Mark as expired

**Acceptance Criteria:**
- ✅ Proper permissions (managers can manage their team)
- ✅ Form validation
- ✅ Success/error messages

---

### Task 12: Certification Upload and Document Management
**File:** `frontend/src/components/certifications/CertificationUploadModal.tsx`
**Priority:** P1
**Estimated Time:** 30 minutes

**Requirements:**
- Modal/form for uploading certificate documents
- File upload (PDF, images)
- Preview uploaded documents
- Validation:
  - File size limits (max 5MB)
  - File type restrictions
  - Required fields (issue date, expiry date)

- Auto-calculate status based on dates
- Link document to certification

**Acceptance Criteria:**
- ✅ Drag-and-drop upload
- ✅ Progress indication
- ✅ Error handling for upload failures
- ✅ File preview

---

### Task 13: Update Dashboard with Certification Alerts
**File:** `frontend/src/pages/DashboardPage.tsx`
**Priority:** P2
**Estimated Time:** 20 minutes

**Requirements:**
- Add certification alerts widget for managers/admins:
  - Show count of expired certifications
  - Show count of expiring soon
  - Click to view certification dashboard

- Add certification status to personal dashboard:
  - Show own expiring certifications
  - Quick link to renew

**Acceptance Criteria:**
- ✅ Role-based visibility
- ✅ Click-through to details works
- ✅ Updates in real-time

---

### Task 14: Skills and Competencies Foundation
**File:** `apps/employees/models.py`
**Priority:** P2
**Estimated Time:** 30 minutes

**Requirements:**
- Create `Skill` model:
  - `name` (e.g., "Ventilator Management")
  - `category` (EQUIPMENT, PATIENT_CARE, PROCEDURE)
  - `description`
  - `is_active`

- Create `EmployeeSkill` junction model:
  - `employee` (ForeignKey)
  - `skill` (ForeignKey)
  - `proficiency_level` (BASIC, INTERMEDIATE, ADVANCED, EXPERT)
  - `verified_by` (ForeignKey to User)
  - `verified_date`
  - `last_used_date`
  - `notes`

- Add methods:
  - `get_skill_level_display()`
  - `is_verified()`

**Acceptance Criteria:**
- ✅ Models migrate successfully
- ✅ Proper relationships
- ✅ Admin interface works

---

### Task 15: Skills API and Frontend (Basic)
**File:** `apps/employees/views.py`, `frontend/src/types/skill.ts`, `frontend/src/services/skill.service.ts`
**Priority:** P2
**Estimated Time:** 45 minutes

**Requirements:**
- Create Skills API endpoints:
  - `GET /api/employees/{id}/skills/` - Get employee skills
  - `POST /api/employees/{id}/skills/` - Add skill
  - `PATCH /api/employees/{id}/skills/{skill_id}/` - Update skill
  - `DELETE /api/employees/{id}/skills/{skill_id}/` - Remove skill
  - `GET /api/skills/` - List all available skills

- Frontend types and service
- Basic hooks (useSkills, useEmployeeSkills)

**Acceptance Criteria:**
- ✅ CRUD operations work
- ✅ Proper validation
- ✅ TypeScript types match

---

### Task 16: Display Skills on Profile and Employee Detail
**File:** `frontend/src/pages/ProfilePage.tsx`, `frontend/src/pages/employees/EmployeeDetailPage.tsx`
**Priority:** P2
**Estimated Time:** 30 minutes

**Requirements:**
- Replace skills placeholder with real data
- Show skills grouped by category
- Display proficiency level
- Show verification status
- Allow adding/editing skills (with permission)

**Acceptance Criteria:**
- ✅ Clear visual display
- ✅ Filterable by category
- ✅ Shows proficiency clearly

---

### Task 17: Testing and Quality Assurance
**Priority:** P0 (Critical)
**Estimated Time:** 45 minutes

**Requirements:**
- Test all certification CRUD operations
- Test expiry calculations
- Test document uploads
- Test filters and search
- Test permissions (employees can't see others' data unless manager)
- Test dashboard widgets
- Test mobile responsiveness
- Cross-browser testing (Chrome, Firefox, Safari)
- Verify accessibility (screen readers, keyboard navigation)

**Acceptance Criteria:**
- ✅ All features work as expected
- ✅ No console errors
- ✅ No TypeScript errors
- ✅ Build succeeds
- ✅ Performance is good (< 2s page loads)

---

### Task 18: Update README and Documentation
**File:** `README.md`
**Priority:** P1
**Estimated Time:** 20 minutes

**Requirements:**
- Document new certification management features
- Update feature list
- Add screenshots/diagrams
- Document how to use certification dashboard
- Update setup instructions if needed

**Acceptance Criteria:**
- ✅ Clear, professional documentation
- ✅ Examples provided
- ✅ Links to relevant sections

---

## TOTAL ESTIMATED TIME: 9-11 hours

---

## Development Guidelines for This Session

### Quality Standards:
1. **Code Quality:**
   - Follow existing code patterns
   - Write clear, self-documenting code
   - Add comprehensive comments for complex logic
   - Use TypeScript strictly (no `any` types)
   - Follow DRY principles

2. **Testing Strategy:**
   - Manual testing of all features
   - Test edge cases (expired certs, no certs, many certs)
   - Test with different roles (employee, manager, admin)
   - Test error scenarios

3. **UI/UX Standards:**
   - Consistent with existing design
   - Clear visual hierarchy
   - Loading states for all async operations
   - Error messages are helpful
   - Accessibility is not optional

4. **Performance:**
   - Optimize database queries
   - Use pagination for lists
   - Cache appropriately
   - Lazy load when sensible

### Git Strategy:
- One commit per major feature (not per file)
- Descriptive commit messages
- Test before committing
- Push to remote branch regularly

---

## Success Metrics for Phase 1

**Functional:**
- ✅ Managers can view all certifications across their team
- ✅ Managers can see which certifications are expiring
- ✅ Employees can view their own certifications
- ✅ Expired certifications are visually flagged
- ✅ Documents can be uploaded for certifications
- ✅ Dashboard shows certification status

**Technical:**
- ✅ No TypeScript errors
- ✅ No console errors
- ✅ Production build succeeds
- ✅ All API endpoints work
- ✅ Permissions enforced correctly

**Business Value:**
- ✅ Solves compliance tracking problem
- ✅ Prevents scheduling of non-compliant staff (foundation for future)
- ✅ Provides audit trail
- ✅ Reduces manual tracking burden

---

## Future Phases (Not This Session)

### Phase 2: Shift Scheduling Foundation
- Shift models and patterns
- Basic schedule builder
- Shift swap requests
- Coverage visualization

### Phase 3: Advanced Scheduling
- Rule enforcement (minimum rest, max hours)
- Fair distribution analytics
- Overtime tracking
- Integration with payroll

### Phase 4: Skills-Based Scheduling
- Match patient acuity to staff skills
- Certification-aware scheduling
- Competency-based assignments

### Phase 5: Analytics and Reporting
- Compliance reports
- Staffing analytics
- Predictive analytics
- Custom dashboards

### Phase 6: Mobile Optimization
- Native mobile app or PWA
- Push notifications
- Offline capability
- Quick actions

---

## Dependencies and Risks

### Dependencies:
- Django backend must be running
- Database migrations must succeed
- File upload infrastructure needed for documents
- Existing employee system must be working

### Risks:
- **Time:** This is a lot of work - may not finish all 18 tasks
- **Complexity:** Healthcare compliance is complex
- **Quality vs. Speed:** Emphasis on quality may mean fewer features
- **Integration:** May discover gaps in existing system

### Mitigation:
- Focus on core tasks (1-13) first
- Tasks 14-16 (skills) are nice-to-have
- Prioritize working features over complete coverage
- Get something deployable, even if not everything

---

## Notes for Developer

**Start Here:**
1. Begin with Task 1 (models) - everything depends on this
2. Work through tasks sequentially - they build on each other
3. Test as you go - don't wait until the end
4. Commit frequently - don't lose work
5. If stuck, skip and come back - don't block on one task
6. Focus on MVP for each feature - perfect is the enemy of good
7. But remember: this is healthcare - quality matters

**Key Principles:**
- Patient safety depends on accurate certification tracking
- Compliance is binary - either compliant or not
- User experience matters - tired ICU managers need simple, clear interfaces
- Performance matters - this will be used during time-sensitive situations
- Security matters - employee data is sensitive

**When in Doubt:**
- Simpler is better
- Clear error messages
- Obvious user flows
- Defensive programming
- Ask "would I trust this in a real ICU?"

---

**This todo list represents a focused, achievable plan to deliver high-value features with the quality and precision required for healthcare software. The emphasis is on doing fewer things exceptionally well rather than many things poorly.**
