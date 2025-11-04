# Careplan Project Plan

## Project Overview
Careplan is a modular management software for care workers, designed to handle employee management, shift planning, vacation tracking, and more. The system must support 100+ concurrent users efficiently.

## Technology Stack

### Backend
- **Framework**: Django 5.x (LTS)
- **Database**: PostgreSQL 15+ (with connection pooling)
- **Cache**: Redis (session storage, query caching, rate limiting)
- **Task Queue**: Celery with Redis broker (async notifications, reports)
- **API**: Django REST Framework (DRF)
- **Package Management**: pip + requirements.txt (with pip-tools for dependency management)

### Infrastructure & Scalability
- **WSGI Server**: Gunicorn with multiple worker processes
- **Reverse Proxy**: Nginx (static files, load balancing, SSL termination)
- **Database Connection Pooling**: pgBouncer or Django's persistent connections
- **Session Backend**: Redis (faster than database sessions)
- **File Storage**: Cloud storage (S3/MinIO) for uploaded documents
- **Monitoring**: Django Debug Toolbar (dev), logging infrastructure

### Development Tools
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest + pytest-django + coverage
- **Code Quality**: flake8, black, isort
- **Version Control**: Git with feature branch workflow

## Project Structure

```
careplan/
├── manage.py
├── requirements/
│   ├── base.txt           # Core dependencies
│   ├── development.txt    # Dev tools (extends base)
│   └── production.txt     # Production deps (extends base)
├── config/                # Project settings package
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py       # Common settings
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py           # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── apps/                  # All Django apps
│   ├── core/             # Shared utilities, base models, mixins
│   ├── accounts/         # User authentication & authorization
│   ├── employees/        # Employee management
│   ├── locations/        # Location management
│   ├── notifications/    # Notification system
│   ├── vacation/         # Vacation planner module
│   ├── shifts/           # Future: Shift management
│   ├── timetracking/     # Future: Time tracking
│   └── payroll/          # Future: Salary management
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded files (development only)
├── templates/            # Global templates
├── logs/                 # Application logs
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
└── tests/                # Integration tests
```

## Phase 1: Initial Setup & Infrastructure

### 1.1 Project Initialization
- [ ] Create Django project with custom settings structure
- [ ] Set up pip requirements files (base, development, production)
- [ ] Configure PostgreSQL database connection
- [ ] Set up Redis for caching and sessions
- [ ] Configure environment variables (.env file, python-decouple)
- [ ] Initialize Git with .gitignore

### 1.2 Scalability Configuration
- [ ] Configure database connection pooling (CONN_MAX_AGE)
- [ ] Set up Redis cache backend for queries and sessions
- [ ] Configure static file handling (WhiteNoise or Nginx)
- [ ] Set up logging (file-based + console, with rotation)
- [ ] Configure Gunicorn with optimal worker count
- [ ] Database query optimization settings (query logging, select_related defaults)

### 1.3 Docker Development Environment
- [ ] Dockerfile for Django application
- [ ] docker-compose.yml with services:
  - Django app
  - PostgreSQL
  - Redis
  - Celery worker
  - Nginx (optional for local testing)
- [ ] Database initialization scripts
- [ ] Volume configuration for development

### 1.4 Testing & Quality Infrastructure
- [ ] Set up pytest with pytest-django
- [ ] Configure coverage reporting
- [ ] Set up black, flake8, isort configuration
- [ ] Pre-commit hooks (optional)
- [ ] CI/CD configuration placeholder (GitHub Actions/GitLab CI)

## Phase 2: Core/Base Modules

### 2.1 Core App (Shared Foundation)
**Purpose**: Shared utilities, base models, and common functionality

**Components**:
- [ ] Base abstract models (TimeStampedModel, SoftDeleteModel)
- [ ] Custom mixins and managers
- [ ] Utility functions (date helpers, validators)
- [ ] Custom middleware (request logging, performance monitoring)
- [ ] Exception handlers
- [ ] Common serializers base classes

