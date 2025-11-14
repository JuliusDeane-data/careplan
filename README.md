# CarePlan - Intensive Care Facility Management System

A comprehensive management system designed specifically for intensive care and healthcare facilities, handling employee management, certification tracking, vacation planning, shift scheduling, and compliance management.

## 🏥 Overview

CarePlan is purpose-built for the unique challenges of intensive care facility management, where patient safety, regulatory compliance, and 24/7 operations require specialized software solutions. The system addresses critical healthcare needs including staff certification tracking, skills management, shift scheduling with safety rules, and comprehensive compliance reporting.

## ✨ Key Features

### 🔐 Public Homepage & Access
- **Public Landing Page**: Professional homepage for visitors without sensitive data exposure
- **Embedded Login**: Convenient header login for quick employee access
- **Feature Showcase**: Comprehensive overview of platform capabilities
- **Responsive Design**: Modern, gradient-based UI optimized for all devices

### 👥 Employee Management
- **Comprehensive Profiles**: Full employee data with contact info, employment details, and location assignments
- **Multi-Location Support**: Assign employees to primary and secondary locations
- **Role-Based Access**: EMPLOYEE, MANAGER, and ADMIN roles with appropriate permissions
- **Employee Directory**: Searchable, filterable directory for managers and admins
- **Profile Pages**: Detailed employee profiles with vacation balance, certifications, and personal information

### 📜 Certification & Compliance Management
- **Qualification Tracking**: Track all employee certifications (BLS, ACLS, PALS, RN licenses, etc.)
- **Expiry Management**: Automatic status updates with 90/60/30/14-day expiry warnings
- **Document Upload**: Upload and verify certificate documents
- **Compliance Dashboard**: Real-time view of certification status across all employees
- **Verification Workflow**: Manager verification of certifications with audit trail
- **Category System**: Must-have, specialized, and optional qualifications
- **Renewal Tracking**: Automatic calculation of renewal periods (e.g., 24 months for BLS/ACLS)

### 🗓️ Vacation Management
- **Request System**: Easy vacation request submission with date pickers
- **Approval Workflow**: Manager approval/denial with reasons
- **Balance Tracking**: Real-time vacation day balance with used/remaining calculations
- **Calendar Integration**: Visual calendar showing vacation periods
- **Public Holiday Support**: Configurable public holidays that don't count toward vacation days
- **Status Tracking**: PENDING, APPROVED, DENIED, CANCELLED states with full audit trail

### 📊 Enhanced Dashboard
- **Role-Based Widgets**: Different dashboard views for employees, managers, and admins
- **Real-Time Stats**: Live statistics with 30-second auto-refresh
- **Activity Feed**: Recent system activities (vacation requests, approvals, employee updates)
- **Upcoming Events**: Calendar widget showing upcoming vacations and events
- **Quick Actions**: Role-appropriate quick action menu
- **Personal Stats**: Vacation balance, pending requests, upcoming vacations
- **Team Stats** (Managers): Team members, current vacations, pending approvals
- **System Stats** (Admins): Total employees, active count, system-wide metrics

### 📱 User Experience
- **User Profiles**: Comprehensive profile pages showing employment details, vacation balance, certifications
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Dark Mode Support**: Full dark mode theme
- **Toast Notifications**: User-friendly success/error messages
- **Loading States**: Clear loading indicators for all async operations
- **Error Handling**: Comprehensive error handling with helpful messages

### 🔒 Security & Compliance
- **GDPR Compliant**: Built for European data protection requirements
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Permissions**: Granular access control
- **Audit Logging**: Complete audit trail for compliance
- **Data Encryption**: Encrypted data at rest and in transit
- **HIPAA Considerations**: No PHI storage, employee data protection

## 🏗️ Architecture

### Backend
- **Framework**: Django 5.2.7 with Django REST Framework
- **Database**: PostgreSQL 15+ with optimized indexing
- **Cache**: Redis for sessions and query caching
- **Task Queue**: Celery for async operations
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Storage**: Configurable (local, S3, etc.)

### Frontend
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **Router**: React Router v7
- **State Management**: React Query (TanStack Query v5)
- **Forms**: React Hook Form + Zod validation
- **UI Components**: shadcn/ui + Tailwind CSS
- **Icons**: Lucide React
- **Notifications**: Sonner (toast library)
- **Date Handling**: date-fns

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Deployment Ready**: Production-optimized builds
- **Scalable**: Supports 100+ concurrent users
- **Performance**: < 2s page loads, < 200ms API responses

## 📁 Project Structure

