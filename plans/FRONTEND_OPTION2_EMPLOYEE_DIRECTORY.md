# Frontend Option 2: Employee Directory & Management

**Date:** 2025-11-05
**Priority:** MEDIUM
**Estimated Time:** 1-2 hours
**Status:** Ready to implement

---

## 🎯 Overview

Build a comprehensive employee directory that allows users to:
- Browse all employees in the organization
- Search and filter employees
- View detailed employee profiles
- See organizational structure
- Contact employees

Managers/Admins will additionally be able to:
- Add new employees
- Edit employee information
- Deactivate employees
- Assign roles and locations

---

## 📋 Features Breakdown

### Core Features (Must Have)
1. **Employee List View** - Grid/table of all employees
2. **Search & Filter** - Find employees quickly
3. **Employee Profile Page** - Detailed employee information
4. **Contact Information** - Phone, email, location

### Enhanced Features (Should Have)
5. **Employee Cards** - Visual card-based layout
6. **Profile Photos** - Avatar/photo display
7. **Location Filter** - Filter by location/facility
8. **Role Filter** - Filter by role/department
9. **Sort Options** - Name, role, location, hire date

### Admin Features (Nice to Have)
10. **Add Employee Form** - Create new employees
11. **Edit Employee** - Update information
12. **Employee Status** - Active/inactive toggle
13. **Bulk Actions** - Export, assign locations

---

## 🏗️ Architecture

### Page Structure
```
/employees
  ├── /                           → EmployeeListPage
  ├── /:id                        → EmployeeDetailPage
  ├── /new                        → AddEmployeePage (admin only)
  └── /:id/edit                   → EditEmployeePage (admin only)
```

### Component Hierarchy
```
EmployeeListPage
  ├── EmployeeFilters
  │   ├── SearchInput
  │   ├── LocationSelect
  │   ├── RoleSelect
  │   └── StatusSelect
  ├── ViewToggle (Grid/Table)
  ├── EmployeeStats (total, by location, etc.)
  └── EmployeeGrid | EmployeeTable
      └── EmployeeCard[] | EmployeeRow[]

EmployeeDetailPage
  ├── EmployeeHeader
  │   ├── Avatar
  │   ├── Name & Title
  │   └── ActionButtons
  ├── EmployeeInfoCard
  │   ├── Contact Information
  │   ├── Employment Information
  │   └── Location & Qualifications
  └── EmployeeActivityFeed
      └── Recent vacation, updates, etc.
```

### Data Models
```typescript
interface Employee {
  id: number
  employee_id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  avatar?: string
  role: 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
  employment_status: 'ACTIVE' | 'ON_LEAVE' | 'TERMINATED'
  primary_location?: Location
  additional_locations?: Location[]
  qualifications?: Qualification[]
  supervisor?: Employee
  hire_date?: string
  remaining_vacation_days: number
}

interface EmployeeFilters {
  search?: string
  location?: number
  role?: string
  status?: string
  page?: number
  ordering?: string
}
```

---

## 📝 Implementation Steps

### Step 1: Types & API Service (15 min)

**Create:** `src/types/employee.ts`
```typescript
export interface Employee {
  id: number
  employee_id: string
  first_name: string
  last_name: string
  full_name: string
  email: string
  phone?: string
  avatar?: string
  role: EmployeeRole
  employment_status: EmploymentStatus
  primary_location?: Location
  additional_locations?: Location[]
  qualifications?: Qualification[]
  supervisor?: EmployeeSummary
  hire_date?: string
  termination_date?: string
  remaining_vacation_days: number
  total_vacation_days: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type EmployeeRole = 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
export type EmploymentStatus = 'ACTIVE' | 'ON_LEAVE' | 'TERMINATED'

export interface EmployeeSummary {
  id: number
  full_name: string
  employee_id: string
}

export interface Location {
  id: number
  name: string
  code: string
}

export interface Qualification {
  id: number
  name: string
  code: string
}
```

