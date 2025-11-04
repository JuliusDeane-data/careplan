# Careplan Project - Next Steps & Roadmap

**Date Created**: 2025-11-04
**Status**: Ready for Next Phase
**Current Phase**: Post-Refactoring, Pre-API Development

---

## 🎯 Project Overview

The Careplan project is a comprehensive care facility management system built with Django and DRF. The core models and admin interface are complete, with the User-Employee refactoring successfully implemented.

---

## ✅ What's Already Complete

### 1. Core Infrastructure ✅
- **Core App**: Fully implemented and tested (26 tests passing)
  - Base models (TimeStamped, SoftDelete, Audit, BaseModel)
  - Custom managers and querysets
  - Date utilities for vacation calculations
  - Validators (phone, postal code, dates, etc.)
  - Helper functions
  - Middleware (logging, timezone)
  - Constants and mixins

### 2. User & Employee Models ✅
- **User-Employee Refactoring**: Successfully completed
  - User model now contains all employee data
  - No separate Employee model (merged architecture)
  - Location relationships working (primary + additional)
  - Qualifications system in place
  - Employee documents model
  - All migrations applied successfully

### 3. Location Management ✅
- Location model with manager relationship
- Admin interface configured
- Database migrations applied

### 4. Database & Migrations ✅
- PostgreSQL database running in Docker
- All migrations applied successfully
- Proper indexes and relationships established
- Circular dependency issues resolved

### 5. Admin Interface ✅
- UserAdmin with all employee fields
- LocationAdmin with manager field
- Superuser created (username: admin, password: admin123)
- Admin accessible at http://localhost:8000/admin/

### 6. Development Environment ✅
- Docker Compose setup (web, db, redis, celery, celery-beat)
- All containers running and healthy
- Environment variables configured

---

## 🚀 Immediate Next Steps (Priority Order)

### Phase 1: Manual Testing & Validation (1-2 hours)

**Goal**: Verify all models work correctly through Django admin

#### Tasks:
1. **Test Location Management**
   - [ ] Create 3-5 locations (different care facilities)
   - [ ] Test location activation/deactivation
   - [ ] Verify soft delete functionality
   - [ ] Check audit trail (created_by, updated_by)

2. **Test Qualifications**
   - [ ] Create common qualifications (RN, CNA, LPN, etc.)
   - [ ] Test activation/deactivation
   - [ ] Verify uniqueness of qualification codes

3. **Test User/Employee Creation**
   - [ ] Create multiple users with employee data
   - [ ] Assign primary and additional locations
   - [ ] Assign qualifications to users
   - [ ] Test supervisor relationships
   - [ ] Verify vacation day tracking
   - [ ] Upload employee documents
   - [ ] Test document expiry tracking

4. **Test Location Manager Assignment**
   - [ ] Assign managers to locations
   - [ ] Verify manager must be a User
   - [ ] Test manager switching

5. **Data Validation Testing**
   - [ ] Test phone number validation
   - [ ] Test postal code validation
   - [ ] Test date range validations
   - [ ] Test employment status transitions

**Expected Outcome**: Confidence that all models work correctly before building APIs

---

### Phase 2: Notifications App Implementation (2-3 hours)

**Goal**: Build notification system for important events

#### Models to Create:
1. **Notification Model**
   ```python
   - recipient (FK to User)
   - notification_type (choices: VACATION_REQUEST, VACATION_APPROVED, etc.)
   - title (CharField)
   - message (TextField)
   - is_read (Boolean, default=False)
   - read_at (DateTime, null)
   - related_object_id (GenericForeignKey - for linking to vacation, etc.)
   - action_url (URLField, optional)
   - created_at (auto)
   ```

2. **NotificationPreference Model** (Optional)
   ```python
   - user (OneToOne to User)
   - email_notifications (Boolean)
   - push_notifications (Boolean)
   - notification_types (JSON - which types to receive)
   ```

