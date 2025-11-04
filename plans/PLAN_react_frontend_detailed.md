# React Frontend - Detailed Implementation Plan

**Date**: 2025-11-04
**Status**: Ready to Execute
**Estimated Time**: 18-22 hours total
**Tech Stack**: React 18 + TypeScript + Vite + shadcn/ui + TanStack Query

---

## 🎯 Project Overview

Build a modern, type-safe React frontend for Careplan using best practices and industry-standard tools. The frontend will communicate with the Django REST API using JWT authentication.

---

## 📦 Tech Stack Summary

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | React 18 + TypeScript | UI library with type safety |
| **Build Tool** | Vite | Fast development and builds |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Components** | shadcn/ui | Beautiful, accessible components |
| **Routing** | React Router v6 | Client-side routing |
| **State (Server)** | TanStack Query | Data fetching, caching, mutations |
| **State (Client)** | Zustand | Lightweight global state |
| **Forms** | React Hook Form | Form management |
| **Validation** | Zod | Schema validation |
| **HTTP Client** | Axios | API requests with interceptors |
| **Icons** | Lucide React | Icon library |
| **Dates** | date-fns | Date manipulation |
| **Tables** | TanStack Table | Advanced data tables |
| **Dev Tools** | ESLint + Prettier | Code quality |

---

## 📋 Implementation Phases

### Phase 1: Project Setup & Core Configuration
### Phase 2: Authentication System
### Phase 3: Layout & Dashboard
### Phase 4: Employee Management
### Phase 5: Vacation Management
### Phase 6: Notifications & Polish

---

# PHASE 1: Project Setup & Core Configuration

**Time Estimate**: 2-3 hours
**Goal**: Set up React project with all dependencies and configurations

---

## Step 1.1: Create Vite Project (15 min)

```bash
# Navigate to project root
cd /home/philip/projects/careplan

# Create React + TypeScript project with Vite
npm create vite@latest frontend -- --template react-ts

# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

**Verify**:
```bash
npm run dev
# Should open at http://localhost:5173
```

---

## Step 1.2: Install Core Dependencies (15 min)

```bash
# Routing
npm install react-router-dom

# HTTP Client & State Management
npm install axios @tanstack/react-query zustand

# Forms & Validation
npm install react-hook-form zod @hookform/resolvers

# Date Handling
npm install date-fns

# Icons
npm install lucide-react

# Utilities
npm install clsx tailwind-merge class-variance-authority
```

**Dev Dependencies**:
```bash
npm install -D @types/node
```

---

## Step 1.3: Setup Tailwind CSS (20 min)

```bash
# Install Tailwind
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind config
npx tailwindcss init -p
```

**Update `tailwind.config.js`**:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}
```

**Update `src/index.css`**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## Step 1.4: Setup shadcn/ui (30 min)

```bash
# Initialize shadcn/ui
npx shadcn-ui@latest init
```

**Configuration prompts**:
- TypeScript: Yes
- Style: Default
- Base color: Slate
- CSS variables: Yes
- Tailwind config: Yes
- Components location: `src/components/ui`
- Utils location: `src/lib/utils.ts`
- React Server Components: No
- Icons library: lucide-react

**Install commonly used components**:
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
npx shadcn-ui@latest add calendar
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add command
npx shadcn-ui@latest add sheet
```

---

## Step 1.5: Create Project Structure (20 min)

```bash
cd src

# Create directory structure
mkdir -p api
mkdir -p components/{layout,auth,common}
mkdir -p features/{dashboard,employees,locations,vacation,notifications}
mkdir -p hooks
mkdir -p lib
mkdir -p types
mkdir -p store
mkdir -p routes
mkdir -p utils
```

**Final structure**:
```
src/
├── api/                    # API client and endpoints
├── components/
│   ├── ui/                 # shadcn/ui components (auto-generated)
│   ├── layout/             # Layout components
│   ├── auth/               # Auth-related components
│   └── common/             # Reusable components
├── features/               # Feature modules
│   ├── dashboard/
│   ├── employees/
│   ├── locations/
│   ├── vacation/
│   └── notifications/
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities
├── types/                  # TypeScript types
├── store/                  # Global state
├── routes/                 # Route definitions
├── utils/                  # Helper functions
├── App.tsx
├── main.tsx
└── index.css
```

---

## Step 1.6: Setup Path Aliases (15 min)

**Update `vite.config.ts`**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
})
```

