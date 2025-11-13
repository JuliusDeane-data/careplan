# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CarePlan is a full-stack care worker management system built with Django (backend) and React (frontend). It handles employee management, vacation planning, location management, and notifications for care facilities supporting 100+ concurrent users.

**Tech Stack:**
- Backend: Django 5.2.7 + Django REST Framework + PostgreSQL + Redis + Celery
- Frontend: React 19 + TypeScript + Vite + Tailwind CSS + TanStack Query
- Infrastructure: Docker Compose for local development

## Development Commands

### Backend (Django)

**Docker Commands (Recommended):**
```bash
# Start all services (web, db, redis, celery, celery-beat)
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web pytest

# Run tests with coverage
docker-compose exec web pytest --cov=apps --cov-report=html

# Django shell
docker-compose exec web python manage.py shell

# Create new app
docker-compose exec web python manage.py startapp <app_name> apps/<app_name>

# Make migrations
docker-compose exec web python manage.py makemigrations
```

**Local Development (without Docker):**
```bash
# Install dependencies
pip install -r requirements/development.txt

# Run development server
python manage.py runserver

# Run Celery worker
celery -A config worker -l info

# Run Celery beat (scheduled tasks)
celery -A config beat -l info

# Run tests
pytest

# Code quality
black .              # Format code
isort .              # Sort imports
flake8               # Lint
pylint apps/         # Advanced linting
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Architecture

### Backend Structure

**Apps-based architecture:** All Django apps live in `apps/` directory:

- **`apps/core/`** - Foundation layer providing base models and utilities
  - `BaseModel`: Combines timestamps, soft delete, and audit tracking
  - All models should inherit from `BaseModel` for consistency
  - Provides `TimeStampedModel`, `SoftDeleteModel`, `AuditModel` mixins

- **`apps/accounts/`** - Authentication and user management
  - Custom `User` model extends `AbstractUser` with employee fields
  - **Important:** User model IS the employee model (no separate Employee model)
  - Handles JWT authentication via `djangorestframework-simplejwt`

- **`apps/employees/`** - Employee-related functionality
  - `Qualification`: Certifications/licenses (RN, CNA, etc.)
  - `EmployeeDocument`: Document storage linked to User model

- **`apps/locations/`** - Multi-location support
  - Users can be assigned to locations
  - Public holidays can be location-specific

- **`apps/vacation/`** - Vacation request and approval system
  - `VacationRequest`: Main vacation request model
  - `PublicHoliday`: Holiday definitions (nationwide or location-specific)
  - Automatic calculation of vacation days excluding weekends/holidays

- **`apps/notifications/`** - Real-time notification system
  - Integrated with vacation approvals and updates

- **`apps/api/`** - Central API endpoint definitions
  - All API routes defined in `apps/api/urls.py`
  - ViewSets organized by domain in `apps/api/views/`

**Key Settings:**
- Custom user model: `AUTH_USER_MODEL = 'accounts.User'`
- PostgreSQL database with connection pooling (CONN_MAX_AGE=600)
- Redis for caching and sessions
- JWT tokens: 1-hour access, 7-day refresh with rotation
- API pagination: 50 items per page
- Rate limiting: 1000/hour for authenticated users

### Frontend Structure

**Component-based React architecture:**

```
frontend/src/
├── components/          # Reusable components
│   ├── ui/             # shadcn/ui base components
│   ├── auth/           # ProtectedRoute, auth components
│   ├── layout/         # Header, Sidebar
│   ├── dashboard/      # Dashboard-specific components
│   ├── employees/      # Employee management UI
│   ├── vacation/       # Vacation management UI
│   └── notifications/  # Notification components
├── contexts/           # React contexts (AuthContext)
├── hooks/              # Custom hooks
├── pages/              # Page components (LoginPage, DashboardPage)
├── services/           # API integration
│   ├── api.ts          # Axios instance with JWT interceptor
│   └── auth.service.ts # Auth API calls
├── types/              # TypeScript type definitions
├── lib/                # Utilities
└── config/             # App configuration
```

**API Integration:**
- Axios instance at `services/api.ts` handles JWT token attachment
- Automatic token refresh on 401 responses
- All API calls proxy to `http://localhost:8000/api` via Vite config
- Base URL: `VITE_API_URL=http://localhost:8000/api` (in frontend/.env)

**Authentication Flow:**
1. User logs in → receives access + refresh tokens
2. Tokens stored in localStorage
3. Access token auto-attached to requests
4. On 401 → auto-refresh token → retry request
5. If refresh fails → redirect to login

## Data Model Key Concepts