#### Implementation Steps:
- [ ] Create Notification model with BaseModel
- [ ] Create NotificationPreference model
- [ ] Configure admin interface
- [ ] Create migrations and apply
- [ ] Add helper function: `send_notification(user, type, title, message)`
- [ ] Write model tests
- [ ] Test via admin interface

**Expected Outcome**: Working notification system ready for integration

---

### Phase 3: Vacation App Implementation (3-4 hours)

**Goal**: Complete vacation request and approval system

#### Models to Create:
1. **VacationRequest Model**
   ```python
   - employee (FK to User)
   - start_date (DateField)
   - end_date (DateField)
   - vacation_days (IntegerField - calculated, excludes weekends)
   - total_days (IntegerField - calendar days)
   - status (PENDING, APPROVED, DENIED, CANCELLED)
   - request_type (ANNUAL_LEAVE, SICK_LEAVE, UNPAID_LEAVE, etc.)
   - reason (TextField, optional)
   - approved_by (FK to User, null)
   - approved_at (DateTime, null)
   - denial_reason (TextField, null)
   - cancelled_at (DateTime, null)
   - notes (TextField)
   ```

2. **PublicHoliday Model** (Optional but recommended)
   ```python
   - date (DateField)
   - name (CharField - e.g., "Christmas")
   - location (FK to Location, null - null means all locations)
   - is_nationwide (Boolean)
   ```

#### Business Logic:
- [ ] Auto-calculate vacation_days using `get_vacation_days_count()`
- [ ] Validate no overlapping vacation requests
- [ ] Check sufficient remaining vacation days
- [ ] Prevent vacation requests in the past
- [ ] Require minimum advance notice (from constants)
- [ ] Support location-specific public holidays

#### Signals to Create:
- [ ] On approval: Update user's remaining_vacation_days
- [ ] On approval: Send notification to employee
- [ ] On denial: Send notification with reason
- [ ] On cancellation: Restore vacation days

#### Implementation Steps:
- [ ] Create VacationRequest model
- [ ] Create PublicHoliday model
- [ ] Create custom VacationManager with query methods
- [ ] Configure admin with filters and actions
- [ ] Create signals for vacation balance updates
- [ ] Write validation logic
- [ ] Create migrations and apply
- [ ] Write comprehensive tests
- [ ] Test via admin interface

**Expected Outcome**: Complete vacation management system

---

### Phase 4: REST API Development (5-7 hours)

**Goal**: Build comprehensive REST API for all features

#### API Structure:

**Accounts/Users API**:
- [ ] UserSerializer (list, detail, create, update)
- [ ] UserViewSet with custom actions:
  - `GET /api/users/me/` - Current user profile
  - `GET /api/users/{id}/vacation-balance/` - Vacation info
  - `POST /api/users/{id}/terminate/` - Terminate employee
  - `GET /api/users/{id}/documents/` - Employee documents
- [ ] Permissions: IsAdminOrPlanner, IsOwnerOrAdmin

**Locations API**:
- [ ] LocationSerializer (list, detail)
- [ ] LocationViewSet with custom actions:
  - `GET /api/locations/{id}/employees/` - All employees
  - `GET /api/locations/{id}/coverage/` - Shift coverage stats
- [ ] Permissions: IsAuthenticated

**Qualifications API**:
- [ ] QualificationSerializer
- [ ] QualificationViewSet (CRUD)
- [ ] Permissions: IsAdminOrPlanner

**Employee Documents API**:
- [ ] EmployeeDocumentSerializer
- [ ] EmployeeDocumentViewSet
- [ ] File upload support
- [ ] Expiry tracking endpoint
- [ ] Permissions: IsOwnerOrAdminOrPlanner

**Notifications API**:
- [ ] NotificationSerializer
- [ ] NotificationViewSet with custom actions:
  - `GET /api/notifications/unread/` - Unread notifications
  - `POST /api/notifications/{id}/mark-read/` - Mark as read
  - `POST /api/notifications/mark-all-read/` - Mark all read
- [ ] Permissions: IsOwner (users see only their notifications)