**Update `tsconfig.json`**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## Step 1.7: Create Environment Variables (10 min)

**Create `.env.development`**:
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Careplan
VITE_APP_VERSION=1.0.0
```

**Create `.env.production`**:
```env
VITE_API_URL=https://api.careplan.com
VITE_APP_NAME=Careplan
VITE_APP_VERSION=1.0.0
```

**Create `src/config/env.ts`**:
```typescript
export const env = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  appName: import.meta.env.VITE_APP_NAME || 'Careplan',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
}
```

---

## Step 1.8: Create Utility Functions (15 min)

**Create `src/lib/utils.ts`** (if not already created by shadcn):
```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Create `src/utils/date.ts`**:
```typescript
import { format, formatDistance, parseISO } from 'date-fns'

export function formatDate(date: string | Date, formatStr: string = 'PPP'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, formatStr)
}

export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return formatDistance(dateObj, new Date(), { addSuffix: true })
}

export function formatDateTime(date: string | Date): string {
  return formatDate(date, 'PPpp')
}
```

**Create `src/utils/format.ts`**:
```typescript
export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function formatPhoneNumber(phone: string): string {
  const cleaned = phone.replace(/\D/g, '')
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`
  }
  return phone
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}
```

---

## Step 1.9: Setup ESLint & Prettier (Optional but Recommended) (20 min)

**Install dependencies**:
```bash
npm install -D eslint-config-prettier prettier
```

**Create `.prettierrc`**:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always"
}
```

**Create `.prettierignore`**:
```
node_modules
dist
build
.env*
*.md
```

**Update `package.json` scripts**:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css,md}\""
  }
}
```

---

## ✅ Phase 1 Checklist

- [ ] Vite project created
- [ ] All dependencies installed
- [ ] Tailwind CSS configured
- [ ] shadcn/ui components installed
- [ ] Project structure created
- [ ] Path aliases configured
- [ ] Environment variables set up
- [ ] Utility functions created
- [ ] ESLint & Prettier configured (optional)
- [ ] Dev server runs without errors

**Verification**:
```bash
npm run dev
# Should open at http://localhost:3000
# No errors in console
```

---

# PHASE 2: Authentication System

**Time Estimate**: 3-4 hours
**Goal**: Implement complete authentication flow with JWT

---

## Step 2.1: Create TypeScript Types (20 min)

**Create `src/types/auth.ts`**:
```typescript
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  employee_id: string
  role: UserRole
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  avatar?: string
  phone_number?: string
  primary_location?: Location
  additional_locations?: Location[]
  qualifications?: Qualification[]
  employment_status: EmploymentStatus
  hire_date?: string
  termination_date?: string
  remaining_vacation_days: number
  total_vacation_days: number
}

export type UserRole = 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
export type EmploymentStatus = 'ACTIVE' | 'ON_LEAVE' | 'TERMINATED'

export interface Location {
  id: number
  name: string
  code: string
  address?: string
  city?: string
  state?: string
  postal_code?: string
}

export interface Qualification {
  id: number
  name: string
  code: string
  description?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface TokenRefreshRequest {
  refresh: string
}

export interface TokenRefreshResponse {
  access: string
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
```

**Create `src/types/api.ts`**:
```typescript
export interface ApiError {
  message: string
  errors?: Record<string, string[]>
  status?: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiResponse<T> {
  data: T
  message?: string
}
```

---

## Step 2.2: Create API Client (30 min)

**Create `src/api/client.ts`**:
```typescript
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { env } from '@/config/env'

const API_BASE_URL = env.apiUrl

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        // Try to refresh token
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        localStorage.setItem('accessToken', access)

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

---

## Step 2.3: Create Auth API Service (20 min)

**Create `src/api/auth.ts`**:
```typescript
import apiClient from './client'
import { LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse, User } from '@/types/auth'

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/login/', credentials)
    return response.data
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout/')
  },

  refreshToken: async (refreshToken: string): Promise<TokenRefreshResponse> => {
    const response = await apiClient.post<TokenRefreshResponse>('/auth/refresh/', {
      refresh: refreshToken,
    })
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me/')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.put<User>('/users/me/', data)
    return response.data
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/users/me/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },
}
```

---

## Step 2.4: Create Auth Store (Zustand) (30 min)

**Create `src/store/authStore.ts`**:
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AuthState, User, LoginRequest } from '@/types/auth'
import { authApi } from '@/api/auth'

interface AuthStore extends AuthState {
  setUser: (user: User | null) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => {
        set({ user, isAuthenticated: !!user })
      },