### User Model is Employee Model
The `User` model (`apps/accounts/models.py`) serves dual purpose:
- Authentication (extends Django's `AbstractUser`)
- Employee profile (includes all employee fields)

**User Fields:**
- Authentication: `email` (unique, login), `password`, `username`
- Role: `role` (EMPLOYEE, MANAGER, ADMIN)
- Employee: `employee_id`, `date_of_birth`, `hire_date`, `employment_status`
- HR: `salary`, `employment_type`, `department`, `job_title`
- Location: `primary_location` (ForeignKey)
- Vacation: `annual_vacation_days`, `remaining_vacation_days`

### Soft Delete Pattern
All models inheriting from `BaseModel` support soft delete:
```python
# Soft delete (sets is_deleted=True)
obj.soft_delete(user=request.user)

# Restore
obj.restore()

# Query only active objects (default)
Model.objects.all()

# Include deleted objects
Model.all_objects.all()
```

### Audit Trail
`BaseModel` automatically tracks:
- `created_by`, `updated_by` (User ForeignKeys)
- `created_at`, `updated_at` (timestamps)
- `deleted_by`, `deleted_at` (for soft deletes)

## API Patterns

### URL Structure
All API endpoints are under `/api/`:
```
/api/auth/login/                    # POST - Login
/api/auth/refresh/                  # POST - Refresh token
/api/auth/logout/                   # POST - Logout
/api/users/                         # GET (list), POST (create)
/api/users/{id}/                    # GET, PUT, PATCH, DELETE
/api/users/me/                      # GET - Current user profile
/api/locations/                     # CRUD for locations
/api/vacation/requests/             # CRUD for vacation requests
/api/vacation/requests/{id}/approve/ # POST - Approve request
/api/vacation/holidays/             # CRUD for public holidays
/api/notifications/                 # List/mark read notifications
/api/dashboard/stats/               # GET - Dashboard statistics
```

### Authentication
- All endpoints require JWT token except `/api/auth/login/` and `/api/health/`
- Header format: `Authorization: Bearer <access_token>`
- Custom permission classes check user roles (EMPLOYEE, MANAGER, ADMIN)

### Testing
- Use pytest for backend tests
- Test files in `tests/` directory
- Factory Boy for test data generation
- Run single test: `pytest tests/test_specific.py::test_function_name`
- Coverage reports: `pytest --cov=apps --cov-report=html`

## Docker Services

The `docker-compose.yml` defines 5 services:
- **db**: PostgreSQL 15 on port 5433 (maps to 5432 internally)
- **redis**: Redis 7 on port 6380 (maps to 6379 internally)
- **web**: Django app on port 8000
- **celery**: Background task worker
- **celery-beat**: Scheduled task scheduler

**Database Connection:**
- Docker: `DB_HOST=db`, `DB_PORT=5432`
- Local: `DB_HOST=localhost`, `DB_PORT=5433`

## Environment Configuration

**Backend (.env in root):**
```
DJANGO_ENV=development
SECRET_KEY=<secret>
DB_NAME=careplan
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db  # or localhost for local dev
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
```

**Frontend (frontend/.env):**
```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=CarePlan
```

## Common Development Tasks

### Adding a New Django App
1. Create app: `python manage.py startapp <app_name> apps/<app_name>`
2. Add to `LOCAL_APPS` in `config/settings/base.py`
3. Create models inheriting from `BaseModel`
4. Create API ViewSet in `apps/api/views/<domain>.py`
5. Register routes in `apps/api/urls.py`
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Adding Frontend Components
1. Use shadcn/ui for base components: `npx shadcn-ui@latest add <component>`
2. Create feature components in `components/<feature>/`
3. Define TypeScript types in `types/index.ts`
4. Create API service functions in `services/`
5. Use TanStack Query for data fetching

### API Endpoint Development
1. Define serializers in app's `serializers.py`
2. Create ViewSet in `apps/api/views/`
3. Register in router or add path in `apps/api/urls.py`
4. Use DRF permissions: `IsAuthenticated`, custom role-based permissions
5. Apply filters via `django_filters` and `SearchFilter`

## Performance Optimization

The system is designed for 100+ concurrent users:
- Database connection pooling enabled (CONN_MAX_AGE=600)
- Redis caching for sessions and expensive queries
- Celery for async tasks (email notifications, reports)
- Query optimization with `select_related()` and `prefetch_related()`
- API pagination (50 items/page)
- Rate limiting (1000 requests/hour per user)

## Celery Tasks

Background tasks handled by Celery:
- Email notifications for vacation approvals
- Scheduled tasks via celery-beat
- Configuration in `config/celery.py`
- Tasks defined in each app's `tasks.py`

## Code Quality Standards

**Backend:**
- Format with Black (line length 100)
- Sort imports with isort
- Lint with flake8 and pylint
- Type hints encouraged
- Docstrings for complex functions

**Frontend:**
- ESLint with TypeScript rules
- Functional components with hooks
- TypeScript strict mode
- Tailwind for styling (no inline styles)
