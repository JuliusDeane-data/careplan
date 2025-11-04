# Frontend Implementation Plan - Careplan

**Date Created**: 2025-11-04
**Status**: Planning Phase
**Priority**: High - Get visible UI

---

## 🎯 Overview

Build a modern, responsive frontend for the Careplan care facility management system. The backend is ready with Django + DRF + JWT authentication. Now we need a user-friendly interface for employees and managers.

---

## 📋 What We Have (Backend Ready)

✅ **Django Backend**:
- User/Employee management (merged model)
- Locations with manager assignments
- Qualifications tracking
- Employee documents
- Vacation request system with approval workflow
- Notifications system
- Public holidays management

✅ **REST Framework Setup**:
- JWT authentication configured
- CORS enabled (localhost:3000 allowed)
- Pagination (50 items per page)
- Filtering, search, ordering
- Rate limiting
- Exception handling

✅ **Infrastructure**:
- Docker Compose (web, db, redis, celery, celery-beat)
- PostgreSQL database
- Redis caching
- Celery for background tasks

---

## 🎨 Frontend Options

### Option 1: React + Vite (Recommended)
**Best for**: Modern, fast development with great DX

**Tech Stack**:
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite (super fast, better than CRA)
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: TanStack Query (React Query) for server state
- **Forms**: React Hook Form + Zod validation
- **Routing**: React Router v6
- **API Client**: Axios with interceptors
- **Auth**: JWT token management
- **Icons**: Lucide React
- **Date Handling**: date-fns
- **Charts**: Recharts (for dashboards)

**Pros**:
- Fast development with Vite hot reload
- TypeScript for type safety
- shadcn/ui for beautiful, customizable components
- React Query handles caching, refetching, optimistic updates
- Huge ecosystem and community

**Cons**:
- Need to set up build tooling
- More initial setup

### Option 2: Next.js 14 (App Router)
**Best for**: Full-stack capabilities, SEO, server-side rendering

**Tech Stack**:
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: TanStack Query
- **Forms**: React Hook Form + Zod
- **API**: API routes for BFF (Backend for Frontend)
- **Auth**: NextAuth.js or custom JWT

**Pros**:
- Server components for better performance
- Built-in routing
- API routes can act as BFF layer
- Great developer experience
- SEO-friendly (if needed)

**Cons**:
- Overkill if you don't need SSR/SSG
- Slightly more complex

### Option 3: Vue 3 + Vite
**Best for**: If you prefer Vue over React

**Tech Stack**:
- **Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Headless UI
- **State Management**: Pinia + TanStack Query (Vue Query)
- **Forms**: VeeValidate + Yup
- **Routing**: Vue Router
- **UI Components**: PrimeVue or Naive UI

**Pros**:
- Simpler learning curve
- Great documentation
- Good TypeScript support
- Fast with Vite

**Cons**:
- Smaller ecosystem than React
- Fewer UI component libraries

### Option 4: Django Templates + HTMX (Simplest)
**Best for**: Quick MVP, server-side rendering, no separate frontend

**Tech Stack**:
- **Templates**: Django Templates
- **Interactivity**: HTMX + Alpine.js
- **Styling**: Tailwind CSS
- **Forms**: Django Forms
- **Auth**: Django sessions (already built-in)

**Pros**:
- No separate frontend project
- Use Django's built-in features
- Faster initial development
- No API needed (direct template rendering)
- Great for teams familiar with Django

**Cons**:
- Less interactive than SPA
- Limited for complex UIs
- Harder to scale to mobile apps later

---

## 🏆 Recommended Approach: React + Vite + shadcn/ui

**Why?**
1. **Modern & Fast**: Vite provides instant HMR and fast builds
2. **Beautiful UI**: shadcn/ui gives you gorgeous, customizable components
3. **Type Safety**: TypeScript catches bugs early
4. **Great DX**: React DevTools, TanStack Query DevTools
5. **Scalable**: Easy to add mobile app later (React Native)
6. **Industry Standard**: Most jobs, most tutorials, best ecosystem

---

## 📁 Project Structure (React + Vite)