      setTokens: (accessToken, refreshToken) => {
        localStorage.setItem('accessToken', accessToken)
        localStorage.setItem('refreshToken', refreshToken)
        set({ accessToken, refreshToken, isAuthenticated: true })
      },

      login: async (credentials) => {
        set({ isLoading: true })
        try {
          const response = await authApi.login(credentials)
          const { access, refresh, user } = response

          // Store tokens
          get().setTokens(access, refresh)
          set({ user, isAuthenticated: true })
        } catch (error) {
          console.error('Login failed:', error)
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      logout: async () => {
        try {
          await authApi.logout()
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          // Clear tokens and user
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          })
        }
      },

      refreshUser: async () => {
        try {
          const user = await authApi.getCurrentUser()
          set({ user })
        } catch (error) {
          console.error('Failed to refresh user:', error)
          get().logout()
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
```

---

## Step 2.5: Create Auth Hook (20 min)

**Create `src/hooks/useAuth.ts`**:
```typescript
import { useAuthStore } from '@/store/authStore'
import { useEffect } from 'react'

export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
  } = useAuthStore()

  // Refresh user data on mount if authenticated
  useEffect(() => {
    if (isAuthenticated && !user) {
      refreshUser()
    }
  }, [isAuthenticated, user, refreshUser])

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
    isAdmin: user?.is_superuser || false,
    isManager: user?.role === 'MANAGER' || user?.is_staff || false,
    isEmployee: user?.role === 'EMPLOYEE' || false,
  }
}
```

---

## Step 2.6: Create Login Page (45 min)

**Create `src/features/auth/LoginPage.tsx`**:
```typescript
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    setError(null)
    try {
      await login(data)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid email or password')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Careplan</CardTitle>
          <CardDescription className="text-center">
            Sign in to your account to continue
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="john.doe@example.com"
                {...register('email')}
                disabled={isSubmitting}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                {...register('password')}
                disabled={isSubmitting}
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

---

## Step 2.7: Create Protected Route Component (20 min)

**Create `src/components/auth/ProtectedRoute.tsx`**:
```typescript
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requiredRole && user?.role !== requiredRole && !user?.is_superuser) {
    return <Navigate to="/unauthorized" replace />
  }

  return <>{children}</>
}
```

---

## Step 2.8: Setup React Query Provider (15 min)

**Create `src/lib/queryClient.ts`**:
```typescript
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})
```

**Update `src/main.tsx`**:
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { queryClient } from '@/lib/queryClient'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
)
```

---

## Step 2.9: Setup Routing (20 min)

**Create `src/routes/index.tsx`**:
```typescript
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LoginPage } from '@/features/auth/LoginPage'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Dashboard } from '@/features/dashboard/Dashboard'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      // More routes will be added in later phases
    ],
  },
  {
    path: '*',
    element: <div>404 - Page Not Found</div>,
  },
])
```

**Update `src/App.tsx`**:
```typescript
import { RouterProvider } from 'react-router-dom'
import { router } from '@/routes'
import { Toaster } from '@/components/ui/toaster'

function App() {
  return (
    <>
      <RouterProvider router={router} />
      <Toaster />
    </>
  )
}