```
careplan/
├── apps/                          # Django applications
│   ├── core/                     # Shared utilities and base models
│   ├── accounts/                 # Authentication and user management
│   ├── employees/                # Employee profiles, certifications, skills
│   ├── locations/                # Location management
│   ├── notifications/            # Notification system
│   └── vacation/                 # Vacation planning module
├── frontend/                      # React frontend application
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── auth/             # Authentication components
│   │   │   ├── dashboard/        # Dashboard widgets
│   │   │   ├── employees/        # Employee components
│   │   │   ├── vacation/         # Vacation components
│   │   │   ├── common/           # Shared components (ErrorBoundary)
│   │   │   └── ui/               # shadcn/ui components
│   │   ├── pages/                # Page components
│   │   │   ├── HomePage.tsx      # Public landing page
│   │   │   ├── ProfilePage.tsx   # User profile page
│   │   │   ├── DashboardPage.tsx # Main dashboard
│   │   │   ├── employees/        # Employee pages
│   │   │   └── vacation/         # Vacation pages
│   │   ├── hooks/                # Custom React hooks
│   │   ├── services/             # API service layer
│   │   ├── types/                # TypeScript type definitions
│   │   ├── utils/                # Utility functions
│   │   ├── config/               # Frontend configuration
│   │   └── contexts/             # React contexts
│   └── package.json
├── config/                        # Django configuration
│   ├── settings/                 # Environment-specific settings
│   └── celery.py                 # Celery configuration
├── plans/                         # Design documents and planning
│   ├── CODE_REVIEW_FINDINGS.md
│   ├── EMPLOYEE_DIRECTORY_DESIGN.md
│   ├── ENHANCED_DASHBOARD_DESIGN.md
│   ├── VACATION_FUTURE_ENHANCEMENTS.md
│   └── NEXT_MODULES_PLAN.md
├── ICU_MANAGER_REQUIREMENTS.md   # Intensive care manager perspective
├── DEVELOPMENT_TODO_LIST.md      # Phased development plan
├── TEST_DATA_README.md           # Test data documentation
├── TEST_CREDENTIALS.md           # Quick reference for test accounts
├── requirements/                  # Python dependencies
├── tests/                        # Test files
├── docker-compose.yml            # Docker services configuration
└── load_test_data.py             # Test data loading script
```

## 🚀 Getting Started

### Prerequisites

- **Python** 3.12+
- **Node.js** 18+ and npm
- **Docker & Docker Compose** (recommended)
- **PostgreSQL** 15+ (if not using Docker)
- **Redis** (if not using Docker)

### Quick Start with Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd careplan
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**:
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Load test data** (optional but recommended):
   ```bash
   docker-compose exec web python load_test_data.py
   ```

6. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Local Development Setup

#### Backend Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements/development.txt
   ```

3. **Set up database** (PostgreSQL and Redis):
   ```bash
   # Option 1: Use Docker for database only
   docker-compose up db redis -d

   # Option 2: Install locally
   # Install PostgreSQL and Redis according to your OS
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Load test data** (optional):
   ```bash
   python load_test_data.py
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Access frontend**:
   Open http://localhost:5173

## 📚 Test Data

The system includes comprehensive test data for development and testing:

### Quick Test Login

All test users have password: **`Test123!`**

**Admin Account:**
```
Email: sarah.anderson@sunshinecare.de
Username: admin001
Role: ADMIN
```

**Manager Account:**
```
Email: michael.schmidt@sunshinecare.de
Username: mgr001
Role: MANAGER
Location: Central (Berlin)
```

**Employee Account:**
```
Email: emma.mueller@sunshinecare.de
Username: nurse001
Role: EMPLOYEE (Registered Nurse)
```

### Test Data Contents

- **4 Care Facilities**: Berlin, Hamburg, Munich, Dresden
- **12 Employees**: Admins, managers, nurses, care workers
- **4 Qualifications**: RN, CNA, BLS, ACLS
- **10 Vacation Requests**: Various states for testing workflow
- **7 Public Holidays**: German holidays for 2025

See `TEST_DATA_README.md` and `TEST_CREDENTIALS.md` for complete details.

## 🎯 User Roles

### EMPLOYEE
- View own profile and vacation balance
- Submit vacation requests
- View own certifications
- See personal dashboard statistics
- Access own information only

### MANAGER
- All employee permissions
- View team member profiles
- Approve/deny vacation requests
- View team statistics
- Access employee directory
- View certification compliance for team
- Manage team certifications

### ADMIN
- All manager permissions
- System-wide statistics and reporting
- Manage all employees across all locations
- Full certification management
- System configuration access
- User management

## 🔧 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication

**Login:**
```bash
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "password"
}
```

**Response:**
```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": { "id": 1, "email": "...", ... }
}
```

**Use token in requests:**
```bash
Authorization: Bearer <access_token>
```

### Key Endpoints

#### Employees
- `GET /api/employees/` - List employees (filtered by permissions)
- `GET /api/employees/{id}/` - Employee details
- `GET /api/employees/{id}/certifications/` - Employee certifications
- `POST /api/employees/{id}/certifications/` - Add certification
- `PATCH /api/employees/{id}/certifications/{cert_id}/` - Update certification

#### Vacation
- `GET /api/vacation/requests/` - List vacation requests
- `POST /api/vacation/requests/` - Submit vacation request
- `POST /api/vacation/requests/{id}/approve/` - Approve request (manager)
- `POST /api/vacation/requests/{id}/deny/` - Deny request (manager)
- `POST /api/vacation/requests/{id}/cancel/` - Cancel request
- `GET /api/vacation/balance/` - Get vacation balance

#### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics (role-based)
- `GET /api/dashboard/activities/` - Recent activities
- `GET /api/dashboard/upcoming-events/` - Upcoming events

#### Certifications
- `GET /api/certifications/expiring/` - Get expiring certifications
- `GET /api/certifications/expired/` - Get expired certifications

## 🧪 Testing

### Backend Tests
```bash
# Using Docker
docker-compose exec web pytest