**Scalability Considerations**:
- Use `select_related()` and `prefetch_related()` in base querysets
- Implement efficient soft-delete with indexed fields
- Add created_by/modified_by tracking for audit trails

### 2.2 Accounts App (Authentication & Authorization)
**Purpose**: User management, authentication, and role-based access control

**Models**:
- [ ] Custom User model (extending AbstractUser)
  - Fields: email (unique), role, is_active, is_staff
  - Roles: EMPLOYEE, SUPERVISOR, PLANNER, ADMIN
- [ ] UserProfile (one-to-one with User)
  - Additional user preferences
  - Notification settings

**Features**:
- [ ] JWT token authentication (djangorestframework-simplejwt)
- [ ] Role-based permissions (custom permission classes)
- [ ] Password management endpoints
- [ ] Login/logout with throttling (prevent brute force)
- [ ] Token refresh mechanism
- [ ] User registration workflow (admin-initiated)

**API Endpoints**:
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/refresh/` - Refresh token
- `POST /api/v1/auth/password/change/` - Change password
- `POST /api/v1/auth/password/reset/` - Request password reset
- `POST /api/v1/auth/password/reset/confirm/` - Confirm reset

**Scalability Considerations**:
- Use Redis for token blacklist (logout)
- Implement rate limiting on authentication endpoints
- Session storage in Redis, not database
- Index on email and username fields

### 2.3 Locations App
**Purpose**: Manage care facility locations

**Models**:
- [ ] Location
  - Fields: name, address, city, postal_code, phone, email
  - Fields: is_active, max_capacity, manager (FK to User)
  - Timestamps (created_at, updated_at)

**Features**:
- [ ] CRUD operations (admin/planner only)
- [ ] List all locations (filtered by user permissions)
- [ ] Location details with employee count
- [ ] Search and filtering

**API Endpoints**:
- `GET /api/v1/locations/` - List locations
- `POST /api/v1/locations/` - Create location (admin)
- `GET /api/v1/locations/{id}/` - Location details
- `PUT/PATCH /api/v1/locations/{id}/` - Update location (admin)
- `DELETE /api/v1/locations/{id}/` - Deactivate location (admin)
- `GET /api/v1/locations/{id}/employees/` - Employees at location

**Scalability Considerations**:
- Simple model, minimal joins
- Cache location list (changes infrequently)
- Pagination for employee lists

### 2.4 Employees App
**Purpose**: Employee profile and HR data management

**Models**:
- [ ] Employee
  - User (one-to-one with User model)
  - Personal info: first_name, last_name, date_of_birth
  - Contact: phone, email, address, city, postal_code
  - Employment: employee_id, hire_date, employment_status
  - Location: primary_location (FK), additional_locations (M2M)
  - Supervisor: supervisor (FK to User, nullable)
  - Qualifications: qualifications (M2M to Qualification model)
  - Vacation: annual_vacation_days (integer)
  - Salary: salary_info (consider separate model for sensitivity)
  - Timestamps and soft delete

- [ ] Qualification
  - Fields: name, description, code
  - Valid for role assignments

- [ ] EmploymentStatus (choices: ACTIVE, ON_LEAVE, TERMINATED)

**Features**:
- [ ] Employee CRUD (admin/planner)
- [ ] Employee self-service profile updates (limited fields: phone, address)
- [ ] View own profile
- [ ] List employees by location
- [ ] Search employees (by name, ID, qualification)
- [ ] Filtering (by location, status, qualification)
- [ ] Bulk import employees (CSV)

**API Endpoints**:
- `GET /api/v1/employees/` - List employees (paginated, filtered)
- `POST /api/v1/employees/` - Create employee (admin)
- `GET /api/v1/employees/me/` - Current user's employee profile
- `GET /api/v1/employees/{id}/` - Employee details
- `PUT/PATCH /api/v1/employees/{id}/` - Update employee
- `PATCH /api/v1/employees/me/` - Self-service update (limited)
- `DELETE /api/v1/employees/{id}/` - Deactivate employee
- `GET /api/v1/employees/{id}/vacation-balance/` - Vacation balance
- `GET /api/v1/qualifications/` - List qualifications

**Scalability Considerations**:
- Index on employee_id, user_id, primary_location
- Use select_related('user', 'primary_location', 'supervisor')
- Prefetch M2M relationships (qualifications, additional_locations)
- Pagination with configurable page size (default 50)
- Cache qualification list
- Optimize search with database full-text search or ElasticSearch (future)

### 2.5 Notifications App
**Purpose**: Centralized notification system

**Models**:
- [ ] Notification
  - Fields: recipient (FK to User), sender (FK, nullable)
  - Fields: notification_type, title, message, link
  - Fields: is_read, sent_via_email, email_sent_at
  - Timestamps

- [ ] NotificationPreference (per user)
  - Fields: user, notification_type, email_enabled, in_app_enabled

**Features**:
- [ ] Create notifications (programmatically)
- [ ] Mark as read
- [ ] List user notifications (paginated)
- [ ] Real-time notifications (optional: Django Channels + WebSockets)
- [ ] Email sending (Celery async task)
- [ ] Notification preferences management

**Notification Types**:
- VACATION_REQUEST_SUBMITTED
- VACATION_REQUEST_APPROVED
- VACATION_REQUEST_DENIED
- VACATION_REQUEST_MODIFIED
- SHIFT_ASSIGNED
- PROFILE_UPDATED

**API Endpoints**:
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/notifications/unread/` - Unread count
- `PATCH /api/v1/notifications/{id}/read/` - Mark as read
- `POST /api/v1/notifications/mark-all-read/` - Mark all read
- `GET /api/v1/notifications/preferences/` - Get preferences
- `PATCH /api/v1/notifications/preferences/` - Update preferences