**Create:** `src/services/employee.service.ts`
```typescript
import api from './api'
import type { Employee, EmployeeFilters } from '@/types/employee'

export const employeeService = {
  async getEmployees(filters?: EmployeeFilters) {
    const response = await api.get('/employees/', { params: filters })
    return response.data
  },

  async getEmployee(id: number): Promise<Employee> {
    const response = await api.get(`/employees/${id}/`)
    return response.data
  },

  async createEmployee(data: Partial<Employee>): Promise<Employee> {
    const response = await api.post('/employees/', data)
    return response.data
  },

  async updateEmployee(id: number, data: Partial<Employee>): Promise<Employee> {
    const response = await api.put(`/employees/${id}/`, data)
    return response.data
  },

  async deactivateEmployee(id: number): Promise<void> {
    await api.post(`/employees/${id}/deactivate/`)
  }
}
```

---

### Step 2: Employee List Page (30 min)

**File:** `src/pages/employees/EmployeeListPage.tsx`

**Layout:**
```
+--------------------------------------+
| Employees                            |
| [+ Add Employee] (admin only)        |
+--------------------------------------+

| [Search...] [Location▼] [Role▼]     |
| [Grid View] [Table View]             |
+--------------------------------------+

| 🏢 Total: 45  📍 Main: 20  🔴 On Leave: 3 |
+--------------------------------------+

Grid View:
+--------+  +--------+  +--------+
| John   |  | Jane   |  | Bob    |
| Doe    |  | Smith  |  | Wilson |
| 👤     |  | 👤     |  | 👤     |
| Manager|  | Employee|  | Admin  |
+--------+  +--------+  +--------+

Table View:
| Name       | ID    | Role     | Location | Status |
|------------|-------|----------|----------|--------|
| John Doe   | E001  | Manager  | Main     | Active |
| Jane Smith | E002  | Employee | Branch A | Active |
```

**Features:**
- Search by name/email/ID
- Filter by location, role, status
- Toggle grid/table view
- Pagination
- Sort options
- Click to view details

---

### Step 3: Employee Card Component (20 min)

**File:** `src/components/employees/EmployeeCard.tsx`

**Design:**
```
+-------------------------+
|         👤              |
|      [Avatar]           |
|                         |
|     John Doe            |
|     Manager             |
|     📍 Main Office      |
|     ✉️ john@care.com    |
|     📞 (555) 123-4567   |
|                         |
| [View Profile]          |
+-------------------------+
```

**Props:**
```typescript
interface EmployeeCardProps {
  employee: Employee
  onClick?: (id: number) => void
  showContact?: boolean
  showActions?: boolean
}
```

---

### Step 4: Employee Detail Page (30 min)

**File:** `src/pages/employees/EmployeeDetailPage.tsx`

**Layout:**
```
+----------------------------------+
| [← Back]           [Edit] [Deactivate] |
+----------------------------------+

+----------------------------------+
|        👤 [Large Avatar]         |
|        John Doe                  |
|        Manager                   |
|        Employee ID: EMP001       |
|        [Active Badge]            |
+----------------------------------+

+----------------------------------+
| Contact Information              |
| ✉️ john.doe@careplan.com        |
| 📞 (555) 123-4567               |
| 📍 123 Main St, City, ST 12345  |
+----------------------------------+

+----------------------------------+
| Employment Information           |
| Hire Date: Jan 15, 2023         |
| Supervisor: Jane Smith           |
| Primary Location: Main Office    |
| Role: Manager                    |
+----------------------------------+

+----------------------------------+
| Locations & Qualifications       |
| 📍 Main Office, Branch A         |
| 🎓 RN, CNA, CPR Certified       |
+----------------------------------+

+----------------------------------+
| Vacation Balance                 |
| 15 days remaining / 30 total     |
| [View Vacation History]          |
+----------------------------------+

+----------------------------------+
| Recent Activity                  |
| • Vacation approved (2 days ago) |
| • Profile updated (1 week ago)   |
+----------------------------------+
```

---

### Step 5: Employee Filters Component (15 min)

**File:** `src/components/employees/EmployeeFilters.tsx`

**Features:**
- Text search (debounced)
- Location dropdown (multi-select)
- Role dropdown
- Status dropdown
- Clear all filters button
- Active filter count badge