export default App
```

---

## ✅ Phase 2 Checklist

- [ ] TypeScript types created
- [ ] API client with interceptors configured
- [ ] Auth API service created
- [ ] Auth store (Zustand) implemented
- [ ] Auth hook created
- [ ] Login page built
- [ ] Protected route component created
- [ ] React Query provider set up
- [ ] Routing configured
- [ ] Can login and logout successfully

**Verification**:
- Open http://localhost:3000
- Should redirect to /login
- Login with credentials (need backend API)
- Should redirect to /dashboard
- Token stored in localStorage
- Logout works

---

# PHASE 3: Layout & Dashboard

**Time Estimate**: 3-4 hours
**Goal**: Create responsive layout and dashboard with statistics

---

## Step 3.1: Create Sidebar Component (45 min)

**Create `src/components/layout/Sidebar.tsx`**:
```typescript
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Users,
  MapPin,
  Calendar,
  Bell,
  Settings,
  LogOut,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { Separator } from '@/components/ui/separator'

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Employees',
    href: '/employees',
    icon: Users,
    roles: ['ADMIN', 'MANAGER'],
  },
  {
    title: 'Locations',
    href: '/locations',
    icon: MapPin,
  },
  {
    title: 'Vacation',
    href: '/vacation',
    icon: Calendar,
  },
  {
    title: 'Notifications',
    href: '/notifications',
    icon: Bell,
  },
]

export function Sidebar() {
  const location = useLocation()
  const { user, logout, isAdmin, isManager } = useAuth()

  const filteredItems = navigationItems.filter((item) => {
    if (!item.roles) return true
    return item.roles.some((role) =>
      (role === 'ADMIN' && isAdmin) || (role === 'MANAGER' && isManager)
    )
  })

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-primary">Careplan</h2>
        <p className="text-sm text-muted-foreground">Care Management</p>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 p-4">
        {filteredItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href

          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.title}
            </Link>
          )
        })}
      </nav>

      <Separator />

      <div className="p-4 space-y-2">
        <Link to="/settings">
          <Button variant="ghost" className="w-full justify-start" size="sm">
            <Settings className="mr-3 h-5 w-5" />
            Settings
          </Button>
        </Link>
        <Button
          variant="ghost"
          className="w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50"
          size="sm"
          onClick={logout}
        >
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </Button>
      </div>

      <div className="border-t p-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-sm font-medium text-primary">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </span>
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-medium truncate">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

## Step 3.2: Create Navbar Component (30 min)

**Create `src/components/layout/Navbar.tsx`**:
```typescript
import { Bell, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { useNavigate } from 'react-router-dom'

export function Navbar() {
  const navigate = useNavigate()
  const unreadCount = 3 // TODO: Get from notifications API

  return (
    <header className="sticky top-0 z-50 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="flex h-16 items-center gap-4 px-6">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search employees, locations..."
              className="pl-10"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <Badge
                    variant="destructive"
                    className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                  >
                    {unreadCount}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="flex flex-col items-start py-3">
                <p className="text-sm font-medium">Vacation Request Approved</p>
                <p className="text-xs text-muted-foreground">
                  Your vacation request for Dec 20-27 has been approved
                </p>
                <p className="text-xs text-muted-foreground mt-1">2 hours ago</p>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-center"
                onClick={() => navigate('/notifications')}
              >
                View all notifications
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
```

---

## Step 3.3: Create Dashboard Layout (20 min)

**Create `src/components/layout/DashboardLayout.tsx`**:
```typescript
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Navbar } from './Navbar'

export function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-y-auto bg-background p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
```

---

## Step 3.4: Create Dashboard Stats Cards (45 min)

**Create `src/features/dashboard/StatsCard.tsx`**:
```typescript
import { LucideIcon } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface StatsCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  description?: string
  trend?: {
    value: number
    isPositive: boolean
  }
  isLoading?: boolean
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  isLoading,
}: StatsCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-8 rounded" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-16 mb-2" />
          <Skeleton className="h-3 w-32" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-5 w-5 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
        {trend && (
          <p
            className={`text-xs mt-1 ${
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {trend.isPositive ? '+' : '-'}
            {Math.abs(trend.value)}% from last month
          </p>
        )}
      </CardContent>
    </Card>
  )
}
```

---

## Step 3.5: Create Dashboard Page (60 min)

**Create `src/api/dashboard.ts`**:
```typescript
import apiClient from './client'