**Scalability Considerations**:
- Index on recipient + is_read + created_at
- Use Celery for email sending (non-blocking)
- Pagination with cursor-based pagination for real-time feeds
- Implement notification archival (auto-delete after 90 days)
- Use database triggers or signals efficiently (avoid N+1)
- Consider Redis pub/sub for real-time features

## Phase 3: Vacation Planner Module (First Feature Module)

### 3.1 Vacation App Models

**VacationRequest**:
- [ ] employee (FK to Employee)
- [ ] start_date (DateField)
- [ ] end_date (DateField)
- [ ] total_days (Integer, calculated excluding weekends/holidays)
- [ ] status (PENDING, APPROVED, DENIED, CANCELLED)
- [ ] request_note (TextField, optional)
- [ ] response_note (TextField, optional - from supervisor)
- [ ] reviewed_by (FK to User, nullable)
- [ ] reviewed_at (DateTimeField, nullable)
- [ ] created_at, updated_at
- [ ] Validation: ensure dates don't overlap for same employee

**VacationBalance** (denormalized for performance):
- [ ] employee (OneToOne to Employee)
- [ ] total_days (from Employee.annual_vacation_days)
- [ ] used_days (approved vacation)
- [ ] pending_days (pending requests)
- [ ] remaining_days (calculated)
- [ ] last_updated (auto-updated via signals)

**PublicHoliday** (optional but recommended):
- [ ] date (DateField, unique)
- [ ] name (CharField)
- [ ] location (FK to Location, nullable - for location-specific holidays)

### 3.2 Business Logic

**Vacation Day Calculation**:
- [ ] Calculate working days between dates (exclude weekends)
- [ ] Exclude public holidays
- [ ] Handle partial days (if applicable)

**Validation Rules**:
- [ ] Employee has sufficient remaining days
- [ ] No overlapping requests for same employee
- [ ] Start date < end date
- [ ] Cannot request dates in the past
- [ ] Advance notice requirement (configurable, e.g., 14 days)