```
careplan/
├── backend/                    # Current Django project
│   ├── apps/
│   ├── config/
│   ├── manage.py
│   └── ...
│
├── frontend/                   # New React project
│   ├── public/
│   │   └── vite.svg
│   │
│   ├── src/
│   │   ├── api/               # API client and endpoints
│   │   │   ├── client.ts      # Axios instance with interceptors
│   │   │   ├── auth.ts        # Auth API calls
│   │   │   ├── users.ts       # User API calls
│   │   │   ├── locations.ts   # Location API calls
│   │   │   ├── vacation.ts    # Vacation API calls
│   │   │   └── notifications.ts
│   │   │
│   │   ├── components/        # Reusable components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── layout/        # Layout components
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── DashboardLayout.tsx
│   │   │   │
│   │   │   ├── auth/          # Auth components
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── ProtectedRoute.tsx
│   │   │   │   └── PasswordResetForm.tsx
│   │   │   │
│   │   │   └── common/        # Common components
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       ├── EmptyState.tsx
│   │   │       └── DataTable.tsx
│   │   │
│   │   ├── features/          # Feature-based modules
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   └── DashboardStats.tsx
│   │   │   │
│   │   │   ├── employees/
│   │   │   │   ├── EmployeeList.tsx
│   │   │   │   ├── EmployeeDetail.tsx
│   │   │   │   ├── EmployeeForm.tsx
│   │   │   │   └── EmployeeCard.tsx
│   │   │   │
│   │   │   ├── locations/
│   │   │   │   ├── LocationList.tsx
│   │   │   │   ├── LocationDetail.tsx
│   │   │   │   └── LocationForm.tsx
│   │   │   │
│   │   │   ├── vacation/
│   │   │   │   ├── VacationList.tsx
│   │   │   │   ├── VacationRequestForm.tsx
│   │   │   │   ├── VacationCalendar.tsx
│   │   │   │   ├── VacationApproval.tsx
│   │   │   │   └── VacationBalance.tsx
│   │   │   │
│   │   │   └── notifications/
│   │   │       ├── NotificationList.tsx
│   │   │       ├── NotificationBell.tsx
│   │   │       └── NotificationItem.tsx
│   │   │
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useVacation.ts
│   │   │   ├── useNotifications.ts
│   │   │   └── useLocalStorage.ts
│   │   │
│   │   ├── lib/               # Utilities and helpers
│   │   │   ├── utils.ts       # Utility functions
│   │   │   ├── cn.ts          # Class name utility
│   │   │   └── date-utils.ts  # Date formatting
│   │   │
│   │   ├── types/             # TypeScript types
│   │   │   ├── auth.ts
│   │   │   ├── user.ts
│   │   │   ├── location.ts
│   │   │   ├── vacation.ts
│   │   │   └── notification.ts
│   │   │
│   │   ├── store/             # Global state (if needed)
│   │   │   └── authStore.ts   # Zustand for auth state
│   │   │
│   │   ├── routes/            # Route definitions
│   │   │   └── index.tsx
│   │   │
│   │   ├── App.tsx            # Main app component
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles
│   │
│   ├── .env.development       # Environment variables
│   ├── .env.production
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── components.json        # shadcn/ui config
│   └── README.md
│
├── docker-compose.yml         # Update to include frontend
└── README.md
```

---

## 🚀 Implementation Plan

### Phase 1: Setup & Authentication (2-3 hours)

#### 1.1 Create React Project
```bash
cd /home/philip/projects/careplan
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

#### 1.2 Install Core Dependencies
```bash
# UI & Styling
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install class-variance-authority clsx tailwind-merge
npm install lucide-react

# Routing
npm install react-router-dom

# Forms & Validation
npm install react-hook-form zod @hookform/resolvers

# API & State Management
npm install axios @tanstack/react-query

# Date Handling
npm install date-fns

# Dev Dependencies
npm install -D @types/node
```

#### 1.3 Setup shadcn/ui
```bash
npx shadcn-ui@latest init
```

Install commonly used components:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add form
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add table
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add toast
npx shadchn-ui@latest add calendar
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
```

#### 1.4 Configure Tailwind
Update `tailwind.config.js` with careplan theme colors.