**Vacation API**:
- [ ] VacationRequestSerializer (with validation)
- [ ] VacationRequestViewSet with custom actions:
  - `GET /api/vacation/my-requests/` - Current user's requests
  - `POST /api/vacation/{id}/approve/` - Approve request
  - `POST /api/vacation/{id}/deny/` - Deny request
  - `POST /api/vacation/{id}/cancel/` - Cancel request
  - `GET /api/vacation/calendar/` - Team vacation calendar
  - `GET /api/vacation/balance/` - Remaining vacation days
- [ ] Permissions: Complex (owner can create/cancel, managers can approve)

**Public Holidays API**:
- [ ] PublicHolidaySerializer
- [ ] PublicHolidayViewSet
- [ ] `GET /api/holidays/?location={id}&year={year}` - Filter by location/year

#### API Features:
- [ ] JWT Authentication (or DRF Token Auth)
- [ ] Pagination (page size: 20)
- [ ] Filtering (django-filter)
- [ ] Search capabilities
- [ ] Proper error handling
- [ ] API documentation (drf-spectacular or Swagger)
- [ ] Rate limiting
- [ ] CORS configuration

#### Implementation Steps:
1. [ ] Set up DRF router and URL structure
2. [ ] Create serializers for all models
3. [ ] Create permissions classes
4. [ ] Create viewsets with custom actions
5. [ ] Configure filtering and pagination
6. [ ] Add API documentation
7. [ ] Write API tests (using DRF test client)
8. [ ] Test all endpoints with Postman/curl

**Expected Outcome**: Fully functional REST API

---

### Phase 5: Frontend Integration Preparation (1-2 hours)

**Goal**: Prepare backend for frontend consumption

#### Tasks:
- [ ] Set up CORS properly for frontend domain
- [ ] Create comprehensive API documentation
- [ ] Add API versioning (e.g., `/api/v1/...`)
- [ ] Create example API responses document
- [ ] Set up API health check endpoint
- [ ] Configure static file serving
- [ ] Configure media file serving (for uploads)

**Expected Outcome**: Backend ready for frontend integration

---

## 🔄 Continuous Improvements (Ongoing)

### Testing
- [ ] Increase test coverage to 80%+
- [ ] Add integration tests
- [ ] Add performance tests
- [ ] Set up CI/CD pipeline

### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Developer setup guide
- [ ] Deployment guide
- [ ] User manual

### Performance
- [ ] Database query optimization
- [ ] Add caching (Redis)
- [ ] Implement background tasks (Celery)
- [ ] Monitor slow queries

### Security
- [ ] Security audit
- [ ] Rate limiting
- [ ] Input sanitization review
- [ ] GDPR compliance check

---

## 📋 Detailed Task Breakdown

### High Priority (Do First)

#### 1. Manual Testing Session (Today)
**Time**: 1-2 hours
**Dependencies**: None
**Output**: Validated models, test data created

#### 2. Notifications App (This Week)
**Time**: 2-3 hours
**Dependencies**: Manual testing complete
**Output**: Notification system ready

#### 3. Vacation App (This Week)
**Time**: 3-4 hours
**Dependencies**: Notifications app (for sending notifications)
**Output**: Complete vacation management

### Medium Priority (Next Week)

#### 4. REST API - Core Resources (Week 2)
**Time**: 3-4 hours
**Focus**: Users, Locations, Qualifications
**Output**: Basic CRUD APIs

#### 5. REST API - Advanced Features (Week 2)
**Time**: 2-3 hours
**Focus**: Vacation, Notifications, Custom Actions
**Output**: Complete API

### Lower Priority (Future)

#### 6. Frontend Preparation
**Time**: 1-2 hours
**Dependencies**: API complete

#### 7. Testing & Documentation
**Time**: Ongoing
**Dependencies**: Features complete

---

## 🎯 Success Metrics

### Phase 1 Complete When:
- ✅ Can create locations, users, qualifications via admin
- ✅ All validations work correctly
- ✅ Audit trail captures all changes
- ✅ Soft delete works as expected