**Approval Workflow**:
- [ ] Employee submits request → status: PENDING
- [ ] Notification sent to supervisor
- [ ] Supervisor approves/denies/modifies
- [ ] Notification sent back to employee
- [ ] Vacation balance updated automatically

**Conflict Detection**:
- [ ] Check if too many employees at same location request same dates
- [ ] Configurable threshold (e.g., max 30% of staff on vacation)
- [ ] Warning to supervisor (not blocking)

### 3.3 Employee Interface Features

- [ ] View vacation calendar for own location (month view)
- [ ] Submit vacation request (single or date range)
- [ ] View own vacation requests (all statuses)
- [ ] View remaining vacation balance
- [ ] Cancel pending request
- [ ] View colleagues' approved vacations (anonymized or full names)

### 3.4 Supervisor Interface Features

- [ ] View pending requests for team members
- [ ] Approve/deny requests
- [ ] Modify request dates (with employee notification)
- [ ] View team vacation calendar
- [ ] View conflict warnings
- [ ] Bulk approve requests (optional)

### 3.5 API Endpoints

**Employee Endpoints**:
- `GET /api/v1/vacation/requests/` - List own vacation requests
- `POST /api/v1/vacation/requests/` - Submit vacation request
- `GET /api/v1/vacation/requests/{id}/` - Request details
- `DELETE /api/v1/vacation/requests/{id}/` - Cancel pending request
- `GET /api/v1/vacation/balance/` - View vacation balance
- `GET /api/v1/vacation/calendar/` - Calendar view (month-based)
  - Query params: year, month, location_id
  - Returns: grid of employees × days with vacation status

**Supervisor Endpoints**:
- `GET /api/v1/vacation/requests/pending/` - Pending requests for team
- `POST /api/v1/vacation/requests/{id}/approve/` - Approve request
- `POST /api/v1/vacation/requests/{id}/deny/` - Deny request
- `PATCH /api/v1/vacation/requests/{id}/modify/` - Modify dates
- `GET /api/v1/vacation/team-calendar/` - Team vacation overview
- `GET /api/v1/vacation/conflicts/` - Check conflicts for date range

**Admin Endpoints**:
- `GET /api/v1/vacation/public-holidays/` - List holidays
- `POST /api/v1/vacation/public-holidays/` - Add holiday
- `GET /api/v1/vacation/statistics/` - Vacation statistics

### 3.6 Scalability Considerations for Vacation Module

**Database Optimization**:
- [ ] Index on employee_id + status + start_date
- [ ] Index on location + start_date + end_date (calendar queries)
- [ ] Composite index for date range queries
- [ ] Use database constraints (check: end_date >= start_date)

**Query Optimization**:
- [ ] Calendar view: Single query with prefetch_related for employee data
- [ ] Use Django's Q objects efficiently for date range filters
- [ ] Annotate vacation counts at database level
- [ ] Cache public holidays (rarely change)

**Caching Strategy**:
- [ ] Cache vacation balance per employee (invalidate on request approval)
- [ ] Cache monthly calendar view (5-minute TTL)
- [ ] Cache-aside pattern for frequently accessed data

**Performance Targets**:
- Calendar view query: < 200ms for 50 employees
- Balance calculation: < 50ms
- Request submission: < 100ms
- Support 100 concurrent calendar views