#### 1.5 Setup API Client
- Create Axios instance with base URL
- Add JWT token interceptor
- Add error handling interceptor
- Add response transformation

#### 1.6 Implement Authentication
- Login page with form
- JWT token storage (localStorage + httpOnly cookie for refresh)
- Protected route wrapper
- Auto token refresh
- Logout functionality

**Deliverables**:
- ✅ React project initialized
- ✅ Dependencies installed
- ✅ shadcn/ui configured
- ✅ API client ready
- ✅ Login/logout working

---

### Phase 2: Dashboard & Layout (2-3 hours)

#### 2.1 Create Layout Components
- `DashboardLayout`: Main layout with sidebar and navbar
- `Navbar`: Top navigation with user menu, notifications
- `Sidebar`: Navigation links (Dashboard, Employees, Locations, Vacation, etc.)
- `Footer`: Copyright and version info

#### 2.2 Build Dashboard Page
- Welcome message with user's name
- Stats cards:
  - Total employees
  - Active locations
  - Pending vacation requests (for managers)
  - Vacation balance (for employees)
- Recent activity feed
- Quick actions buttons

#### 2.3 Implement Routing
- Route structure with React Router
- Protected routes (requires auth)
- Role-based routes (admin vs employee)
- 404 page

**Deliverables**:
- ✅ Beautiful dashboard layout
- ✅ Navigation working
- ✅ Dashboard with stats
- ✅ Responsive design

---

### Phase 3: Employee Management (3-4 hours)

#### 3.1 Employee List Page
- Data table with search and filters
- Columns: Name, Email, Role, Location, Status, Actions
- Pagination
- Sort by columns
- Filter by location, role, status

#### 3.2 Employee Detail Page
- Employee information card
- Vacation balance
- Documents list with upload
- Qualifications
- Assigned locations

#### 3.3 Employee Form (Create/Edit)
- Form validation with Zod
- Fields: Personal info, contact, employment details
- Location assignment (primary + additional)
- Qualification selection
- Document upload

**Deliverables**:
- ✅ Employee list with search/filter
- ✅ Employee detail view
- ✅ Create/edit employee form
- ✅ CRUD operations working

---

### Phase 4: Vacation Management (3-4 hours)

#### 4.1 Vacation Request Form
- Date range picker
- Request type selection
- Reason textarea
- Auto-calculate vacation days
- Show remaining balance
- Validation (no overlapping, sufficient balance)

#### 4.2 My Vacation Requests (Employee View)
- List of own requests
- Status badges (Pending, Approved, Denied, Cancelled)
- Filter by status, date range
- Cancel pending/approved requests

#### 4.3 Vacation Approvals (Manager View)
- List of pending requests for team
- Approve/deny with reason
- Bulk actions
- Calendar view of team vacations

#### 4.4 Vacation Calendar
- Monthly calendar view
- Show all team members' vacations
- Color-coded by status
- Hover tooltip with details

#### 4.5 Vacation Balance Card
- Current balance
- Used days
- Pending requests
- Available days
- Visual progress bar

**Deliverables**:
- ✅ Request vacation form
- ✅ View own requests
- ✅ Manager approval interface
- ✅ Team calendar view
- ✅ Balance tracking

---

### Phase 5: Notifications (2 hours)

#### 5.1 Notification Bell Icon
- Badge with unread count
- Dropdown with recent notifications
- Mark as read on click
- Link to full notification page

#### 5.2 Notification Page
- List of all notifications
- Filter by read/unread, type
- Mark all as read button
- Delete notifications
- Real-time updates (polling or WebSocket)

**Deliverables**:
- ✅ Notification bell in navbar
- ✅ Notification list page
- ✅ Mark as read functionality

---

### Phase 6: Locations & Settings (2-3 hours)

#### 6.1 Location List
- Card grid or table view
- Location details (name, address, manager)
- Employee count per location

#### 6.2 Location Detail
- Location info
- Manager assignment
- Employees at this location
- Location-specific holidays

#### 6.3 User Settings
- Profile page
- Change password
- Notification preferences
- Theme toggle (dark mode)