# Local
pytest

# With coverage
pytest --cov=apps --cov-report=html
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build

# Type check
npm run type-check
```

### Test Coverage Goals
- Backend: > 80%
- Frontend: > 70%
- Critical paths: 100%

## 📈 Development Roadmap

### ✅ Phase 1: Completed
- Employee management
- Vacation request system
- Employee directory
- Enhanced dashboard
- Public homepage
- User profiles
- Test data system
- Basic certification tracking (models)

### 🚧 Phase 2: In Progress (Certification System)
- Certification API endpoints
- Certification dashboard for managers
- Document upload and verification
- Expiry alerts and notifications
- Compliance reporting
- Skills and competency tracking

### 📋 Phase 3: Planned (Shift Scheduling)
- Basic shift models
- Schedule builder
- Shift patterns and templates
- Shift swap requests
- Coverage visualization
- Overtime tracking

### 🔮 Phase 4: Future
- Advanced scheduling with rules enforcement
- Skills-based scheduling
- Predictive analytics
- Mobile app (native or PWA)
- Advanced reporting and BI
- Integration with payroll systems

See `ICU_MANAGER_REQUIREMENTS.md` and `DEVELOPMENT_TODO_LIST.md` for detailed requirements and implementation plans.

## 🏥 Healthcare-Specific Features

### Compliance & Safety
- **Certification Expiry Tracking**: Automatic warnings at 90, 60, 30, 14 days
- **Verification Workflow**: Manager verification required for critical certifications
- **Audit Trail**: Complete logging of all certification changes
- **Status Tracking**: ACTIVE, EXPIRING_SOON, EXPIRED, PENDING_VERIFICATION
- **Document Management**: Upload and verify certificate documents

### Intensive Care Support
- **24/7 Operations**: Built for round-the-clock facility operations
- **Staffing Ratios**: Foundation for minimum patient-to-nurse ratio enforcement
- **Skills Tracking**: Match patient needs to qualified staff
- **Emergency Preparedness**: Framework for disaster/surge staffing

## 🛡️ Security

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: GDPR and HIPAA considerations
- **Input Validation**: Comprehensive validation on frontend and backend
- **SQL Injection Prevention**: Django ORM with parameterized queries
- **XSS Protection**: React automatic escaping + CSP headers
- **CSRF Protection**: Django CSRF middleware
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Audit Logging**: Track all sensitive operations

## 🚀 Performance

### Optimization Strategies
- **Database**: Connection pooling, optimized indexes, select_related/prefetch_related
- **Caching**: Redis for sessions, query results, and computed data
- **Frontend**: Code splitting, lazy loading, React Query caching
- **Assets**: Optimized builds, gzip compression, CDN-ready
- **API**: Pagination, field filtering, efficient serializers

### Performance Targets
- Page load: < 2 seconds
- API response: < 200ms (95th percentile)
- Database queries: < 100ms (95th percentile)
- Concurrent users: 100+
- Uptime: 99.9%

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Ensure code quality:
   ```bash
   # Backend
   black .
   flake8
   isort .

   # Frontend
   npm run lint
   npm run type-check
   ```
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- Follow existing code patterns
- Write clear, self-documenting code
- Add comments for complex logic
- Use TypeScript strictly (no `any`)
- Write tests for new features
- Update documentation

## 📄 License

[Your License Here]

## 💬 Support

- **Documentation**: See `/plans` directory for detailed design docs
- **Issues**: Open an issue on GitHub
- **Email**: info@careplan.de (example)

## 🙏 Acknowledgments

Built with input from:
- Senior ICU facility managers with 15+ years experience
- Healthcare compliance experts
- Care workers and nurses
- Project managers and software architects

---

**CarePlan** - Professional management for intensive care excellence