**Async Operations**:
- [ ] Send notifications via Celery (don't block request/response)
- [ ] Generate vacation reports in background
- [ ] Bulk operations (imports) as Celery tasks

## Phase 4: Future Modules (Roadmap)

### 4.1 Shifts Module
- Shift templates (8h, 12h shifts)
- Shift scheduling and assignment
- Shift swapping functionality
- Integration with employee qualifications and locations

### 4.2 Time Tracking Module
- Clock in/out system
- Work hours calculation and validation
- Overtime tracking
- Integration with shift schedules

### 4.3 Onboarding/Offboarding Module
- Employee lifecycle workflows
- Document management (contracts, certifications)
- Task checklists for HR
- Equipment tracking

### 4.4 Payroll Module
- Salary calculation based on hours worked
- Overtime compensation
- Payroll history and reports
- Integration with time tracking

### 4.5 Reporting Module
- Customizable reports
- Export to PDF/Excel
- Scheduled report generation
- Dashboard with KPIs

## Scalability Best Practices

### Database
1. **Connection Pooling**: Configure `CONN_MAX_AGE` and use pgBouncer
2. **Indexing**: Add indexes on foreign keys and frequently queried fields
3. **Query Optimization**: Use `select_related()`, `prefetch_related()`, `only()`, `defer()`
4. **Read Replicas**: Consider read replicas for reporting queries (future)

### Caching
1. **Redis Backend**: Cache views, querysets, and computed data
2. **Cache Warming**: Pre-populate cache for frequently accessed data
3. **Cache Invalidation**: Clear cache on data changes (signals or explicit)
4. **Template Caching**: Cache rendered templates where appropriate

### Application Server
1. **Gunicorn Workers**: Formula: (2 × CPU cores) + 1
2. **Worker Timeout**: Set appropriate timeout (30-60 seconds)
3. **Worker Class**: Use sync workers unless async features needed
4. **Graceful Restarts**: Zero-downtime deployments

### Asynchronous Processing
1. **Celery Tasks**: Email, reports, imports, exports
2. **Task Queue**: Redis as broker
3. **Result Backend**: Redis for task results
4. **Monitoring**: Flower for Celery monitoring

### Security
1. **Rate Limiting**: Throttle API endpoints (django-ratelimit or DRF throttling)
2. **Input Validation**: Use DRF serializers strictly
3. **SQL Injection**: Use Django ORM (avoid raw SQL)
4. **XSS Protection**: Django's built-in escaping
5. **CSRF Protection**: Enable for non-API views
6. **HTTPS Only**: Enforce SSL in production
7. **Secrets Management**: Environment variables, never in code

### Monitoring & Logging
1. **Application Logs**: Structured logging with log levels
2. **Error Tracking**: Sentry or similar (optional)
3. **Performance Monitoring**: Django Debug Toolbar (dev), APM (prod)
4. **Database Slow Query Log**: Identify optimization opportunities
5. **Health Check Endpoint**: `/health/` for load balancer

## Development Workflow

### Git Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Production hotfixes

### Code Review
- All changes via pull requests
- Required reviews before merge
- Automated checks (tests, linting)

### Testing Strategy
1. **Unit Tests**: Test models, utilities, business logic (>80% coverage)
2. **Integration Tests**: Test API endpoints, workflows
3. **Load Testing**: Simulate 100+ concurrent users (locust, JMeter)
4. **Database Tests**: Test with production-like data volume

### Deployment Pipeline
1. Code commit → Git push
2. Run automated tests (CI)
3. Run linting and code quality checks
4. Build Docker image (if passing)
5. Deploy to staging environment
6. Manual QA/approval
7. Deploy to production
8. Run smoke tests

## Initial Implementation Priority

1. **Phase 1**: Setup (1-2 weeks)
   - Django project structure
   - Docker environment
   - Database setup
   - Basic authentication

2. **Phase 2**: Core modules (2-3 weeks)
   - Accounts app with JWT auth
   - Employees app with CRUD
   - Locations app
   - Notifications app (basic)

3. **Phase 3**: Vacation module (2-3 weeks)
   - Models and migrations
   - Business logic and validation
   - API endpoints
   - Calendar view optimization

4. **Testing & Optimization** (1 week)
   - Load testing
   - Performance tuning
   - Security audit

**Total estimated time for MVP with vacation module: 6-9 weeks**

## Success Metrics

- Support 100 concurrent users with < 500ms average response time
- 99.9% uptime
- < 1% error rate
- Database query time < 100ms (95th percentile)
- API endpoint response time < 200ms (95th percentile)
- Zero security vulnerabilities (critical/high)
