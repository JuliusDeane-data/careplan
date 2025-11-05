# Frontend Troubleshooting Guide

This document contains solutions to common issues encountered during frontend development and deployment.

---

## Table of Contents

1. [Blank White Screen Issues](#blank-white-screen-issues)
2. [Port Connection Refused](#port-connection-refused)
3. [PostCSS/Tailwind CSS Errors](#postcsstailwind-css-errors)
4. [TypeScript Import Errors](#typescript-import-errors)
5. [Login/Authentication Issues](#loginauthentication-issues)
6. [Development Server Issues](#development-server-issues)

---

## Blank White Screen Issues

### Symptom
Browser shows a blank white page, even though the dev server is running.

### Common Causes & Solutions

#### 1. Missing `@/lib/utils.ts` File
**Error:** `Failed to resolve import "@/lib/utils" from "src/components/ui/..."`

**Solution:**
```bash
# Create the missing utils file
mkdir -p src/lib
```

Then create `src/lib/utils.ts`:
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

#### 2. TypeScript Type Import Errors
**Error:** `The requested module does not provide an export named 'AxiosInstance'`

**Problem:** Importing TypeScript types as runtime values.

**Solution:** Use `import type` for TypeScript types:

❌ **Wrong:**
```typescript
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { User, LoginCredentials } from '@/types'
```

✅ **Correct:**
```typescript
import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { User, LoginCredentials } from '@/types'
```

**Files to check:**
- `src/services/api.ts`
- `src/services/auth.service.ts`
- `src/contexts/AuthContext.tsx`
- Any component importing types

#### 3. React Not Mounting
**Symptom:** Empty `<div id="root"></div>` in HTML.

**Debug Steps:**
1. Check browser console for JavaScript errors
2. Temporarily simplify `App.tsx` to test React mounting:
   ```tsx
   function App() {
     return <div>Test - React is working!</div>
   }
   export default App
   ```
3. If test works, restore original App and check for errors in child components

---

## Port Connection Refused

### Symptom
`ERR_CONNECTION_REFUSED` when accessing `http://localhost:3000`

### Solutions

#### 1. Port Already in Use
**Check what's using the port:**
```bash
# Windows
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :3000
```

**Kill the process:**
```bash
# Windows
taskkill //F //PID <process_id>

# Linux/Mac
kill -9 <process_id>
```

#### 2. Incorrect Vite Host Configuration
**Check `vite.config.ts`:**
```typescript
export default defineConfig({
  server: {
    host: 'localhost',  // Use 'localhost' not '0.0.0.0' for local dev
    port: 3000,
  },
})
```

#### 3. Dev Server Not Running
**Start the dev server:**
```bash
cd frontend
npm run dev
```

**Verify it's running:** Look for output:
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
```

---

## PostCSS/Tailwind CSS Errors

### Error 1: Tailwind v4 PostCSS Plugin Not Found
**Error:** `Package subpath './postcss' is not defined by "exports"`

**Problem:** Tailwind CSS v4 has a different PostCSS plugin structure.

**Solution:** Downgrade to Tailwind v3 (stable):

1. **Update `package.json`:**
   ```json
   "devDependencies": {
     "tailwindcss": "^3.4.1",
     "autoprefixer": "^10.4.21",
     "postcss": "^8.5.6"
   }
   ```

2. **Update `postcss.config.js`:**
   ```javascript
   export default {
     plugins: {
       tailwindcss: {},
       autoprefixer: {},
     },
   }
   ```

3. **Update `src/index.css`:**
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

4. **Reinstall:**
   ```bash
   npm install
   ```

---

## TypeScript Import Errors

### Best Practices for Imports

#### Types/Interfaces
Always use `import type` for TypeScript-only constructs:
```typescript
import type { User, LoginCredentials } from '@/types'
import type { AxiosInstance } from 'axios'
```

#### Runtime Values
Use regular imports for values used at runtime:
```typescript
import axios from 'axios'
import { authService } from '@/services/auth.service'
import { Button } from '@/components/ui/button'
```

#### Mixed Imports
You can combine both:
```typescript
import axios from 'axios'
import type { AxiosInstance, AxiosError } from 'axios'
```

### Path Alias Issues

**Verify `tsconfig.app.json` has path aliases:**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Verify `vite.config.ts` has aliases:**
```typescript
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

---

## Login/Authentication Issues

### Error: "Invalid email or password" (400 Bad Request)

#### Cause 1: No Users in Database
**Check if users exist:**
```bash
docker-compose exec web python manage.py shell -c "from apps.accounts.models import User; print('Users:', User.objects.count())"
```

**Create superuser:**
```bash
docker-compose exec -T web python manage.py shell <<'EOF'
from apps.accounts.models import User

user = User.objects.create_superuser(
    username='admin',
    email='admin@careplan.com',
    password='admin123',
    first_name='Admin',
    last_name='User',
    employee_id='EMP001'
)
print(f"Created: {user.email}")
EOF
```

#### Cause 2: Wrong Credentials
**Test credentials:**
- Email: `admin@careplan.com`
- Password: `admin123`

**Verify backend is working:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@careplan.com","password":"admin123"}'
```

Should return JWT tokens and user object.

#### Cause 3: Backend Not Running
**Check backend status:**
```bash
docker-compose ps
```

**Start backend:**
```bash
docker-compose up
```

### CORS Issues

**Symptom:** Login request blocked with CORS error.

**Check `backend/config/settings/base.py`:**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CORS_ALLOW_CREDENTIALS = True
```

**Verify frontend API URL in `.env`:**
```env
VITE_API_URL=http://localhost:8000/api
```

---

## Development Server Issues

### Hot Module Replacement (HMR) Not Working

**Solution 1: Restart dev server**
```bash
# Kill existing processes
taskkill //F //PID <pid>  # Windows
kill -9 <pid>             # Linux/Mac

# Restart
npm run dev
```

**Solution 2: Clear Vite cache**
```bash
rm -rf node_modules/.vite
npm run dev
```

### Build Errors

**Clear everything and rebuild:**
```bash
# Remove dependencies
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try dev server
npm run dev
```

### Port Changed Automatically

**Problem:** Vite says "Port 3000 is in use, trying another one..."

**Solution:** Kill all Node processes on port 3000:
```bash
# Windows
netstat -ano | findstr :3000
taskkill //F //PID <each_pid>

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

---

## Environment Setup

### Required Files

#### `.env`
```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=CarePlan
```

#### `vite.config.ts`
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
    host: 'localhost',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## Quick Checklist for Fresh Setup

1. ✅ Backend is running: `docker-compose up`
2. ✅ Database has users: Create superuser if needed
3. ✅ `.env` file exists with correct API URL
4. ✅ `src/lib/utils.ts` exists
5. ✅ All type imports use `import type`
6. ✅ Tailwind CSS v3 is installed (not v4)
7. ✅ No processes on port 3000
8. ✅ Node modules installed: `npm install`
9. ✅ Dev server running: `npm run dev`
10. ✅ Browser at `http://localhost:3000`

---

## Common Commands Reference

```bash
# Frontend
cd frontend
npm install              # Install dependencies
npm run dev             # Start dev server
npm run build           # Build for production
npm run preview         # Preview production build

# Backend
docker-compose up       # Start all services
docker-compose down     # Stop all services
docker-compose ps       # Check service status
docker-compose logs web # View backend logs

# Database
docker-compose exec web python manage.py shell       # Django shell
docker-compose exec web python manage.py migrate    # Run migrations
docker-compose exec web python manage.py createsuperuser  # Create user

# Port cleanup (Windows)
netstat -ano | findstr :3000  # Find process on port
taskkill //F //PID <pid>      # Kill process

# Port cleanup (Linux/Mac)
lsof -i :3000            # Find process on port
kill -9 <pid>            # Kill process
```

---

## Getting Help

If issues persist:

1. **Check browser console** (F12) for JavaScript errors
2. **Check terminal** for build errors
3. **Check backend logs**: `docker-compose logs web`
4. **Verify all services running**: `docker-compose ps`
5. **Test API directly**: Use curl or Postman to test endpoints

---

**Last Updated:** November 2025
**Frontend Version:** React 18 + Vite 7 + TypeScript
**Backend Version:** Django 5.2.7 + DRF