**Deliverables**:
- ✅ Location management
- ✅ User profile settings
- ✅ Dark mode support

---

### Phase 7: Polish & Production (2-3 hours)

#### 7.1 Error Handling
- Error boundary component
- Toast notifications for errors/success
- Form validation errors
- API error messages

#### 7.2 Loading States
- Skeleton loaders
- Loading spinners
- Optimistic UI updates

#### 7.3 Responsive Design
- Mobile-friendly navigation (hamburger menu)
- Responsive tables (horizontal scroll or card view)
- Touch-friendly buttons

#### 7.4 Performance
- Code splitting
- Lazy loading routes
- Image optimization
- Query caching

#### 7.5 Testing & Documentation
- Component tests (optional)
- E2E tests (optional)
- README with setup instructions
- Environment variables documentation

**Deliverables**:
- ✅ Production-ready frontend
- ✅ Mobile responsive
- ✅ Error handling
- ✅ Good UX

---

## 🎨 Design System

### Colors (Tailwind)
```javascript
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#3b82f6',  // Blue
    600: '#2563eb',
  },
  success: {
    500: '#10b981',  // Green
  },
  warning: {
    500: '#f59e0b',  // Orange
  },
  danger: {
    500: '#ef4444',  // Red
  },
}
```

### Typography
- **Headings**: Inter or Geist Sans
- **Body**: Inter
- **Code**: JetBrains Mono

### Spacing
- Use Tailwind's default spacing scale
- Consistent padding/margin across components

---

## 🔐 Authentication Flow

### Login Flow
1. User enters email + password
2. Frontend sends `POST /api/auth/login/` (need to create this endpoint)
3. Backend validates credentials
4. Returns JWT access token + refresh token
5. Frontend stores tokens:
   - Access token: memory (React state) + localStorage (for persistence)
   - Refresh token: httpOnly cookie (more secure)
6. Redirect to dashboard

### Protected Routes
1. Check if access token exists
2. If no token: redirect to login
3. If token expired: try refresh
4. If refresh fails: redirect to login

### Auto Token Refresh
- Before API call, check token expiry
- If < 5 minutes: refresh token
- Use interceptor for automatic refresh

---

## 🗂️ API Endpoints (Backend TODO)

You'll need to create these REST API endpoints:

### Auth Endpoints
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout (blacklist token)
- `POST /api/auth/password-reset/` - Request password reset
- `POST /api/auth/password-reset-confirm/` - Confirm password reset

### User Endpoints
- `GET /api/users/me/` - Current user profile
- `PUT /api/users/me/` - Update profile
- `POST /api/users/me/change-password/` - Change password
- `GET /api/users/` - List users (admin/manager only)
- `GET /api/users/{id}/` - User detail
- `PUT /api/users/{id}/` - Update user
- `GET /api/users/{id}/vacation-balance/` - Vacation balance

### Location Endpoints
- `GET /api/locations/` - List locations
- `GET /api/locations/{id}/` - Location detail
- `GET /api/locations/{id}/employees/` - Employees at location

### Vacation Endpoints
- `GET /api/vacation/requests/` - List all vacation requests (filtered by role)
- `POST /api/vacation/requests/` - Create vacation request
- `GET /api/vacation/requests/{id}/` - Vacation request detail
- `PUT /api/vacation/requests/{id}/` - Update vacation request
- `DELETE /api/vacation/requests/{id}/` - Delete/cancel vacation request
- `POST /api/vacation/requests/{id}/approve/` - Approve vacation request
- `POST /api/vacation/requests/{id}/deny/` - Deny vacation request
- `POST /api/vacation/requests/{id}/cancel/` - Cancel vacation request
- `GET /api/vacation/my-requests/` - Current user's vacation requests
- `GET /api/vacation/calendar/` - Team vacation calendar
- `GET /api/vacation/balance/` - Current user's vacation balance