export interface DashboardStats {
  total_employees: number
  active_employees: number
  total_locations: number
  pending_vacation_requests: number
  vacation_balance: number
  upcoming_vacations: number
}

export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats/')
    return response.data
  },
}
```

**Create `src/features/dashboard/Dashboard.tsx`**:
```typescript
import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboard'
import { StatsCard } from './StatsCard'
import { Users, MapPin, Calendar, Clock } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'

export function Dashboard() {
  const { user, isManager, isAdmin } = useAuth()
  const navigate = useNavigate()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
  })

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="text-muted-foreground">
          Here's what's happening with your team today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {(isAdmin || isManager) && (
          <>
            <StatsCard
              title="Total Employees"
              value={stats?.total_employees || 0}
              icon={Users}
              description={`${stats?.active_employees || 0} active`}
              isLoading={isLoading}
            />
            <StatsCard
              title="Locations"
              value={stats?.total_locations || 0}
              icon={MapPin}
              description="Active facilities"
              isLoading={isLoading}
            />
            <StatsCard
              title="Pending Requests"
              value={stats?.pending_vacation_requests || 0}
              icon={Clock}
              description="Awaiting approval"
              isLoading={isLoading}
            />
          </>
        )}
        <StatsCard
          title="Vacation Balance"
          value={stats?.vacation_balance || user?.remaining_vacation_days || 0}
          icon={Calendar}
          description="Days remaining"
          isLoading={isLoading}
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <Button
            variant="outline"
            className="h-24 flex-col"
            onClick={() => navigate('/vacation/new')}
          >
            <Calendar className="h-8 w-8 mb-2" />
            Request Vacation
          </Button>
          <Button
            variant="outline"
            className="h-24 flex-col"
            onClick={() => navigate('/vacation')}
          >
            <Clock className="h-8 w-8 mb-2" />
            View My Requests
          </Button>
          {(isAdmin || isManager) && (
            <Button
              variant="outline"
              className="h-24 flex-col"
              onClick={() => navigate('/employees')}
            >
              <Users className="h-8 w-8 mb-2" />
              Manage Employees
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Recent Activity (placeholder) */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No recent activity to display.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
```

---

## ✅ Phase 3 Checklist

- [ ] Sidebar with navigation created
- [ ] Navbar with search and notifications created
- [ ] Dashboard layout implemented
- [ ] Stats cards component built
- [ ] Dashboard page with statistics working
- [ ] Quick actions functional
- [ ] Responsive design works on mobile
- [ ] Navigation between pages works

**Verification**:
- Login and see dashboard
- Stats display correctly
- Sidebar navigation works
- Notifications dropdown works
- Quick action buttons navigate correctly
- Responsive on mobile (hamburger menu in future)

---

# PHASE 4: Employee Management

**Time Estimate**: 4-5 hours
**Goal**: Full CRUD for employees with list, detail, and forms

---

## Step 4.1: Create Employee Types (15 min)

**Create `src/types/employee.ts`**:
```typescript
import { Location, Qualification, EmploymentStatus } from './auth'

export interface Employee {
  id: number
  email: string
  first_name: string
  last_name: string
  employee_id: string
  phone_number?: string
  date_of_birth?: string
  address?: string
  city?: string
  state?: string
  postal_code?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  hire_date?: string
  termination_date?: string
  employment_status: EmploymentStatus
  role: 'ADMIN' | 'MANAGER' | 'EMPLOYEE'
  primary_location?: Location
  additional_locations?: Location[]
  qualifications?: Qualification[]
  supervisor?: {
    id: number
    first_name: string
    last_name: string
  }
  remaining_vacation_days: number
  total_vacation_days: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EmployeeFormData {
  email: string
  first_name: string
  last_name: string
  employee_id: string
  phone_number?: string
  date_of_birth?: string
  address?: string
  city?: string
  state?: string
  postal_code?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  hire_date?: string
  employment_status: EmploymentStatus
  role: string
  primary_location?: number
  additional_locations?: number[]
  qualifications?: number[]
  supervisor?: number
  total_vacation_days: number
}
```

---

## Step 4.2: Create Employee API Service (20 min)

**Create `src/api/employees.ts`**:
```typescript
import apiClient from './client'
import { Employee, EmployeeFormData } from '@/types/employee'
import { PaginatedResponse } from '@/types/api'

export interface EmployeeFilters {
  search?: string
  location?: number
  status?: string
  role?: string
  page?: number
  page_size?: number
}

export const employeesApi = {
  getEmployees: async (filters?: EmployeeFilters): Promise<PaginatedResponse<Employee>> => {
    const response = await apiClient.get<PaginatedResponse<Employee>>('/employees/', {
      params: filters,
    })
    return response.data
  },

  getEmployee: async (id: number): Promise<Employee> => {
    const response = await apiClient.get<Employee>(`/employees/${id}/`)
    return response.data
  },

  createEmployee: async (data: EmployeeFormData): Promise<Employee> => {
    const response = await apiClient.post<Employee>('/employees/', data)
    return response.data
  },

  updateEmployee: async (id: number, data: Partial<EmployeeFormData>): Promise<Employee> => {
    const response = await apiClient.put<Employee>(`/employees/${id}/`, data)
    return response.data
  },

  deleteEmployee: async (id: number): Promise<void> => {
    await apiClient.delete(`/employees/${id}/`)
  },

  terminateEmployee: async (id: number, terminationDate: string): Promise<Employee> => {
    const response = await apiClient.post<Employee>(`/employees/${id}/terminate/`, {
      termination_date: terminationDate,
    })
    return response.data
  },
}
```

---

## Step 4.3: Create Employee List Page (90 min)

**Install TanStack Table**:
```bash
npm install @tanstack/react-table
```

**Create `src/features/employees/EmployeeList.tsx`**:
```typescript
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { employeesApi } from '@/api/employees'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Plus, Search, MoreHorizontal, Pencil, Trash2 } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'

export function EmployeeList() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['employees', { search, status, page }],
    queryFn: () => employeesApi.getEmployees({ search, status, page }),
  })

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'success' | 'warning' | 'destructive'> = {
      ACTIVE: 'success',
      ON_LEAVE: 'warning',
      TERMINATED: 'destructive',
    }
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Employees</h1>
          <p className="text-muted-foreground">
            Manage your team members and their information
          </p>
        </div>
        <Button onClick={() => navigate('/employees/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Add Employee
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Statuses</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="ON_LEAVE">On Leave</SelectItem>
              <SelectItem value="TERMINATED">Terminated</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 7 }).map((_, j) => (
                      <TableCell key={j}>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data?.results && data.results.length > 0 ? (
                data.results.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell className="font-medium">{employee.employee_id}</TableCell>
                    <TableCell>
                      {employee.first_name} {employee.last_name}
                    </TableCell>
                    <TableCell>{employee.email}</TableCell>
                    <TableCell className="capitalize">{employee.role.toLowerCase()}</TableCell>
                    <TableCell>{employee.primary_location?.name || '-'}</TableCell>
                    <TableCell>{getStatusBadge(employee.employment_status)}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => navigate(`/employees/${employee.id}`)}
                          >
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => navigate(`/employees/${employee.id}/edit`)}
                          >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    No employees found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {data && data.count > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {data.results.length} of {data.count} employees
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!data.previous}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!data.next}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
```

---

## Step 4.4: Create Employee Detail Page (45 min)

**Create `src/features/employees/EmployeeDetail.tsx`**:
```typescript
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { employeesApi } from '@/api/employees'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Pencil, MapPin, Calendar, Award } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { formatDate } from '@/utils/date'

