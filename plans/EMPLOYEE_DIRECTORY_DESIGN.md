# Employee Directory - Architectural Design Document

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
7. [State Management](#state-management)
8. [User Flows](#user-flows)
9. [UI/UX Specifications](#ui-ux-specifications)
10. [Security Considerations](#security-considerations)
11. [Performance Optimization](#performance-optimization)
12. [Implementation Plan](#implementation-plan)
13. [Testing Strategy](#testing-strategy)

---

## Executive Summary

The Employee Directory is a comprehensive employee management interface that allows users to browse, search, and view employee profiles. It provides role-based functionality with admin users having additional capabilities for CRUD operations.

### Key Features
- **Employee Listing:** Paginated, searchable list of all employees
- **Advanced Search:** Filter by name, role, location, employment status
- **Employee Profiles:** Detailed view of employee information
- **Admin CRUD:** Create, update, delete employees (admin only)
- **Responsive Design:** Mobile-first, accessible interface
- **Real-time Data:** Live updates using React Query

### Success Criteria
- Load employee list in <500ms
- Support 100+ employees with smooth pagination
- Mobile responsive (works on 320px+ viewports)
- WCAG 2.1 AA accessibility compliance
- <2 second page transitions

---

## Business Requirements

### Functional Requirements

#### FR-1: Employee Listing
- Display paginated list of employees (20 per page)
- Show employee card with photo, name, role, location
- Sort by: name, role, hire date, location
- Default sort: name (A-Z)

#### FR-2: Search & Filtering
- Search by: name, email, employee ID
- Filter by:
  - Role (Care Worker, Nurse, Manager, Admin)
  - Location (multi-select)
  - Employment Status (Active, On Leave, Terminated)
  - Department
- Real-time search (debounced)
- Clear filters button
- Show result count

#### FR-3: Employee Profile View
- Display comprehensive employee information:
  - Personal: name, email, phone, address
  - Employment: role, department, hire date, status
  - Location: primary location, secondary locations
  - Vacation: current balance, upcoming vacations
  - Qualifications: certifications, skills
  - Manager: reporting relationship
- Edit button (admin/manager only)
- Back to list navigation

#### FR-4: Employee CRUD (Admin Only)
- **Create:** Add new employee with all required fields
- **Update:** Edit existing employee information
- **Delete:** Soft delete with confirmation
- **Bulk Actions:** Archive, export selected employees
- Validation for all fields
- Duplicate detection (email, employee ID)

### Non-Functional Requirements

#### NFR-1: Performance
- Initial load: <1 second
- Search response: <300ms
- Pagination: <200ms
- Profile load: <500ms
- Support 500+ employees

#### NFR-2: Usability
- Intuitive navigation
- Clear visual hierarchy
- Responsive design (320px - 4K)
- Keyboard navigation support
- Screen reader compatible

#### NFR-3: Security
- Role-based access control
- Data encryption in transit
- No sensitive data in URLs
- CSRF protection
- Input sanitization

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │ Employee List │  │ Employee      │  │ Employee Form  │  │
│  │ Page          │  │ Detail Page   │  │ (Admin)        │  │
│  └───────┬───────┘  └───────┬───────┘  └───────┬────────┘  │
└──────────┼──────────────────┼──────────────────┼────────────┘
           │                  │                  │
┌──────────┼──────────────────┼──────────────────┼────────────┐
│          │        Business Logic Layer         │            │
│  ┌───────▼───────┐  ┌───────▼───────┐  ┌─────▼──────┐    │
│  │ useEmployees  │  │ useEmployee   │  │ useEmployee │    │
│  │ (list/search) │  │ (single)      │  │ Mutations   │    │
│  └───────┬───────┘  └───────┬───────┘  └─────┬──────┘    │
└──────────┼──────────────────┼──────────────────┼────────────┘
           │                  │                  │
┌──────────┼──────────────────┼──────────────────┼────────────┐
│          │           Data Layer                │            │
│  ┌───────▼──────────────────▼──────────────────▼────────┐  │
│  │          employeeService (API Client)                 │  │
│  │  - getEmployees()    - getEmployee()                  │  │
│  │  - createEmployee()  - updateEmployee()               │  │
│  │  - deleteEmployee()  - searchEmployees()              │  │
│  └────────────────────────────┬──────────────────────────┘  │
└───────────────────────────────┼─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                     Backend API Layer                        │
│  /api/employees/              - List/Create                  │
│  /api/employees/{id}/         - Get/Update/Delete            │
│  /api/employees/search/       - Search                       │
│  /api/employees/{id}/profile/ - Detailed profile             │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 19 with TypeScript
- React Router for navigation
- React Query for data fetching
- React Hook Form + Zod for forms
- Tailwind CSS + shadcn/ui for styling
- Sonner for notifications

**State Management:**
- React Query for server state
- React Hook Form for form state
- URL params for filters/pagination
- Context API for global UI state (if needed)

---

## Component Design

### Component Hierarchy

```
pages/employees/
├── EmployeeListPage.tsx           (Main list view)
│   ├── EmployeeFilters             (Search & filter bar)
│   ├── EmployeeGrid                (Grid/List view toggle)
│   │   └── EmployeeCard            (Individual employee card)
│   ├── EmployeeTable               (Table view option)
│   │   └── EmployeeRow             (Table row)
│   └── Pagination                  (Page controls)
├── EmployeeDetailPage.tsx         (Profile view)
│   ├── EmployeeHeader              (Name, photo, status)
│   ├── EmployeeInfoCard            (Personal info)
│   ├── EmployeeEmploymentCard      (Job info)
│   ├── EmployeeLocationsCard       (Locations)
│   ├── EmployeeVacationCard        (Vacation balance)
│   └── EmployeeQualificationsCard  (Certs, skills)
└── EmployeeFormPage.tsx           (Create/Edit - Admin)
    ├── EmployeeFormPersonal        (Personal info section)
    ├── EmployeeFormEmployment      (Employment section)
    ├── EmployeeFormLocations       (Location assignment)
    └── EmployeeFormQualifications  (Skills/certs)

components/employees/
├── EmployeeCard.tsx               (Card display)
├── EmployeeFilters.tsx            (Filter controls)
├── EmployeeSearchBar.tsx          (Search input)
├── EmployeeStatusBadge.tsx        (Status indicator)
├── EmployeeAvatar.tsx             (Profile photo)
└── EmployeeQuickActions.tsx       (Action menu)
```

### Component Specifications

#### EmployeeListPage

**Purpose:** Main employee directory landing page

**Props:** None (uses URL params)

**State:**
```typescript
- currentPage: number
- pageSize: number (20)
- sortBy: string ('name' | 'role' | 'hireDate' | 'location')
- sortOrder: 'asc' | 'desc'
- filters: EmployeeFilters
- viewMode: 'grid' | 'table'
```

**Features:**
- Pagination controls
- View mode toggle (grid/table)
- Bulk actions (admin only)
- Export to CSV
- Keyboard shortcuts (/, Ctrl+K for search)

---

#### EmployeeCard

**Purpose:** Display employee summary in grid view

**Props:**
```typescript
interface EmployeeCardProps {
  employee: EmployeeSummary
  onSelect?: (id: number) => void
  isSelected?: boolean
  showActions?: boolean
}
```

**Layout:**
```
┌─────────────────────────────────────┐
│  ┌────┐  John Smith                 │
│  │IMG │  Care Worker                │
│  │    │  Downtown Center            │
│  └────┘  ✓ Active                   │
│                                      │
│  📧 john.smith@careplan.com         │
│  📞 (555) 123-4567                  │
│                                      │
│  Hired: Jan 15, 2024                │
│  [View Profile] [...More]           │
└─────────────────────────────────────┘
```

---

#### EmployeeFilters

**Purpose:** Filter and search controls

**Props:**
```typescript
interface EmployeeFiltersProps {
  filters: EmployeeFilters
  onFilterChange: (filters: EmployeeFilters) => void
  onClear: () => void
  resultCount?: number
}
```

**Features:**
- Real-time search (300ms debounce)
- Multi-select location filter
- Role dropdown
- Status toggle
- Active filter count badge
- Clear all button

---

#### EmployeeDetailPage

**Purpose:** Comprehensive employee profile view

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  [← Back to List]           [Edit] [More ▼]             │
├─────────────────────────────────────────────────────────┤
│  ┌────────┐                                             │
│  │        │  John Smith                                 │
│  │  IMG   │  Care Worker                                │
│  │        │  ✓ Active  •  ID: EMP-1234                 │
│  └────────┘                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Personal Info   │  │ Employment      │              │
│  │ • Email         │  │ • Role          │              │
│  │ • Phone         │  │ • Department    │              │
│  │ • Address       │  │ • Hire Date     │              │
│  └─────────────────┘  └─────────────────┘              │
│                                                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Locations       │  │ Vacation        │              │
│  │ • Primary       │  │ • Balance: 15   │              │
│  │ • Secondary     │  │ • Upcoming: 2   │              │
│  └─────────────────┘  └─────────────────┘              │
│                                                          │
│  ┌──────────────────────────────────────┐              │
│  │ Qualifications                        │              │
│  │ [Cert1] [Cert2] [Skill1] [Skill2]   │              │
│  └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## Data Models

### TypeScript Interfaces

```typescript
// Employee Summary (for list view)
export interface EmployeeSummary {
  id: number
  employee_id: string // EMP-1234
  full_name: string
  email: string
  phone?: string
  role: EmployeeRole
  employment_status: EmploymentStatus
  primary_location: LocationSummary
  profile_photo?: string
  hire_date: string
}

// Full Employee Profile
export interface Employee extends EmployeeSummary {
  first_name: string
  last_name: string
  middle_name?: string
  date_of_birth?: string
  gender?: 'M' | 'F' | 'O' | 'N'
  address?: Address

  // Employment
  department?: string
  job_title?: string
  manager?: EmployeeSummary
  hourly_rate?: number
  salary?: number

  // Locations
  secondary_locations: LocationSummary[]

  // Vacation
  annual_vacation_days: number
  remaining_vacation_days: number
  sick_days_remaining: number

  // Qualifications
  qualifications: Qualification[]
  skills: string[]

  // Metadata
  created_at: string
  updated_at: string
  last_login?: string
}

// Employee Role
export type EmployeeRole =
  | 'CARE_WORKER'
  | 'NURSE'
  | 'MANAGER'
  | 'ADMIN'
  | 'COORDINATOR'

// Employment Status
export type EmploymentStatus =
  | 'ACTIVE'
  | 'ON_LEAVE'
  | 'TERMINATED'
  | 'PROBATION'

// Location Summary
export interface LocationSummary {
  id: number
  name: string
  address: string
  type: string
}

// Address
export interface Address {
  street1: string
  street2?: string
  city: string
  state: string
  postal_code: string
  country: string
}

// Qualification
export interface Qualification {
  id: number
  name: string
  issuing_organization: string
  issue_date: string
  expiry_date?: string
  is_active: boolean
}

// Employee Filters
export interface EmployeeFilters {
  search?: string
  role?: EmployeeRole[]
  location?: number[]
  employment_status?: EmploymentStatus[]
  department?: string[]
  page?: number
  page_size?: number
  ordering?: string
}

// Employee Create/Update
export interface EmployeeCreate {
  first_name: string
  last_name: string
  middle_name?: string
  email: string
  phone?: string
  role: EmployeeRole
  employment_status: EmploymentStatus
  primary_location: number
  secondary_locations?: number[]
  hire_date: string
  date_of_birth?: string
  address?: Address
  department?: string
  job_title?: string
  manager_id?: number
  annual_vacation_days?: number
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {
  id: number
}
```

---

## API Integration

### Service Layer

```typescript
// src/services/employee.service.ts

import api from './api'
import type {
  Employee,
  EmployeeSummary,
  EmployeeFilters,
  EmployeeCreate,
  EmployeeUpdate,
} from '@/types/employee'

export const employeeService = {
  /**
   * Get paginated list of employees with optional filters
   */
  async getEmployees(filters?: EmployeeFilters) {
    const response = await api.get<{
      count: number
      next: string | null
      previous: string | null
      results: EmployeeSummary[]
    }>('/employees/', { params: filters })

    return response.data
  },

  /**
   * Get single employee by ID
   */
  async getEmployee(id: number): Promise<Employee> {
    const response = await api.get<Employee>(`/employees/${id}/`)
    return response.data
  },

  /**
   * Get employee profile (more detailed than basic GET)
   */
  async getEmployeeProfile(id: number): Promise<Employee> {
    const response = await api.get<Employee>(`/employees/${id}/profile/`)
    return response.data
  },

  /**
   * Create new employee (admin only)
   */
  async createEmployee(data: EmployeeCreate): Promise<Employee> {
    const response = await api.post<Employee>('/employees/', data)
    return response.data
  },

  /**
   * Update employee (admin/manager only)
   */
  async updateEmployee(id: number, data: Partial<EmployeeUpdate>): Promise<Employee> {
    const response = await api.patch<Employee>(`/employees/${id}/`, data)
    return response.data
  },

  /**
   * Delete employee (soft delete - admin only)
   */
  async deleteEmployee(id: number): Promise<void> {
    await api.delete(`/employees/${id}/`)
  },

  /**
   * Search employees by query
   */
  async searchEmployees(query: string): Promise<EmployeeSummary[]> {
    const response = await api.get<EmployeeSummary[]>('/employees/search/', {
      params: { q: query },
    })
    return response.data
  },

  /**
   * Export employees to CSV
   */
  async exportEmployees(filters?: EmployeeFilters): Promise<Blob> {
    const response = await api.get('/employees/export/', {
      params: filters,
      responseType: 'blob',
    })
    return response.data
  },
}
```

---

## State Management

### React Query Hooks

```typescript
// src/hooks/useEmployees.ts

import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query'
import { employeeService } from '@/services/employee.service'
import type { EmployeeFilters, EmployeeCreate, EmployeeUpdate } from '@/types/employee'
import { EMPLOYEE_CONFIG } from '@/config/employee.config'

/**
 * Hook to fetch paginated employees with filters
 */
export function useEmployees(filters?: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => employeeService.getEmployees(filters),
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
    placeholderData: (prev) => prev, // Keep previous data while loading
  })
}

/**
 * Hook to fetch single employee
 */
export function useEmployee(id: number | undefined) {
  return useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeeService.getEmployee(id!),
    enabled: !!id,
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to fetch employee profile (detailed)
 */
export function useEmployeeProfile(id: number | undefined) {
  return useQuery({
    queryKey: ['employee-profile', id],
    queryFn: () => employeeService.getEmployeeProfile(id!),
    enabled: !!id,
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
  })
}

/**
 * Hook to create employee
 */
export function useCreateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: EmployeeCreate) => employeeService.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })
}

/**
 * Hook to update employee
 */
export function useUpdateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<EmployeeUpdate> }) =>
      employeeService.updateEmployee(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      queryClient.invalidateQueries({ queryKey: ['employee', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['employee-profile', variables.id] })
    },
  })
}

/**
 * Hook to delete employee
 */
export function useDeleteEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => employeeService.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })
}

/**
 * Hook for employee search with debouncing
 */
export function useEmployeeSearch(query: string, debounceMs: number = 300) {
  const [debouncedQuery, setDebouncedQuery] = useState(query)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), debounceMs)
    return () => clearTimeout(timer)
  }, [query, debounceMs])

  return useQuery({
    queryKey: ['employees-search', debouncedQuery],
    queryFn: () => employeeService.searchEmployees(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: EMPLOYEE_CONFIG.QUERY_STALE_TIME,
  })
}
```

---

## User Flows

### Flow 1: Browse Employees

```
┌─────────────────────────────────────────────────────────┐
│ 1. User navigates to /employees                         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 2. EmployeeListPage loads                               │
│    - Fetch employees (page 1, 20 items)                 │
│    - Show loading skeleton                              │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Display employee grid/table                          │
│    - Employee cards with avatars                        │
│    - Pagination controls                                │
│    - View mode toggle                                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 4. User clicks on employee card                         │
│    - Navigate to /employees/:id                         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 5. EmployeeDetailPage displays profile                  │
│    - Full employee information                          │
│    - Edit button (if authorized)                        │
└─────────────────────────────────────────────────────────┘
```

### Flow 2: Search and Filter

```
1. User types in search box (debounced 300ms)
2. Real-time search executes
3. Results update dynamically
4. User applies filters (role, location, status)
5. Results filter immediately
6. User can clear all filters
7. Results reset to default view
```

### Flow 3: Create Employee (Admin)

```
1. Admin clicks "Add Employee" button
2. Navigate to /employees/new
3. EmployeeFormPage renders with empty form
4. Admin fills required fields:
   - Personal info (name, email, phone)
   - Employment (role, hire date, location)
   - Optional: address, qualifications
5. Form validates on submit
6. API call to create employee
7. Success toast notification
8. Navigate to new employee profile
9. Employee list cache invalidated
```

### Flow 4: Edit Employee (Admin/Manager)

```
1. User views employee profile
2. Clicks "Edit" button (if authorized)
3. Navigate to /employees/:id/edit
4. EmployeeFormPage renders with pre-filled data
5. User modifies fields
6. Form validates on submit
7. API call to update employee
8. Success toast notification
9. Navigate back to profile
10. Cache invalidated for this employee
```

---

## UI/UX Specifications

### Design Principles

1. **Clarity:** Clear information hierarchy
2. **Efficiency:** Minimize clicks to complete tasks
3. **Consistency:** Match existing CarePlan design system
4. **Accessibility:** WCAG 2.1 AA compliant
5. **Responsiveness:** Mobile-first approach

### Color Scheme (from theme.ts)

```typescript
export const EMPLOYEE_STATUS_STYLES = {
  ACTIVE: {
    badge: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    icon: 'text-green-600',
    label: 'Active',
  },
  ON_LEAVE: {
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    icon: 'text-yellow-600',
    label: 'On Leave',
  },
  TERMINATED: {
    badge: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    icon: 'text-red-600',
    label: 'Terminated',
  },
  PROBATION: {
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    icon: 'text-blue-600',
    label: 'Probation',
  },
} as const
```

### Typography

- **Headers:** 2xl font-bold (employee names)
- **Subheaders:** lg font-semibold (section titles)
- **Body:** sm text (content)
- **Labels:** xs text-muted-foreground (metadata)

### Spacing

- **Card Padding:** p-6
- **Section Spacing:** space-y-6
- **Grid Gaps:** gap-4 (mobile), gap-6 (desktop)

---

## Security Considerations

### Authorization Matrix

| Action | Care Worker | Manager | Admin |
|--------|-------------|---------|-------|
| View Employee List | ✓ | ✓ | ✓ |
| View Employee Profile | ✓ | ✓ | ✓ |
| Edit Own Profile | ✓ | ✓ | ✓ |
| Edit Team Member | ✗ | ✓ | ✓ |
| Create Employee | ✗ | ✗ | ✓ |
| Delete Employee | ✗ | ✗ | ✓ |
| View Salary Info | ✗ | Partial | ✓ |
| Export Data | ✗ | ✓ | ✓ |

### Data Protection

- **PII Handling:** Encrypt sensitive data
- **Field-Level Security:** Hide salary from non-admins
- **Audit Logging:** Track all CRUD operations
- **Session Management:** Timeout after 30 min inactivity

---

## Performance Optimization

### Optimization Strategies

1. **Pagination:** Load 20 employees per page
2. **Image Optimization:**
   - Use thumbnails for list view (100x100)
   - Full size for profile (400x400)
   - Lazy load images
   - WebP format with fallback
3. **Data Fetching:**
   - Prefetch next page on hover
   - Cache employee list for 5 minutes
   - Optimistic updates for mutations
4. **Code Splitting:**
   - Lazy load EmployeeFormPage (admin only)
   - Lazy load EmployeeDetailPage
5. **Debouncing:**
   - Search: 300ms
   - Filter changes: 200ms

### Performance Metrics

- **LCP (Largest Contentful Paint):** <2.5s
- **FID (First Input Delay):** <100ms
- **CLS (Cumulative Layout Shift):** <0.1
- **TTI (Time to Interactive):** <3.5s

---

## Implementation Plan

### Phase 1: Foundation (6 hours)

**Tasks:**
1. Create type definitions (employee.ts) - 1h
2. Create employee service (employee.service.ts) - 1h
3. Create React Query hooks (useEmployees.ts) - 1.5h
4. Create configuration (employee.config.ts) - 0.5h
5. Create theme styles (add to theme.ts) - 0.5h
6. Create shared components (EmployeeAvatar, EmployeeStatusBadge) - 1.5h

**Deliverables:**
- Complete type system
- Working API integration
- Reusable hooks
- Base components

### Phase 2: Employee List (4 hours)

**Tasks:**
1. EmployeeListPage component - 1.5h
2. EmployeeCard component - 1h
3. EmployeeFilters component - 1h
4. Pagination component - 0.5h

**Deliverables:**
- Functional employee list
- Working search and filters
- Pagination
- Grid/table view toggle

### Phase 3: Employee Profile (3 hours)

**Tasks:**
1. EmployeeDetailPage layout - 1h
2. Profile information cards - 1.5h
3. Navigation and breadcrumbs - 0.5h

**Deliverables:**
- Complete profile view
- All information sections
- Responsive layout

### Phase 4: CRUD Operations (5 hours)

**Tasks:**
1. EmployeeFormPage structure - 1h
2. Form validation schema - 1h
3. Create/Edit logic - 1.5h
4. Delete confirmation - 0.5h
5. Admin-only guards - 1h

**Deliverables:**
- Complete CRUD functionality
- Form validation
- Authorization checks
- Success/error handling

### Phase 5: Testing & Polish (4 hours)

**Tasks:**
1. Unit tests for components - 1.5h
2. Integration tests - 1h
3. Accessibility audit - 0.5h
4. Performance optimization - 0.5h
5. Bug fixes - 0.5h

**Deliverables:**
- >80% test coverage
- WCAG 2.1 AA compliant
- Performance benchmarks met
- Production-ready code

**Total Estimated Time: 22 hours**

---

## Testing Strategy

### Unit Tests

```typescript
// EmployeeCard.test.tsx
describe('EmployeeCard', () => {
  it('displays employee information correctly', () => {
    const employee = createMockEmployee()
    render(<EmployeeCard employee={employee} />)

    expect(screen.getByText(employee.full_name)).toBeInTheDocument()
    expect(screen.getByText(employee.role)).toBeInTheDocument()
  })

  it('shows status badge with correct color', () => {
    const employee = createMockEmployee({ employment_status: 'ACTIVE' })
    render(<EmployeeCard employee={employee} />)

    const badge = screen.getByText('Active')
    expect(badge).toHaveClass('bg-green-100')
  })

  it('navigates to profile on click', () => {
    const employee = createMockEmployee()
    render(<EmployeeCard employee={employee} />)

    fireEvent.click(screen.getByText('View Profile'))
    expect(mockNavigate).toHaveBeenCalledWith(`/employees/${employee.id}`)
  })
})
```

### Integration Tests

```typescript
// EmployeeListPage.integration.test.tsx
describe('EmployeeListPage Integration', () => {
  it('loads and displays employees', async () => {
    render(<EmployeeListPage />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('John Smith')).toBeInTheDocument()
    })
  })

  it('filters employees by role', async () => {
    render(<EmployeeListPage />)

    const roleFilter = screen.getByLabelText('Role')
    fireEvent.change(roleFilter, { target: { value: 'NURSE' } })

    await waitFor(() => {
      expect(screen.queryByText('Care Worker')).not.toBeInTheDocument()
      expect(screen.getByText('Nurse')).toBeInTheDocument()
    })
  })
})
```

### E2E Tests

```typescript
// employee-directory.e2e.ts
test('complete employee workflow', async ({ page }) => {
  // 1. Navigate to employee list
  await page.goto('/employees')
  await expect(page.getByRole('heading', { name: 'Employee Directory' })).toBeVisible()

  // 2. Search for employee
  await page.getByPlaceholder('Search employees...').fill('John Smith')
  await expect(page.getByText('John Smith')).toBeVisible()

  // 3. View employee profile
  await page.getByText('View Profile').click()
  await expect(page.getByRole('heading', { name: 'John Smith' })).toBeVisible()

  // 4. Admin creates new employee
  await loginAsAdmin(page)
  await page.goto('/employees')
  await page.getByRole('button', { name: 'Add Employee' }).click()
  await fillEmployeeForm(page, employeeData)
  await page.getByRole('button', { name: 'Create Employee' }).click()
  await expect(page.getByText('Employee created successfully')).toBeVisible()
})
```

---

## Appendix

### Configuration File

```typescript
// src/config/employee.config.ts

export const EMPLOYEE_CONFIG = {
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // Search
  MIN_SEARCH_LENGTH: 2,
  SEARCH_DEBOUNCE_MS: 300,

  // Filters
  MAX_LOCATION_FILTERS: 10,

  // Caching
  QUERY_STALE_TIME: 5 * 60 * 1000, // 5 minutes
  QUERY_CACHE_TIME: 10 * 60 * 1000, // 10 minutes

  // Images
  AVATAR_THUMBNAIL_SIZE: 100,
  AVATAR_FULL_SIZE: 400,

  // Validation
  MAX_NAME_LENGTH: 100,
  MAX_EMAIL_LENGTH: 255,
  MIN_PHONE_LENGTH: 10,
} as const
```

---

**End of Document**

*Next Steps: Review and approve design, then proceed to implementation.*