### Notification Endpoints
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread/` - Unread notifications
- `PUT /api/notifications/{id}/mark-read/` - Mark as read
- `POST /api/notifications/mark-all-read/` - Mark all as read
- `DELETE /api/notifications/{id}/` - Delete notification

### Public Holiday Endpoints
- `GET /api/holidays/` - List public holidays
- `GET /api/holidays/?location={id}&year={year}` - Filter holidays

---

## 🐳 Docker Integration

Update `docker-compose.yml` to include frontend:

```yaml
services:
  # ... existing services (web, db, redis, celery, celery-beat)

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: careplan_frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - web
    command: npm run dev -- --host
```

Create `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
```

---

## 📦 Environment Variables

### Frontend `.env.development`
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Careplan
```

### Frontend `.env.production`
```env
VITE_API_URL=https://api.careplan.com
VITE_APP_NAME=Careplan
```

---

## 🎯 Success Metrics

### Phase 1 Complete:
- ✅ Can login and logout
- ✅ Tokens stored and refreshed
- ✅ Protected routes working

### Phase 2 Complete:
- ✅ Dashboard shows stats
- ✅ Navigation works
- ✅ Responsive layout

### Phase 3 Complete:
- ✅ Can view employee list
- ✅ Can create/edit employees
- ✅ CRUD operations work

### Phase 4 Complete:
- ✅ Can request vacation
- ✅ Managers can approve/deny
- ✅ Calendar view shows team vacations
- ✅ Balance updates correctly

### Phase 5 Complete:
- ✅ Notifications appear in real-time
- ✅ Can mark as read
- ✅ Badge shows unread count

### Phase 6 Complete:
- ✅ Location management works
- ✅ User settings functional
- ✅ Dark mode working

### Phase 7 Complete:
- ✅ Production-ready
- ✅ No critical bugs
- ✅ Good performance
- ✅ Mobile responsive

---

## 🔄 Alternative: Quick Start with Django Templates + HTMX

If you want to see something **immediately** without setting up React:

### 1. Install HTMX & Alpine.js
Add to `base.html`:
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://unpkg.com/alpinejs@3.13.5/dist/cdn.min.js"></script>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3/dist/tailwind.min.css" rel="stylesheet">
```

### 2. Create Base Template
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Careplan{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://unpkg.com/alpinejs@3.13.5/dist/cdn.min.js"></script>
</head>
<body class="bg-gray-50">
    {% include 'partials/navbar.html' %}

    <div class="flex">
        {% include 'partials/sidebar.html' %}

        <main class="flex-1 p-6">
            {% block content %}{% endblock %}
        </main>
    </div>
</body>
</html>
```

### 3. Create Dashboard View
```python
# apps/dashboard/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    context = {
        'total_employees': User.objects.filter(is_active=True).count(),
        'total_locations': Location.objects.filter(is_active=True).count(),
        'pending_requests': VacationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'dashboard/index.html', context)
```

### Pros:
- See results in 30 minutes
- No separate frontend build
- Use Django's auth (no JWT complexity)

### Cons:
- Less interactive
- Harder to scale later

---

## 💡 Recommendation

**For a production-quality app**: Go with **React + Vite + shadcn/ui**

**For a quick MVP to show stakeholders**: Start with **Django Templates + HTMX**, then migrate to React later

**What I suggest**: Let's build the React frontend! It will take a bit longer initially, but you'll have a modern, scalable, beautiful application that's easy to maintain and extend.

---

## 📅 Timeline

### If React + Vite:
- **Week 1**: Setup + Auth + Dashboard (6-8 hours)
- **Week 2**: Employee Management + Vacation (6-8 hours)
- **Week 3**: Notifications + Polish (4-6 hours)
- **Total**: ~20 hours of focused work

### If Django Templates + HTMX:
- **Day 1-2**: Basic templates + dashboard (4-6 hours)
- **Day 3-4**: Vacation management (4-6 hours)
- **Day 5**: Polish (2-3 hours)
- **Total**: ~12 hours

---

## ❓ Next Decision

**What would you like to do?**

1. **Go with React + Vite** (modern, scalable, beautiful)
2. **Go with Django Templates + HTMX** (quick, simple, server-rendered)
3. **Something else** (Vue, Next.js, etc.)

I recommend **Option 1 (React + Vite)** for the best long-term results.

Let me know your preference, and I'll start building! 🚀