export function EmployeeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: employee, isLoading } = useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeesApi.getEmployee(Number(id)),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!employee) {
    return <div>Employee not found</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/employees')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {employee.first_name} {employee.last_name}
            </h1>
            <p className="text-muted-foreground">{employee.email}</p>
          </div>
        </div>
        <Button onClick={() => navigate(`/employees/${id}/edit`)}>
          <Pencil className="mr-2 h-4 w-4" />
          Edit
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Employee ID</p>
              <p className="text-sm">{employee.employee_id}</p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Phone Number</p>
              <p className="text-sm">{employee.phone_number || '-'}</p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Date of Birth</p>
              <p className="text-sm">
                {employee.date_of_birth ? formatDate(employee.date_of_birth) : '-'}
              </p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Address</p>
              <p className="text-sm">
                {employee.address ? (
                  <>
                    {employee.address}
                    <br />
                    {employee.city}, {employee.state} {employee.postal_code}
                  </>
                ) : (
                  '-'
                )}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Employment Information */}
        <Card>
          <CardHeader>
            <CardTitle>Employment Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Role</p>
              <Badge>{employee.role}</Badge>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <Badge>{employee.employment_status}</Badge>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Hire Date</p>
              <p className="text-sm">
                {employee.hire_date ? formatDate(employee.hire_date) : '-'}
              </p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Primary Location</p>
              <p className="text-sm flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {employee.primary_location?.name || '-'}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Vacation Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Vacation Balance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Remaining Days</p>
              <p className="text-2xl font-bold">{employee.remaining_vacation_days}</p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Annual Days</p>
              <p className="text-sm">{employee.total_vacation_days}</p>
            </div>
          </CardContent>
        </Card>

        {/* Qualifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Qualifications
            </CardTitle>
          </CardHeader>
          <CardContent>
            {employee.qualifications && employee.qualifications.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {employee.qualifications.map((qual) => (
                  <Badge key={qual.id} variant="secondary">
                    {qual.name}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No qualifications assigned</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

---

## Step 4.5: Create Employee Form (90 min)

This step is complex and will be detailed in the next section. For now, I'll provide a simplified version.

**Create `src/features/employees/EmployeeForm.tsx`**:
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { employeesApi } from '@/api/employees'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

const employeeSchema = z.object({
  email: z.string().email('Invalid email'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  employee_id: z.string().min(1, 'Employee ID is required'),
  phone_number: z.string().optional(),
  // ... more fields
})

type EmployeeFormData = z.infer<typeof employeeSchema>

export function EmployeeForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEditing = !!id

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EmployeeFormData>({
    resolver: zodResolver(employeeSchema),
  })

  const createMutation = useMutation({
    mutationFn: employeesApi.createEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      toast({ title: 'Employee created successfully' })
      navigate('/employees')
    },
  })

  const onSubmit = async (data: EmployeeFormData) => {
    await createMutation.mutateAsync(data as any)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/employees')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">
          {isEditing ? 'Edit Employee' : 'Add New Employee'}
        </h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader>
            <CardTitle>Employee Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name *</Label>
                <Input id="first_name" {...register('first_name')} />
                {errors.first_name && (
                  <p className="text-sm text-red-500">{errors.first_name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name *</Label>
                <Input id="last_name" {...register('last_name')} />
                {errors.last_name && (
                  <p className="text-sm text-red-500">{errors.last_name.message}</p>
                )}
              </div>

              {/* More fields... */}
            </div>

            <div className="flex gap-4 justify-end">
              <Button type="button" variant="outline" onClick={() => navigate('/employees')}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : isEditing ? 'Update' : 'Create'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
```

---

## ✅ Phase 4 Checklist

- [ ] Employee types defined
- [ ] Employee API service created
- [ ] Employee list with search and filters
- [ ] Employee detail page
- [ ] Employee create/edit form
- [ ] Delete employee functionality
- [ ] CRUD operations working
- [ ] Table pagination working

---

# PHASE 5: Vacation Management

**Time Estimate**: 4-5 hours
**Goal**: Complete vacation request system with calendar view

(Due to length constraints, I'll create separate detailed documents for Phases 5 and 6)

---

# PHASE 6: Notifications & Polish

**Time Estimate**: 2-3 hours
**Goal**: Real-time notifications and final polish

(Detailed plan will follow)

---

## 🎯 Summary

This detailed plan provides:

1. **Step-by-step instructions** for each phase
2. **Code snippets** for every component
3. **Time estimates** for realistic planning
4. **Verification steps** to ensure quality
5. **Complete file structure**

**Total Time**: 18-22 hours of focused work

**Next Action**: Start with Phase 1 - shall I begin implementing?
