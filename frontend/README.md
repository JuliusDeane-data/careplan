# CarePlan Frontend

Modern React frontend for the CarePlan care facility management system.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components
- **React Router v6** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client with interceptors
- **Zustand** - Lightweight state management
- **React Hook Form + Zod** - Form handling and validation

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Create production build:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Base shadcn/ui components (Button, Card, Input, etc.)
│   ├── auth/           # Authentication components (ProtectedRoute)
│   ├── layout/         # Layout components (Header, Sidebar, etc.)
│   ├── dashboard/      # Dashboard components
│   ├── employees/      # Employee management components
│   ├── vacation/       # Vacation management components
│   └── notifications/  # Notification components
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── hooks/              # Custom React hooks
├── pages/              # Page components
│   ├── LoginPage.tsx   # Login page
│   └── DashboardPage.tsx # Dashboard page
├── services/           # API services
│   ├── api.ts          # Axios instance with interceptors
│   └── auth.service.ts # Authentication service
├── types/              # TypeScript type definitions
│   └── index.ts        # All API and app types
├── lib/                # Utility functions
│   └── utils.ts        # CN utility for Tailwind
└── App.tsx             # Main app component with routing
```

## Features Implemented

### Phase 1: Authentication ✅
- [x] Login page with email/password
- [x] JWT token management (access + refresh)
- [x] Automatic token refresh on 401
- [x] Protected routes
- [x] Auth context and hooks
- [x] Logout functionality

### Phase 2: Dashboard ✅
- [x] Basic dashboard layout
- [x] User profile display
- [x] Vacation balance card
- [x] Quick actions
- [x] Welcome message

### Phase 3: To Be Implemented
- [ ] Employee management (CRUD)
- [ ] Vacation request creation
- [ ] Vacation approval workflow
- [ ] Calendar view
- [ ] Notifications system
- [ ] Location management
- [ ] User profile editing

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=CarePlan
```

## API Integration

The frontend communicates with the Django REST API at `/api/`:

### Authentication Endpoints
- `POST /api/auth/login/` - Login with email/password
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout (blacklist refresh token)
- `GET /api/auth/test/` - Test token validity

### User Endpoints
- `GET /api/users/me/` - Get current user profile
- `GET /api/users/` - List users (admin/manager)
- `POST /api/users/` - Create user (admin)
- `PATCH /api/users/{id}/` - Update user

### Vacation Endpoints
- `GET /api/vacation/requests/` - List vacation requests
- `POST /api/vacation/requests/` - Create vacation request
- `POST /api/vacation/requests/{id}/approve/` - Approve request
- `POST /api/vacation/requests/{id}/deny/` - Deny request
- `GET /api/vacation/requests/balance/` - Get vacation balance

### Dashboard Endpoints
- `GET /api/dashboard/stats/` - Get dashboard statistics

## Authentication Flow

1. User enters email and password on login page
2. Frontend sends credentials to `/api/auth/login/`
3. Backend returns JWT tokens (access + refresh) and user data
4. Tokens stored in localStorage
5. Access token attached to all API requests via interceptor
6. On 401 error, interceptor automatically refreshes token
7. If refresh fails, user redirected to login

## Styling

- Uses Tailwind CSS with custom theme
- Color scheme defined in `src/index.css`
- Dark mode support built-in
- Responsive design (mobile-first)
- shadcn/ui components for consistency

## Testing Credentials

Use the admin account created in backend:

```
Email: admin@careplan.com
Password: admin123
```

## Development Notes

- API proxy configured in `vite.config.ts` (proxies `/api` to `http://localhost:8000`)
- Path aliases: Use `@/` for absolute imports from `src/`
- TypeScript strict mode enabled
- All components use functional components with hooks

## Next Steps

1. Implement employee management pages
2. Add vacation request creation form
3. Build approval workflow UI
4. Add calendar view for vacations
5. Implement real-time notifications
6. Add comprehensive form validation
7. Add loading states and error boundaries
8. Implement pagination for lists
9. Add search and filtering
10. Create admin settings pages

## Support

For issues or questions, refer to the main CarePlan documentation or contact the development team.