---

### Step 6: Employee Table View (20 min)

**File:** `src/components/employees/EmployeeTable.tsx`

**Columns:**
- Photo (avatar)
- Name
- Employee ID
- Role
- Location
- Status
- Actions (view, edit, etc.)

**Features:**
- Sortable columns
- Clickable rows
- Action dropdown menu
- Pagination controls

---

### Step 7: Add/Edit Employee Form (30 min) [Admin Only]

**File:** `src/pages/employees/EmployeeFormPage.tsx`

**Form Sections:**
```
+----------------------------------+
| Personal Information             |
| First Name: [________]           |
| Last Name:  [________]           |
| Email:      [________]           |
| Phone:      [________]           |
+----------------------------------+

+----------------------------------+
| Employment Information           |
| Employee ID: [________]          |
| Role:        [Manager ▼]         |
| Status:      [Active ▼]          |
| Hire Date:   [📅 Select]         |
| Supervisor:  [Select... ▼]       |
+----------------------------------+

+----------------------------------+
| Locations                        |
| Primary:     [Main Office ▼]     |
| Additional:  [☑ Branch A]        |
|              [☐ Branch B]        |
+----------------------------------+

+----------------------------------+
| Qualifications                   |
| [☑ RN] [☑ CNA] [☐ LPN]          |
+----------------------------------+

+----------------------------------+
| Vacation                         |
| Annual Days: [30________]        |
+----------------------------------+

| [Cancel]           [Save]        |
+----------------------------------+
```

**Validation:**
- Required: first name, last name, email, employee ID, role
- Email format validation
- Unique employee ID
- Valid hire date

---

## 🎨 UI Components Needed

**From shadcn/ui:**
- ✅ Card
- ✅ Button
- ✅ Input
- ✅ Select
- ✅ Badge
- ✅ Avatar
- ✅ Tabs
- ✅ Table
- ✅ Dialog
- ⬜ Checkbox (for multi-select)
- ⬜ Combobox (for searchable dropdowns)

**Install if needed:**
```bash
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add combobox
```

---

## 🔌 Integration Points

### React Query Hooks
```typescript
export function useEmployees(filters?: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => employeeService.getEmployees(filters),
    keepPreviousData: true
  })
}

export function useEmployee(id: number) {
  return useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeeService.getEmployee(id),
    enabled: !!id
  })
}

export function useCreateEmployee() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: employeeService.createEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries(['employees'])
    }
  })
}
```

### Routing Updates
```typescript
// Add to App.tsx
<Route path="/employees">
  <Route index element={<EmployeeListPage />} />
  <Route path=":id" element={<EmployeeDetailPage />} />
  <Route path="new" element={<EmployeeFormPage />} /> {/* Admin only */}
  <Route path=":id/edit" element={<EmployeeFormPage />} /> {/* Admin only */}
</Route>
```

---

## 🧪 Testing Checklist

- [ ] Load employee list
- [ ] Search employees
- [ ] Filter by location
- [ ] Filter by role
- [ ] Toggle grid/table view
- [ ] Sort columns (table view)
- [ ] Paginate through results
- [ ] Click to view details
- [ ] Admin: Create employee
- [ ] Admin: Edit employee
- [ ] Admin: Deactivate employee
- [ ] Mobile responsive

---

## 🎯 Success Criteria

1. ✅ Can browse all employees
2. ✅ Can search and filter effectively
3. ✅ Can view detailed employee profile
4. ✅ Grid and table views work
5. ✅ Pagination works correctly
6. ✅ Admin can add/edit employees
7. ✅ Responsive on all devices
8. ✅ Fast load times
9. ✅ Proper error handling
10. ✅ Loading states implemented

---

## 🚀 Implementation Order

**Total Time: 1-2 hours**

1. **Setup (15 min):** Types, API service, hooks
2. **List Page (30 min):** Grid view, filters, search
3. **Detail Page (30 min):** Profile view, info cards
4. **Polish (15 min):** Table view, loading states, errors

**Admin features can be added later as Phase 2.**

---

**Ready for implementation after Option 1!** 🎉