### Phase 2 Complete When:
- ✅ Notifications can be created programmatically
- ✅ Notifications appear in admin
- ✅ Read/unread status tracking works

### Phase 3 Complete When:
- ✅ Can request vacation via admin
- ✅ Can approve/deny vacation requests
- ✅ Vacation days auto-calculate correctly
- ✅ Balance updates on approval
- ✅ Notifications sent on status changes

### Phase 4 Complete When:
- ✅ All CRUD operations via API
- ✅ Authentication working
- ✅ Permissions enforced correctly
- ✅ API tests passing
- ✅ Documentation generated

### Phase 5 Complete When:
- ✅ CORS configured
- ✅ API docs published
- ✅ Health check endpoint working
- ✅ Media uploads working

---

## 🛠 Technical Decisions Needed

### Questions to Answer:
1. **Authentication**: JWT or Token Auth?
2. **API Versioning**: URL-based (/api/v1/) or Header-based?
3. **File Storage**: Local filesystem or cloud (S3)?
4. **Email Notifications**: Enable now or later?
5. **Real-time Updates**: WebSockets needed for notifications?
6. **Shift Scheduling**: Part of vacation app or separate?
7. **Reporting**: Build analytics now or later?

---

## 📚 Resources & References

### Documentation to Create:
- [ ] API Reference Guide
- [ ] Data Model ERD Diagram
- [ ] Business Logic Documentation
- [ ] Deployment Checklist
- [ ] Troubleshooting Guide

### Existing Documentation:
- ✅ Core App Completion Report: `plans/COMPLETED_core_app.md`
- ✅ Employees & Locations Status: `plans/STATUS_employees_locations.md`
- ✅ User-Employee Refactoring Status: `plans/STATUS_refactoring_user_employee.md`
- ✅ Employees App Plan: `plans/employees_app.md`
- ✅ Core App Plan: `plans/core_app.md`

---

## 🚨 Known Issues & Blockers

### Current Issues:
- None! System is stable and ready for next phase.

### Warnings in Docker:
- `The "d" variable is not set` - Cosmetic only, doesn't affect functionality
- Can be fixed by adding `d=` to .env file if needed

---

## 💡 Recommendations

### Immediate Actions:
1. **Start with Manual Testing** - Validate everything works before building on top
2. **Create Test Data** - Build realistic dataset for development
3. **Document Assumptions** - Write down business rules discovered during testing

### Best Practices:
- Commit after each phase completion
- Write tests alongside features (TDD)
- Update status documents after each phase
- Keep migrations small and focused
- Use feature branches for major changes

### Architecture Decisions:
- ✅ User IS Employee (merged model) - Simpler and more maintainable
- ✅ Soft delete everywhere - Preserve data for audit
- ✅ Vacation days exclude weekends - Correct for shift work
- ✅ Location-based permissions - Employees tied to locations

---

## 📅 Suggested Timeline

### Week 1 (Current Week):
- **Day 1**: Manual testing (1-2 hours)
- **Day 2**: Notifications app (2-3 hours)
- **Day 3-4**: Vacation app (3-4 hours)
- **Day 5**: Testing and bug fixes

### Week 2:
- **Day 1-3**: REST API core resources (3-4 hours)
- **Day 4-5**: REST API advanced features (2-3 hours)

### Week 3:
- **Day 1**: Frontend preparation (1-2 hours)
- **Day 2-5**: Testing, documentation, polish

---

## ✅ Next Action: Manual Testing

**Recommended First Step**: Start a manual testing session to validate all models

1. Open admin: http://localhost:8000/admin/
2. Login: admin / admin123
3. Follow Phase 1 testing checklist above
4. Document any issues found
5. Create realistic test data for future API testing

**After Testing**: Choose between Phase 2 (Notifications) or Phase 3 (Vacation) based on priority

---

**Document Status**: Living document - update after each phase
**Last Updated**: 2025-11-04
**Next Review**: After Phase 1 completion
